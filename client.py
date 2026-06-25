# from fastmcp import Client
# import asyncio


# async def run():
#     client = Client("server.py")
#     async with client:
#         tools = await client.list_tools()
#         for tool in tools:
#             print("\nCurrent tool:", tool)
#         tool = tools[0]
#         result = await client.call_tool(tool.name, {"state": "CA"})
#         print(result)

# if __name__ == "__main__":
#     asyncio.run(run())

from fastmcp import Client
import asyncio


async def run():
    client = Client("server.py")
    async with client:
        tools = await client.list_tools()
        print(f"✅ 已连接到 Server，可用工具: {[tool.name for tool in tools]}")
        
        while True:
            try:
                question = input("\nUser (输入 'exit' 退出): ")
                if question.lower() in ["exit", "quit"]:
                    print("👋 再见！")
                    break
                
                # 简单的工具调用逻辑（假设用户输入的是 state）
                if question:
                    result = await client.call_tool("get_weather", {"state": question})
                    print(f"AI: {result}")
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

if __name__ == "__main__":
    asyncio.run(run())