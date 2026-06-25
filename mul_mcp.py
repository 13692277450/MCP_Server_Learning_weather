import asyncio
import json
from fastmcp import Client
from openai import OpenAI
from typing import List, Dict, Any, Optional


class MCPServerRegistry:
    """管理多个 MCP Server 的注册表"""
    
    def __init__(self, config_file: str = "mcp_servers.json"):
        self.config_file = config_file
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.clients: Dict[str, Client] = {}
        self.load_config()
    
    def load_config(self):
        """从配置文件加载所有 Server 配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.servers = json.load(f)
            print(f"✅ 加载了 {len(self.servers)} 个 MCP Server 配置")
        except FileNotFoundError:
            print(f"⚠️ 配置文件 {self.config_file} 不存在，使用默认配置")
            self.servers = self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Dict[str, Any]]:
        """默认配置"""
        return {
            "weather": {
                "script": "servers/weather_server.py",
                "enabled": True,
                "description": "天气查询服务"
            },
            "database": {
                "script": "servers/db_server.py",
                "enabled": True,
                "description": "数据库操作服务"
            },
            "file": {
                "script": "servers/file_server.py",
                "enabled": False,
                "description": "文件操作服务"
            }
        }
    
    def get_enabled_servers(self) -> Dict[str, Dict[str, Any]]:
        """获取所有启用的 Server"""
        return {name: config for name, config in self.servers.items() 
                if config.get("enabled", True)}
    
    async def get_client(self, server_name: str) -> Optional[Client]:
        """获取或创建指定 Server 的 Client"""
        if server_name in self.clients:
            return self.clients[server_name]
        
        config = self.servers.get(server_name)
        if not config:
            print(f"❌ Server {server_name} 不存在")
            return None
        
        if not config.get("enabled", True):
            print(f"⚠️ Server {server_name} 已禁用")
            return None
        
        try:
            client = Client(config["script"])
            await client.__aenter__()  # 手动进入上下文
            self.clients[server_name] = client
            print(f"✅ 连接到 Server: {server_name}")
            return client
        except Exception as e:
            print(f"❌ 连接 Server {server_name} 失败: {e}")
            return None
    
    async def close_all(self):
        """关闭所有 Client 连接"""
        for name, client in self.clients.items():
            try:
                await client.__aexit__(None, None, None)
                print(f"✅ 关闭 Server: {name}")
            except:
                pass
        self.clients.clear()
    
    async def list_all_tools(self) -> List[Dict[str, Any]]:
        """从所有 Server 收集所有工具"""
        all_tools = []
        for server_name in self.get_enabled_servers():
            client = await self.get_client(server_name)
            if client:
                try:
                    tools = await client.list_tools()
                    for tool in tools:
                        all_tools.append({
                            "server": server_name,
                            "tool": tool,
                            "type": "function",
                            "function": {
                                "name": f"{server_name}_{tool.name}",  # 添加 Server 前缀避免冲突
                                "description": tool.description,
                                "parameters": tool.inputSchema,
                            }
                        })
                    print(f"📊 {server_name}: 加载了 {len(tools)} 个工具")
                except Exception as e:
                    print(f"❌ 获取 {server_name} 工具失败: {e}")
        return all_tools
    
    async def call_tool(self, full_tool_name: str, arguments: Dict[str, Any]):
        """调用指定工具（自动路由到对应的 Server）"""
        # 解析 server_name 和 tool_name
        if "_" in full_tool_name:
            server_name, tool_name = full_tool_name.split("_", 1)
        else:
            # 如果没有前缀，尝试在所有 Server 中查找
            return await self.call_tool_by_name(full_tool_name, arguments)
        
        client = await self.get_client(server_name)
        if client:
            try:
                return await client.call_tool(tool_name, arguments)
            except Exception as e:
                print(f"❌ 调用工具 {full_tool_name} 失败: {e}")
                return f"错误: {e}"
        return f"Server {server_name} 不可用"
    
    async def call_tool_by_name(self, tool_name: str, arguments: Dict[str, Any]):
        """在所有 Server 中按工具名查找并调用"""
        # 这里可以遍历所有 Server 查找工具
        # 实现略...
        pass


class UserClient:
    def __init__(self, model="deepseek-v4-pro"):
        self.model = model
        self.messages: List[Dict[str, Any]] = []
        
        # 使用 Server 注册表
        self.registry = MCPServerRegistry("mcp_servers.json")
        self.openai_client = OpenAI(
            api_key="sk-80289082a38c4136a41834f93058d4b",  #test after b
            base_url="https://api.deepseek.com/v1",
        )
    
    async def prepare_tools(self):
        """从所有 Server 获取工具列表"""
        return await self.registry.list_all_tools()
    
    async def chat(self, messages: List[Dict]) -> Dict[str, Any]:
        """与 LLM 对话，支持多 Server 工具调用"""
        try:
            tools = await self.prepare_tools()
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else None,
            )
            
            message = response.choices[0].message
            
            result = {
                "role": "assistant",
                "content": message.content or "",
            }
            
            # 处理工具调用
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print(f"🔧 AI 调用了 {len(message.tool_calls)} 个工具")
                
                tool_results = []
                for tool_call in message.tool_calls:
                    function = getattr(tool_call, 'function', None)
                    if function is None:
                        continue
                    
                    tool_name = getattr(function, 'name', '')
                    tool_args_str = getattr(function, 'arguments', '{}')
                    
                    print(f"   📞 调用工具: {tool_name}")
                    
                    try:
                        import json
                        tool_args = json.loads(tool_args_str) if tool_args_str else {}
                        
                        # ✅ 通过注册表调用工具（自动路由到正确的 Server）
                        tool_result = await self.registry.call_tool(tool_name, tool_args)
                        print(f"   ✅ 工具执行成功")
                        
                        tool_results.append({
                            "tool_call_id": getattr(tool_call, 'id', ''),
                            "role": "tool",
                            "content": str(tool_result),
                        })
                    except Exception as e:
                        print(f"   ❌ 工具执行失败: {e}")
                        tool_results.append({
                            "tool_call_id": getattr(tool_call, 'id', ''),
                            "role": "tool",
                            "content": f"错误: {e}",
                        })
                
                # 如果有工具结果，再次调用 LLM 生成最终回答
                if tool_results:
                    result["tool_calls"] = [...]
                    messages_with_results = messages + [result] + tool_results
                    final_response = self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=messages_with_results,
                    )
                    result["content"] = final_response.choices[0].message.content or ""
            
            return result
        except Exception as e:
            print(f"❌ chat() 错误: {e}")
            return {"role": "assistant", "content": f"抱歉，发生了错误: {str(e)}"}
    
    async def loop(self):
        """交互式对话循环"""
        print("🤖 AI 助手已启动，输入 'exit' 或 'quit' 退出\n")
        
        try:
            # 显示所有可用工具
            tools = await self.prepare_tools()
            print(f"📊 加载了 {len(tools)} 个工具")
            for tool in tools:
                print(f"   - {tool['function']['name']}: {tool['function'].get('description', '')}")
            print()
        except Exception as e:
            print(f"⚠️ 加载工具失败: {e}")
        
        while True:
            try:
                question = input("User: ").strip()
                if question.lower() in ["exit", "quit", "退出"]:
                    print("👋 再见！")
                    break
                if not question:
                    continue
                
                self.messages.append({"role": "user", "content": question})
                response = await self.chat(self.messages)
                
                if response:
                    content = response.get("content", "")
                    if content:
                        print("AI:", content)
                        self.messages.append(response)
                    else:
                        print("AI: (空响应)")
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
        
        # 关闭所有连接
        await self.registry.close_all()


async def main():
    user_client = UserClient()
    await user_client.loop()


if __name__ == "__main__":
    asyncio.run(main())