# Gmail MCP Server

A Model Context Protocol (MCP) server that provides Gmail integration for AI assistants.

## Features

- **Search emails** - Search Gmail using Gmail's native search syntax
- **Read emails** - Read the full content of specific emails
- **Send emails** - Compose and send emails
- **List labels** - View all Gmail labels/folders

## Prerequisites

- Python 3.10 or higher
- A Google Cloud project with the Gmail API enabled
- OAuth 2.0 credentials (Desktop application type)

## Setup

### 1. Google Cloud Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and enable it
4. Create OAuth 2.0 credentials:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application" as the application type
   - Download the credentials JSON file
5. Save the credentials file as `credentials.json` in the project root

### 2. Install Dependencies

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .
```

### 3. Authenticate

Run the server once to complete OAuth authentication:

```bash
python -m gmail_mcp.server
```

This will open a browser window for Google OAuth. After authenticating, a `token.json` file will be created.

## Configuration

### Environment Variables

- `GMAIL_CREDENTIALS_PATH` - Path to OAuth credentials file (default: `credentials.json`)
- `GMAIL_TOKEN_PATH` - Path to store OAuth token (default: `token.json`)

### VS Code / Copilot Integration

Add to your VS Code settings or `.vscode/mcp.json`:

```json
{
  "servers": {
    "gmail": {
      "command": "python",
      "args": ["-m", "gmail_mcp.server"],
      "cwd": "/path/to/gmail-mcp",
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/path/to/credentials.json",
        "GMAIL_TOKEN_PATH": "/path/to/token.json"
      }
    }
  }
}
```

## Available Tools

### gmail_search

Search for emails using Gmail's search syntax.

**Parameters:**
- `query` (required): Gmail search query (e.g., `from:example@gmail.com`, `subject:meeting`, `is:unread`)
- `max_results` (optional): Maximum number of results (default: 10)

### gmail_read

Read the full content of a specific email.

**Parameters:**
- `message_id` (required): The ID of the email message

### gmail_send

Send an email.

**Parameters:**
- `to` (required): Recipient email address
- `subject` (required): Email subject
- `body` (required): Email body content

### gmail_list_labels

List all labels in the Gmail account. No parameters required.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linter
ruff check src/

# Run tests
pytest
```

## License

MIT
