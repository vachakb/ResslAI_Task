# MCP Keyword Search Server

A minimal MCP (Model Context Protocol) server that implements a keyword search tool for text files. Built with FastAPI for the MCP Inspector.

## Features

- MCP Protocol compliant (JSON-RPC 2.0)
- Case-insensitive keyword search
- Returns matches with line numbers
- Configurable via environment variables
- 15 pytest tests included

## Requirements

- Python 3.8+

## Installation

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

**1. Start the server:**
```powershell
python server.py
```
Server runs on `http://127.0.0.1:8080`

**2. Use MCP Inspector:**
```powershell
npx @modelcontextprotocol/inspector python server.py
```
- Opens browser with Inspector UI
- Click **Tools** tab → `search_keyword`
- Enter: `file_path: sample.txt`, `keyword: Salesforce`
- Click **Run Tool**

## Testing

```powershell
# Run all tests (15 total)
pytest -v

# Run specific test suite
pytest test_server.py -v
pytest tests/test_search.py -v
```

## Configuration

Set via environment variables (see `.env.example`):
```powershell
$env:MCP_HOST="127.0.0.1"  # Default
$env:MCP_PORT="8080"        # Default
```

## Project Structure

```
ResslAI_Task/
├── server.py           # MCP server (FastAPI)
├── search_tool.py      # Search module with regex support
├── test_server.py      # MCP server tests (12 tests)
├── tests/
│   └── test_search.py  # Search tool tests (3 tests)
├── sample.txt          # Test file
└── requirements.txt    # Dependencies
```

## MCP Tool: search_keyword

**Parameters:**
- `file_path` (string): Path to file
- `keyword` (string): Keyword to search

**Returns:** Matches with line numbers

**Example:**
```json
{
  "file_path": "sample.txt",
  "keyword": "Salesforce"
}
```

## Notes

- Default `127.0.0.1` accepts local connections only
- CORS enabled for browser-based tools

