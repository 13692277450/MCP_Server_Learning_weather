import asyncio
import json
import time
from openai.types.chat import ChatCompletionMessageParam
from fastmcp import FastMCP
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict


class UserClient:
    def __init__(self, script = "weatherServer.py", model = "qwen-plus"): #deepseek-v4-pro
        self.model = model
        self.messages: List[ChatCompletionMessageParam] = []
        self.mcp_client = Client(script)
        self.openai_client = OpenAI(
            # api_key="sk-6f49e0374f834f079f0c56ddf105db7b",
            # base_url="https://api.deepseek.com/v1",
            api_key="sk-ws-H.EDXLHDR.EYhV.MEUCIQCb3cdzaAeDb1BYWbmyPGdlitfGooLM41ArNV_6WeybiwIgdpAbBv7de29CLygBmcyLyRxSoVeE3-l4iczA2aQrD-M",
            base_url="https://ws-2fqrt6fseml9k9m9.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
            #host: ws-2fqrt6fseml9k9m9.cn-beijing.maas.aliyuncs.com
            #dahscope: https://ws-2fqrt6fseml9k9m9.cn-beijing.maas.aliyuncs.com/api/v1
            #openai : https://ws-2fqrt6fseml9k9m9.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
            
        )
        self.messages = [
            {
                "role": "system",
                "content": """你是人工智能助手，你可以使用工具来获取信息。
                                重要规则：
                                1. 当用户询问天气时，必须使用 get_weather 工具，
                                2. 当用户询问股票时，必须使用 get_stock 工具，
                                3. 当用户询问磁盘信息时，使用 get_diskinfo 工具
                                4. 工具调用后，根据返回的结果回答用户
                                5. 如果用户没有提供城市名，友好地询问用户城市
                                """,
            }
        ]
        self.tools = []
        self.refreshInterval = False

    async def _ensure_client(self): # 确保客户端已连接
        if self.mcp_client is None:# or self.refreshInterval == True:
            # print("刷新MCP服务器")
            # if self.mcp_client:
            #     self.mcp_client = await Client(self.model).init() # type: ignore
            self.mcp_client = await Client(self.model).__aenter__()
            self.refreshInterval = False
        return self.mcp_client

    async def prepare_tools(self):
        tools = await self.mcp_client.list_tools()
        tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,  # ⭐ 用 parameters，不是 input_schema
            },
        } for tool in tools]
        return tools
  
    async def chat(self, messages: List[Dict]):
       

            # ⭐ 循环：只要 LLM 说要调用工具，就继续对话
            while True:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages,  # type: ignore
                    tools=self.tools,  # type: ignore
                )
                message = response.choices[0].message
                # ① 如果不需要调用工具，直接返回回答
                if response.choices[0].finish_reason != "tool_calls" or not message.tool_calls:
                    return message

                # ② 把 LLM 的 tool_calls 消息加入对话历史
                tool_calls_message = {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name, # type: ignore
                                "arguments": tc.function.arguments, # type: ignore
                            },
                        }
                        for tc in message.tool_calls
                    ]
                }
                messages.append(tool_calls_message)  # type: ignore

                # ③ 逐个调用工具，把结果加回对话
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments) # type: ignore
                    print(f"🔧 调用工具: {tool_call.function.name}, 参数: {args}") # type: ignore
                    tool_result = await self.mcp_client.call_tool(
                        tool_call.function.name, args # type: ignore
                    )
                    print(f"📦 工具结果: {tool_result}")

                    # 把工具结果加回对话
                    messages.append({  # type: ignore
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    })

                # ④ 循环继续，让 LLM 用工具结果生成最终回答

    async def loop(self):
        print("🤖 AI 助手已启动，输入 'exit' 或 'quit' 退出\n")
        while True:
            async with self.mcp_client:
                await self._ensure_client()
                if not self.tools:
                    self.tools = await self.prepare_tools()
                    self.refreshInterval = True
            print(f"当前工具数量------: {len(self.tools)}") # type: ignore
            time.sleep(10) # type: ignore
            while True:
                question = input("User: ")
                if question.lower() in ["exit", "quit"]:
                    break
                if question.lower() in ["mcptools", "tools"]:
                
                    print(f"刷新后的工具列表数量: {len(self.tools)}")
                    time.sleep(2) # type: ignore
                    
                if not question.strip():
                    continue
                self.messages.append({"role": "user", "content": question})  # type: ignore
                response_message = await self.chat(self.messages)  # type: ignore
                content = response_message.content if hasattr(response_message, "content") else str(response_message)
                print("AI:", content)
                self.messages.append({  # type: ignore
                    "role": "assistant",
                    "content": content,
                })


async def main():
    user_client = UserClient()
    await user_client.chat([{"role": "user", "content": "你有哪些工具？"}])
    await user_client.loop()


if __name__ == "__main__":
    asyncio.run(main())