"""测试 fastmcp.Client 的初始化"""
import asyncio
from fastmcp import Client

async def test():
    c = Client("mcppackages/mcp_diskInfoServer.py")
    print("Client created")
    
    # 尝试 initialize
    await c.initialize()
    print("Connected:", c.is_connected())
    
    # 获取工具
    tools = await c.list_tools()
    print(f"Tools: {len(tools)}")
    for t in tools:
        print(f"  - {t.name}: {t.description[:60]}")
    
    # 调用工具
    result = await c.call_tool("get_disk_info", {})
    print(f"Result type: {type(result)}")
    
    await c.close()
    print("Closed")

asyncio.run(test())