# tool_manager.py
import asyncio
from asyncio import tools
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionMessageToolCall,
)
from fastmcp import Client


class MCPToolManager:
    """
    管理多个 MCP Server 的工具
    """
    
    def __init__(self):
        self.model = "deepseek-chat"
        self.clients: Dict[str, Client] = {}  # name -> Client
        self.tools: List[Dict] = []
        self.tool_to_client: Dict[str, str] = {}  # tool_name -> client_name
    
    async def add_server(self, name: str, script_path: str):
        """添加 MCP Server (异步)"""
        try:
            client = Client(script_path)
            # 必须保持在 async with 块内，所以提前打开连接
            await client.__aenter__()
            # async with client:
            self.clients[name] = client
            
            # 获取工具
            tools = await client.list_tools()
            for tool in tools:
                self.tools.append({
                    "type": "function",
                    "function": {
                        "name": f"{name}_{tool.name}",  # 添加前缀避免冲突
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    }
                })
                self.tool_to_client[f"{name}_{tool.name}"] = name
            
            print(f"✅ 添加 Server: {name} ({len(tools)} 个工具)")
            
        except Exception as e:
            print(f"❌ 添加 Server 失败 {name}: {e}")
    
    def remove_server(self, name: str):
        """移除 MCP Server"""
        if name in self.clients:
            prefix = f"{name}_"
            self.tools = [t for t in self.tools if not t["function"]["name"].startswith(prefix)]
            self.tool_to_client = {k: v for k, v in self.tool_to_client.items() if v != name}
            del self.clients[name]
            print(f"🗑️ 移除 Server: {name}")
    
    def get_tools(self) -> List[Dict]:
        """获取所有工具"""
        return self.tools
    
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """执行工具 (异步)"""
        parts = tool_name.split("_", 1)
        if len(parts) != 2:
            return {"error": f"无效的工具名: {tool_name}"}
        
        client_name, actual_tool = parts
        
        if client_name not in self.clients:
            return {"error": f"未找到 Server: {client_name}"}
        
        try:
            client = self.clients[client_name]
            result = await client.call_tool(actual_tool, arguments)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def close_all(self):
        """关闭所有客户端"""
        for name, client in self.clients.items():
            try:
                await client.__aexit__(None, None, None)
            except:
                pass
        self.clients.clear()
        self.tools.clear()
        self.tool_to_client.clear()


class UserClient:
    def __init__(self, model: str = "deepseek-chat" ):
        self.model = model
        self.tool_manager = MCPToolManager()
        self.messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "你是人工智能助手，你可以使用工具来获取信息。"
            }
        ]
        
        self.openai_client: OpenAI = OpenAI(
            api_key="sk-6f49e0374f834f079f0c56ddf105db7b",
            base_url="https://api.deepseek.com/v1",
        )
    
    def add_server(self, name: str, script_path: str):
        """添加 MCP Server（同步包装）"""
        asyncio.run(self.tool_manager.add_server(name, script_path))
    
    def remove_server(self, name: str):
        """移除 MCP Server"""
        self.tool_manager.remove_server(name)
    async def _ensure_client(self):
        if self.client is None:
            self.client = await Client(self.model).__aenter__()
        return self.client

    async def prepare_tools(self):
        tools = await self.client.list_tools()
        tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,  # ⭐ 用 parameters，不是 input_schema
            },
        } for tool in tools]
        return tools
    
    def chat(self, user_message: str) -> str:
        """处理用户消息"""
        # asyncio.run(self._ensure_client())
        # asyncio.run(self.prepare_tools())
        while True:
            question = input("User: ")
            if question.lower() in ["exit", "quit"]:
                break
            if not question.strip():
                continue
            self.messages.append({"role": "user", "content": question})  # type: ignore[arg-type]
            
            tools: list[ChatCompletionToolParam] = self.tool_manager.get_tools()  # type: ignore[assignment]
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice="auto" if tools else "none",
            )
            message = response.choices[0].message

            # ① 如果不需要调用工具，直接返回回答
            if response.choices[0].finish_reason != "tool_calls" or not message.tool_calls:
                return message.content or ""
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
            self.messages.append(tool_calls_message)  # type: ignore

            # ③ 逐个调用工具，把结果加回对话
            for tool_call in message.tool_calls:
                args = json.loads(tool_call.function.arguments) # type: ignore
                print(f"🔧 调用工具: {tool_call.function.name}, 参数: {args}") # type: ignore
                tool_result = asyncio.run(self.tool_manager.execute_tool(  # type: ignore
                    tool_call.function.name, args # type: ignore
                )
                print(f"📦 工具结果: {tool_result}")

                # 把工具结果加回对话
                self.messages.append({  # type: ignore
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result),
                })

            # ④ 循环继续，让 LLM 用工具结果生成最终回答
            # if message.tool_calls:
            #     self.messages.append(message.model_dump())  # type: ignore[arg-type]
                
            #     for tool_call in message.tool_calls:
            #         assert isinstance(tool_call, ChatCompletionMessageToolCall), "Unexpected tool_call type"
            #         tool_name = tool_call.function.name
            #         arguments = json.loads(tool_call.function.arguments)
                    
            #         result = asyncio.run(self.tool_manager.execute_tool(tool_name, arguments))
                    
            #         self.messages.append({
            #             "role": "tool",
            #             "tool_call_id": tool_call.id,
            #             "content": json.dumps(result, ensure_ascii=False)
            #         })
                
            #     final_response = self.openai_client.chat.completions.create(
            #         model=self.model,
            #         messages=self.messages,
            #     )
            #     final_message = final_response.choices[0].message
            #     self.messages.append(final_message.model_dump())  # type: ignore[arg-type]
            #     return final_message.content or ""
            
            # self.messages.append(message.model_dump())  # type: ignore[arg-type]
            # return message.content or ""
        return ""
    
    def close(self):
        """关闭所有 MCP 连接"""
        asyncio.run(self.tool_manager.close_all())


# ============ 使用示例 ============
if __name__ == "__main__":
    user = UserClient()
    try:
        # 动态添加多个 Server
        user.add_server("weather", "zothers/weatherServer.py")
        # user.add_server("disk", "mcppackages/mcp_diskInfoServer.py")
        
        print(f"📋 总工具数: {len(user.tool_manager.get_tools())}")
        for tool in user.tool_manager.get_tools():
            print(tool)
        
        # 测试
        response = user.chat("我的磁盘有多大？")
        print(f"🤖 {response}")
        
        response = user.chat("今天天气怎么样？")
        print(f"🤖 {response}")
        chat = user.chat("")
        print(f"🤖 {chat}")
    finally:
        user.close()