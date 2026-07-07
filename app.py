import asyncio
import json
from openai.types.chat import ChatCompletionMessageParam
from fastmcp import FastMCP
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict


class UserClient:
    def __init__(self, script = "weatherServer.py", model = "deepseek-v4-pro"):
        self.model = model
        self.messages: List[ChatCompletionMessageParam] = []

        self.mcp_client = Client(script)
        self.openai_client = OpenAI(
            api_key="sk-b7624d639e9042a096def190185fc071",
            base_url="https://api.deepseek.com/v1",
        )
        self.messages = [
            {
                "role": "system",
                "content": "你是人工智能助手，你需要用工具来获取信息回答用户的问题.",
            }
        ]
        self.tools = []

    async def _ensure_client(self):
        if self.mcp_client is None:
            self.mcp_client = await Client(self.model).__aenter__()
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
        async with self.mcp_client:
            if not self.tools:
                self.tools = await self.prepare_tools()

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
        await self._ensure_client()
        while True:
            question = input("User: ")
            if question.lower() in ["exit", "quit"]:
                break
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
    await user_client.chat([{"role": "user", "content": "南昌今天的天气怎么样？"}])
    await user_client.loop()


if __name__ == "__main__":
    asyncio.run(main())