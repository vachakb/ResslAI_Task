from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn
import pathlib
import logging
import os

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="MCP Keyword Search Server")

# Allow CORS so browser-based inspectors can connect and OPTIONS preflight succeeds
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MCPRequest(BaseModel):
    tool: str
    args: Dict[str, Any] = {}


@app.post("/mcp")
async def mcp_endpoint(req: Request):

    body = await req.json()
    logging.info("Received /mcp request body: %s", body)

    
    if isinstance(body, dict) and "method" in body:
        method = body.get("method")
        jsonrpc = body.get("jsonrpc", "2.0")
        req_id = body.get("id")
        params = body.get("params", {})

       
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "mcp-keyword-search",
                    "version": "1.0.0"
                }
            }
            return {"jsonrpc": jsonrpc, "id": req_id, "result": result}

        
        elif method == "tools/list":
            result = {
                "tools": [
                    {
                        "name": "search_keyword",
                        "description": "Search for a keyword in a text file (case-insensitive)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "Path to the file to search"
                                },
                                "keyword": {
                                    "type": "string",
                                    "description": "Keyword to search for"
                                }
                            },
                            "required": ["file_path", "keyword"]
                        }
                    }
                ]
            }
            return {"jsonrpc": jsonrpc, "id": req_id, "result": result}

       
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name == "search_keyword":
                try:
                    search_result = search_keyword_tool(tool_args)
                    result = {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Found {search_result['count']} matches:\n" + 
                                       "\n".join([f"Line {m['line']}: {m['text']}" for m in search_result['matches']])
                            }
                        ]
                    }
                    return {"jsonrpc": jsonrpc, "id": req_id, "result": result}
                except HTTPException as e:
                    return {
                        "jsonrpc": jsonrpc,
                        "id": req_id,
                        "error": {
                            "code": e.status_code,
                            "message": str(e.detail)
                        }
                    }
            else:
                return {
                    "jsonrpc": jsonrpc,
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }

        
        else:
            return {
                "jsonrpc": jsonrpc,
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

   
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail={"error": "Invalid request body"})

   
    tool = body.get("tool")
    args = body.get("args") or body.get("params") or {}

    if not tool:
        raise HTTPException(status_code=400, detail={"error": "Missing 'tool' in request body"})

    if tool == "search_keyword":
        return search_keyword_tool(args)
    else:
        raise HTTPException(status_code=400, detail={"error": f"Unknown tool: {tool}"})


def search_keyword_tool(args: Dict[str, Any]):
    file_path = args.get("file_path")
    keyword = args.get("keyword")
    if not file_path or not keyword:
        raise HTTPException(status_code=400, detail={"error": "Missing 'file_path' or 'keyword' in args"})

    p = pathlib.Path(file_path)
    if not p.exists():
        raise HTTPException(status_code=400, detail={"error": f"File not found: {file_path}"})

    matches: List[Dict[str, Any]] = []
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, start=1):
                if keyword.lower() in line.lower():
                    matches.append({"line": i, "text": line.rstrip("\n")})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})

    return {"matches": matches, "count": len(matches)}


if __name__ == "__main__":
    
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8080"))
    
    logging.info(f"Starting MCP server on {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, log_level="info")
