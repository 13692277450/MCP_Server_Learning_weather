import ast
import asyncio
import json
import os
from openai.types.chat import ChatCompletionMessageParam
from fastmcp import FastMCP
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict


class UserClient:
    def __init__(self, scripts=[
            "weatherServer.py",      # 天气服务
            "weatherServer2.py",
            "weatherMCPSearch.py",
        ], model="deepseek-v4-pro"):
        self.model = model
        self.valid_scripts = []

        # for script in scripts:
        #     is_valid, msg = self.is_valid_mcp_script_strict(script)
        #     if not is_valid:
        #         print(f"⚠️ {script} 无效: {msg}")
        #         continue
        #     self.valid_scripts.append(script)
        # self.scripts =  self.valid_scripts
        self.scripts = scripts
        self.messages: List[ChatCompletionMessageParam] = []
        self.mcp_clients: List[Client] = []
        self.openai_client = OpenAI(
            api_key="sk-6f49e0374f834f079f0c56ddf105db7b",
            base_url="https://api.deepseek.com/v1",
        )       # 2. 当用户询问股票时，必须使用工具，
                                # 3. 当用户询问磁盘信息时，使用工具
                                # 4. 工具调用后，根据返回的结果回答用户
                                # 5. 如果用户没有提供城市名，友好地询问用户城市
        self.messages = [
            {
                "role": "system",
                "content": """你是人工智能助手，你可以使用工具来获取信息。
                                重要规则：
                                1. 当用户询问任何问题时，可以使用工具，
                                """,
            }
        ]
        self.tools = []
        self.refreshInterval = False
        # === 文件监听相关 ===
        self._last_mtime = {}
        for s in self.scripts:
            if os.path.exists(s):
                self._last_mtime[s] = os.path.getmtime(s)
            else:
                self._last_mtime[s] = 0
                print(f"Warning: {s} does not exist, skip it.")
        self._running = True
        self._reconnecting = False

    # 更严格的版本：用 AST 解析真正检查语法
    def is_valid_mcp_script_strict(self, filepath: str) -> tuple[bool, str]:
        """用 AST 解析，真正校验语法和结构"""
        if not os.path.exists(filepath):
            return False, "文件不存在"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=filepath)
        except SyntaxError as e:
            return False, f"Python 语法错误: {e}"
        
        has_fastmcp_import = False
        has_mcp_instance = False
        has_tool_decorator = False
        has_run_call = False
        
        for node in ast.walk(tree):
            # 检查导入
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if 'fastmcp' in alias.name.lower():
                        has_fastmcp_import = True
            
            # 检查 FastMCP 调用（创建实例）
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'FastMCP':
                    has_mcp_instance = True
                # 检查 .run() 调用
                if isinstance(node.func, ast.Attribute) and node.func.attr == 'run':
                    has_run_call = True
            
            # 检查 @mcp.tool() 装饰器
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr == 'tool':
                                has_tool_decorator = True
        
        # 判断标准
        if not has_fastmcp_import:
            return False, "没有导入 FastMCP"
        if not has_mcp_instance:
            return False, "没有创建 FastMCP 实例"
        if not has_run_call and not has_tool_decorator:
            return False, "既没有 mcp.run() 也没有 @mcp.tool()，可能不是 MCP Server"
        
        return True, "合规的 MCP Server 文件"


    async def connect(self):
        """建立连接（连接所有 Server）"""
        if self.mcp_clients:
            await self.disconnect()
        
        # 筛选出存在的文件
        self.valid_scripts = []
        for script in self.scripts:
            if os.path.exists(script):
                self.valid_scripts.append(script)
            else:
                print(f"⚠️ 文件不存在，跳过: {script}")
        
        if not self.valid_scripts:
            print("❌ 没有可用的 Server 脚本")
            self.tools = []
            return
        
        # 为每个有效文件创建 client
        for script in self.valid_scripts:
            client = Client(script)
            self.mcp_clients.append(client)
        
        # 启动所有 client
        for client in self.mcp_clients:
            await client.__aenter__()
        
        # 获取所有工具
        self.tools = await self.prepare_tools()
        print(f"🚒总共MCP服务器数: {len(self.scripts)}")
        print(f"✅ 已连接，工具数量: {len(self.tools)}")
        

    async def disconnect(self):
        """断开所有连接"""
        if self.mcp_clients:
            for client in self.mcp_clients:
                try:
                    await client.__aexit__(None, None, None)
                except Exception:
                    pass
            self.mcp_clients = []
            
    async def _ensure_client(self):
        """确保客户端已连接"""
        if not self.mcp_clients:
            await self.connect()
        return self.mcp_clients

    async def prepare_tools(self):
        """从所有 MCP Server 获取工具列表（合并）"""
        if not self.mcp_clients:
            return []
        try:
            all_tools = []
            for client in self.mcp_clients:  # ✅ 遍历所有 client
                tools = await client.list_tools()
                for tool in tools:
                    all_tools.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    })
            return all_tools
        except Exception as e:
            print(f"⚠️ 获取工具失败: {e}")
            return self.tools

    async def _find_client_by_tool(self, tool_name: str):
        """根据工具名找到对应的 client"""
        for client in self.mcp_clients:
            try:
                tools = await client.list_tools()
                for t in tools:
                    if t.name == tool_name:
                        return client
            except Exception:
                continue
        return None

    async def _watch_file_changes(self):
        """后台监听文件变化，自动重连并刷新工具"""
        while self._running:
            await asyncio.sleep(3)
            try:
                if self.valid_scripts:
                    for script in self.scripts:
                        current_mtime = os.path.getmtime(script)
                        if current_mtime > self._last_mtime[script] and not self._reconnecting:
                            self._reconnecting = True
                            self._last_mtime[script] = current_mtime
                            print(f"\n🔔 检测到 {script} 文件变化，正在重连...")
                            await self.connect()
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
            
            # ✅ 找到对应的 client 来调用
            client = await user_client._find_client_by_tool(tool_call.function.name) # type: ignore
            if client is None:
                print(f"❌ 找不到 {tool_call.function.name} 对应的 Server") # type: ignore
                continue
            
            tool_result = await client.call_tool(
                tool_call.function.name, args # type: ignore
            )
            print(f"📦 工具结果: {tool_result}")

            user_client.messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(tool_result),
            })


async def loop(user_client: UserClient):
    print("🤖 AI 助手已启动，输入 'exit' 或 'quit' 退出\n")
    
    await user_client.connect()
    print(f"📋 当前工具数量: {len(user_client.tools)}")
    for t in user_client.tools:
        print(f"   - {t['function']['name']}")
    
    asyncio.create_task(user_client._watch_file_changes())
    
    try:
        while True:
            question = input("User: ")
            if question.lower() in ["exit", "quit"]:
                break
                
            if question.lower() in ["mcptools", "tools", "tool", "mcptool"]:
                await user_client.connect()
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
