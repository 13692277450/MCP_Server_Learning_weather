import os

def list_mcp_tools() -> list[str]:
    """
    列出所有MCP工具的文件名
    Returns:
    List of tool names.
    """
    mcps = []
    for file in os.listdir("mcp"):
        if file.endswith(".py"):
            mcps.append(file) #[:-3])
    return mcps
    