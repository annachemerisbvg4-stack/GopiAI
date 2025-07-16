@echo off
echo Starting Serena MCP Server with Enhanced Sequential Thinking...
cd /d C:\Users\crazy\mcp_servers\serena
uv run serena-mcp-server --project C:\Users\crazy\GOPI_AI_MODULES --context agent --mode planning,editing --transport sse --port 8001 --enable-web-dashboard true
pause
