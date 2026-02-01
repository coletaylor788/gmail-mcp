# Gmail MCP Server - Copilot Instructions

This is a Python-based Model Context Protocol (MCP) server for Gmail integration.

## Project Structure

- `src/gmail_mcp/` - Main source code
  - `server.py` - MCP server implementation with Gmail tools
  - `__init__.py` - Package initialization
- `pyproject.toml` - Project configuration and dependencies

## Key Technologies

- **MCP SDK**: `mcp` package for Model Context Protocol server implementation
- **Google APIs**: `google-api-python-client` for Gmail API access
- **OAuth**: `google-auth-oauthlib` for authentication

## Development Guidelines

1. **Async First**: All tool handlers should be async functions
2. **Error Handling**: Wrap Gmail API calls in try/except to provide helpful error messages
3. **Type Hints**: Use Python type hints throughout the codebase
4. **Scopes**: Be mindful of Gmail API scopes - request only what's needed

## Adding New Tools

To add a new Gmail tool:

1. Add the tool definition in `list_tools()` with proper schema
2. Add a handler case in `call_tool()`
3. Implement the helper function (e.g., `_new_tool()`)

## Testing

Run tests with `pytest`. Use mocking for Gmail API calls to avoid requiring credentials in tests.
