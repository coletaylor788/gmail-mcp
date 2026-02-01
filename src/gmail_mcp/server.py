"""Gmail MCP Server implementation."""

import asyncio
import base64
import os
from email.mime.text import MIMEText
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

# Initialize MCP server
server = Server("gmail-mcp")


def get_gmail_service():
    """Get authenticated Gmail API service."""
    creds = None
    token_path = os.environ.get("GMAIL_TOKEN_PATH", "token.json")
    credentials_path = os.environ.get("GMAIL_CREDENTIALS_PATH", "credentials.json")

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    "Please download it from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Gmail tools."""
    return [
        Tool(
            name="gmail_search",
            description="Search for emails in Gmail using Gmail's search syntax",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (e.g., 'from:example@gmail.com', 'subject:meeting', 'is:unread')",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="gmail_read",
            description="Read the full content of a specific email by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The ID of the email message to read",
                    },
                },
                "required": ["message_id"],
            },
        ),
        Tool(
            name="gmail_send",
            description="Send an email through Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body content",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        ),
        Tool(
            name="gmail_list_labels",
            description="List all labels in the Gmail account",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    service = get_gmail_service()

    if name == "gmail_search":
        return await _search_emails(service, arguments)
    elif name == "gmail_read":
        return await _read_email(service, arguments)
    elif name == "gmail_send":
        return await _send_email(service, arguments)
    elif name == "gmail_list_labels":
        return await _list_labels(service)
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _search_emails(service, arguments: dict[str, Any]) -> list[TextContent]:
    """Search emails using Gmail API."""
    query = arguments["query"]
    max_results = arguments.get("max_results", 10)

    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )

    messages = results.get("messages", [])
    if not messages:
        return [TextContent(type="text", text="No messages found.")]

    output = []
    for msg in messages:
        msg_data = (
            service.users().messages().get(userId="me", id=msg["id"], format="metadata").execute()
        )
        headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
        output.append(
            f"ID: {msg['id']}\n"
            f"From: {headers.get('From', 'Unknown')}\n"
            f"Subject: {headers.get('Subject', 'No Subject')}\n"
            f"Date: {headers.get('Date', 'Unknown')}\n"
            f"---"
        )

    return [TextContent(type="text", text="\n".join(output))]


async def _read_email(service, arguments: dict[str, Any]) -> list[TextContent]:
    """Read a specific email."""
    message_id = arguments["message_id"]

    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()

    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

    # Extract body
    body = ""
    if "parts" in msg["payload"]:
        for part in msg["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                break
    elif "body" in msg["payload"] and "data" in msg["payload"]["body"]:
        body = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode("utf-8")

    output = (
        f"From: {headers.get('From', 'Unknown')}\n"
        f"To: {headers.get('To', 'Unknown')}\n"
        f"Subject: {headers.get('Subject', 'No Subject')}\n"
        f"Date: {headers.get('Date', 'Unknown')}\n"
        f"\n{body}"
    )

    return [TextContent(type="text", text=output)]


async def _send_email(service, arguments: dict[str, Any]) -> list[TextContent]:
    """Send an email."""
    message = MIMEText(arguments["body"])
    message["to"] = arguments["to"]
    message["subject"] = arguments["subject"]

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    sent_message = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    return [TextContent(type="text", text=f"Email sent successfully. Message ID: {sent_message['id']}")]


async def _list_labels(service) -> list[TextContent]:
    """List all Gmail labels."""
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
        return [TextContent(type="text", text="No labels found.")]

    output = ["Gmail Labels:", "---"]
    for label in labels:
        output.append(f"- {label['name']} (ID: {label['id']})")

    return [TextContent(type="text", text="\n".join(output))]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
