from fastmcp import FastMCP
from tesing.agent import process_query

mcp = FastMCP("NER-RAG-Server")

@mcp.tool()
def run_agent_tool(query: str) -> str:
    """Викликає NER та RAG агента для аналізу тексту."""
    return process_query(query)

if __name__ == "__main__":
    mcp.run()