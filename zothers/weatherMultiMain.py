import asyncio
import json
from typing import List, Dict, Any
from openai import OpenAI
from fastmcp import Client  # 假设是自定义的 MCP 客户端
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionMessageToolCall,
)
class UserClient:
    def __init__(self, scripts: List[str] = [], model: str = "deepseek-chat"):
        """
        Args:
            scripts: MCP Server 脚本路径列表
            model: 使用的模型
        """
        self.model = model
        self.messages:  list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": "你是人工智能助手，你需要用工具来获取信息回答用户的问题。"
            }
        ]
        
        # ✅ 为每个 MCP Server 创建一个 Client
        self.mcp_clients: List[Client] = []
        if scripts:
            for script in scripts:
                try:
                    client = Client(script)
                    self.mcp_clients.append(client)
                    print(f"✅ 已连接: {script}")
                except Exception as e:
                    print(f"❌ 连接失败 {script}: {e}")
        
        # OpenAI 客户端
        self.openai_client = OpenAI(
            api_key="sk-6f49e0374f834f079f0c56ddf105db7b",
            base_url="https://api.deepseek.com/v1",
        )
        
        # 合并所有工具
        self.tools = []
        self._collect_tools()
    
    def _collect_tools(self):
        """从所有 MCP Client 收集工具"""
        self.tools = []
        for client in self.mcp_clients:
            try:
                tools = asyncio.run(client.list_tools())
                for tool in tools:
                    self.tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        }
                    })
                print(f"📋 从 {client} 获取 {len(tools)} 个工具")
            except Exception as e:
                print(f"⚠️ 获取工具失败: {e}")
    
    def chat(self, user_message: str) -> str:
        """处理用户消息"""
        self.messages.append({"role": "user", "content": user_message})
        
        # 第一次调用：AI 决定是否使用工具
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tools if self.tools else [],
            tool_choice="auto" if self.tools else "none",
        )
        
        message = response.choices[0].message
        
        # 处理工具调用
        if message.tool_calls:
            self.messages.append(message.model_dump()) # type: ignore
            
            for tool_call in message.tool_calls:
                assert isinstance(tool_call, ChatCompletionMessageToolCall), "Unexpected tool_call type"

                tool_name = tool_call.function.name 
                arguments = json.loads(tool_call.function.arguments)
                
                # 找到对应的 Client 执行工具
                result = self._execute_tool(tool_name, arguments)
                
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })
            
            # 生成最终回复
            final_response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=self.messages,
            )
            final_message = final_response.choices[0].message
            self.messages.append(final_message.model_dump()) # type: ignore
            return final_message.content or ""
        
        # 无工具调用
        self.messages.append(message.model_dump()) # type: ignore
        return message.content or ""
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """在多个 Client 中查找并执行工具"""
        for client in self.mcp_clients:
            try:
                # 检查这个 Client 是否有该工具
                tools = asyncio.run(client.list_tools())
                if any(t.name == tool_name for t in tools):
                    result = asyncio.run(client.call_tool(tool_name, arguments))
                    return result # type: ignore
            except Exception as e:
                print(f"⚠️ 执行工具 {tool_name} 失败: {e}")
        
        return {"error": f"未找到工具: {tool_name}"}


# ============ 使用示例 ============
if __name__ == "__main__":
    # 初始化多个 MCP Server
    user = UserClient(
        scripts=[
            "weatherServer.py",      # 天气服务
            "../mcppackages/mcp_diskInfoServer.py",     # 磁盘信息服务
        ],
        model="deepseek-chat"
    )
    
    print(f"📋 总工具数: {len(user.tools)}")
    
    # 测试对话
    response = user.chat("今天天气怎么样？")
    print(f"🤖 {response}")