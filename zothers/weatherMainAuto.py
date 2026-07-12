import asyncio
import json
from openai.types.chat import ChatCompletionMessageParam
from fastmcp import FastMCP
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict


class UserClient:
    def __init__(self, scripts: List[str] = [], model = "deepseek-v4-pro"):
        if scripts is None:
            scripts = []
        self.model = model
        self.messages: List[ChatCompletionMessageParam] = []

        self.openai_client = OpenAI(
            api_key="sk-6f49e0374f834f079f0c56ddf105db7b",
            base_url="https://api.deepseek.com/v1",
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
        self.mcp_clients: List[Client] = []
        for script in scripts:
            self.mcp_clients.append(Client(script))
            print(f"✅ 已连接 {script}")
            
        self.tools = []

    async def _ensure_clients(self):
        """确保所有 MCP Client 都已连接"""
        for idx, client in enumerate(self.mcp_clients):
            try:
                await client.__aenter__()
                print(f"✅ client {idx} 已进入上下文")
            except Exception as e:
                print(f"⚠️ client {idx} 进入上下文失败: {e}")

    async def prepare_tools(self):
        """准备所有工具"""
        # ✅ 确保所有 client 都已连接
        await self._ensure_clients()
        
        all_tools = []
        for c in self.mcp_clients:
            tools = await c.list_tools()
            for tool in tools:
                all_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    }
                })
        print(f"📋 共加载 {len(all_tools)} 个工具")
        return all_tools

    async def _collect_tools(self):
        """从所有 MCP Client 收集工具（已被 prepare_tools 替代）"""
        self.tools = await self.prepare_tools()

    async def chat(self, messages: List[Dict]):
        # ✅ 确保所有 client 都已连接
        await self._ensure_clients()
        
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
                tool_name = tool_call.function.name # type: ignore
                args = json.loads(tool_call.function.arguments) # type: ignore
                print(f"🔧 调用工具: {tool_name}, 参数: {args}") # type: ignore
                
                # ✅ 查找对应的 client 执行工具
                tool_result = await self._execute_tool(tool_name, args)
                print(f"📦 工具结果: {tool_result}")

                # 把工具结果加回对话
                messages.append({  # type: ignore
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                })

            # ④ 循环继续，让 LLM 用工具结果生成最终回答

    async def _execute_tool(self, tool_name: str, arguments: Dict):
        """在所有 client 中查找并执行工具"""
        for client in self.mcp_clients:
            try:
                # 检查这个 client 是否有该工具
                tools = await client.list_tools()
                if any(t.name == tool_name for t in tools):
                    result = await client.call_tool(tool_name, arguments)
                    return result
            except Exception as e:
                print(f"⚠️ 执行工具 {tool_name} 失败: {e}")
        
        return {"error": f"未找到工具: {tool_name}"}

    async def loop(self):
        print("🤖 AI 助手已启动，输入 'exit' 或 'quit' 退出\n")
        while True:
            question = input("😊User: ")
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
    user_client = UserClient(
        scripts=[
            "weatherServer.py",      # 天气服务
            "weatherServer2.py",     # 磁盘信息服务
        ],
        model="deepseek-chat"
    )
    
    # ✅ 初始化：收集所有工具
    await user_client._collect_tools()
    
    print(f"📋 总工具数: {len(user_client.tools)}")
    await user_client.chat([{"role": "user", "content": "南昌今天的天气怎么样？"}])
    await user_client.loop()


if __name__ == "__main__":
    asyncio.run(main())