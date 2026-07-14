import asyncio
import json
import os
from openai.types.chat import ChatCompletionMessageParam
from fastmcp import FastMCP
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict, Optional


class UserClient:
    def __init__(self, script="weatherServer.py", model="deepseek-v4-pro"):
        self.model = model
        self.script = script
        self.messages: List[ChatCompletionMessageParam] = []
        self.mcp_client: Optional[Client] = None  # 初始为 None
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
        self.tools = []
        self.refreshInterval = False
        
        # === 文件监听相关 ===
        self._last_mtime = os.path.getmtime(script)
        self._running = True
        self._reconnecting = False  # 防止重连冲突

    async def connect(self):
        """建立连接"""
        if self.mcp_client:
            await self.disconnect()
        self.mcp_client = Client(self.script)
        await self.mcp_client.__aenter__()
        self.tools = await self.prepare_tools()
        print(f"✅ 已连接，工具数量: {len(self.tools)}")

    async def disconnect(self):
        """断开连接"""
        if self.mcp_client:
            try:
                await self.mcp_client.__aexit__(None, None, None)
            except Exception:
                pass
            self.mcp_client = None

    async def _ensure_client(self):
        """确保客户端已连接"""
        if self.mcp_client is None:
            await self.connect()
        return self.mcp_client

    async def prepare_tools(self):
        """从 MCP Server 获取工具列表"""
        if self.mcp_client is None:
            return []
        try:
            tools = await self.mcp_client.list_tools()
            return [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            } for tool in tools]
        except Exception as e:
            print(f"⚠️ 获取工具失败: {e}")
            return self.tools  # 返回缓存

    async def _watch_file_changes(self):
        """后台监听文件变化，自动重连并刷新工具"""
        while self._running:
            await asyncio.sleep(3)
            try:
                current_mtime = os.path.getmtime(self.script)
                if current_mtime > self._last_mtime and not self._reconnecting:
                    self._reconnecting = True
                    self._last_mtime = current_mtime
                    print("\n🔔 检测到 Server 文件变化，正在重连...")
                    await self.connect()  # 自动断开旧 + 连接新
                    print(f"✅ 已刷新，当前工具: {len(self.tools)} 个")
                    self._reconnecting = False
            except Exception as e:
                print(f"⚠️ 文件监听异常: {e}")
                self._reconnecting = False


async def chat(user_client: UserClient, messages: List[Dict], tools: List[Dict]):
    """循环：只要 LLM 说要调用工具，就继续对话"""
    while True:
        response = user_client.openai_client.chat.completions.create(
            model=user_client.model,
            messages=user_client.messages,
            tools=user_client.tools,
        )
        message = response.choices[0].message
        
        if response.choices[0].finish_reason != "tool_calls" or not message.tool_calls:
            return message

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
        messages.append(tool_calls_message)

        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments) # type: ignore
            print(f"🔧 调用工具: {tool_call.function.name}, 参数: {args}") # type: ignore
            
            # 确保连接可用
            await user_client._ensure_client()
            tool_result = await user_client.mcp_client.call_tool( # type: ignore
                tool_call.function.name, args # type: ignore
            )
            print(f"📦 工具结果: {tool_result}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result),
            })


async def loop(user_client: UserClient):
    print("🤖 AI 助手已启动，输入 'exit' 或 'quit' 退出\n")
    
    # ❶ 建立连接
    await user_client.connect()
    print(f"📋 当前工具数量: {len(user_client.tools)}")
    for t in user_client.tools:
        print(f"   - {t['function']['name']}")
    
    # ❷ 启动后台文件监听
    asyncio.create_task(user_client._watch_file_changes())
    
    try:
        while True:
            question = input("User: ")
            if question.lower() in ["exit", "quit"]:
                break
                
            if question.lower() in ["mcptools", "tools"]:
                await user_client.connect()  # 重连刷新
                print(f"🔄 刷新后的工具列表数量: {len(user_client.tools)}")
                continue
                
            if not question.strip():
                continue
                
            user_client.messages.append({"role": "user", "content": question})
            response_message = await chat(user_client, user_client.messages, user_client.tools) # type: ignore
            content = response_message.content if hasattr(response_message, "content") else str(response_message)
            print("AI:", content)
            user_client.messages.append({
                "role": "assistant",
                "content": content,
            })
    finally:
        user_client._running = False
        await user_client.disconnect()


async def main():
    user_client = UserClient()
    await loop(user_client)


if __name__ == "__main__":
    asyncio.run(main())
