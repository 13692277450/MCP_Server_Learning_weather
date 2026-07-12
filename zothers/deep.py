import asyncio
import json
from openai import OpenAI
from fastmcp import Client
from typing import List, Dict, Any


class UserClient:
    def __init__(self, script="server.py", model="deepseek-v4-pro"):
        self.model = model
        self.messages: List[Dict[str, Any]] = []
        
        self.script = script
        self.mcp_client = Client(script)
        self.openai_client = OpenAI(
            api_key="sk-80289082a38c4136a41834f93058d4b",  #test after b
            base_url="https://api.deepseek.com/v1",
        )
    
    async def prepare_tools(self):
        """获取 MCP Server 的工具列表"""
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
            print(f"❌ 获取工具失败: {e}")
            return []
    
    async def chat(self, messages: List[Dict]) -> Dict[str, Any]:
        """与 LLM 对话，并执行工具调用"""
        try:
            # 准备工具
            tools = await self.prepare_tools()
            
            # 调用 LLM
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
            
            # ✅ 关键：处理工具调用
            if hasattr(message, 'tool_calls') and message.tool_calls is not None:
                print(f"🔧 AI 想要调用 {len(message.tool_calls)} 个工具")
                
                tool_results = []
                for tool_call in message.tool_calls:
                    # 获取工具信息
                    function = getattr(tool_call, 'function', None)
                    if function is None:
                        continue
                    
                    tool_name = getattr(function, 'name', '')
                    tool_args_str = getattr(function, 'arguments', '{}')
                    
                    print(f"   📞 调用工具: {tool_name}")
                    print(f"   📝 参数: {tool_args_str}")
                    
                    try:
                        # 解析参数
                        tool_args = json.loads(tool_args_str) if tool_args_str else {}
                        
                        # ✅ 执行 MCP 工具调用
                        tool_result = await self.mcp_client.call_tool(
                            tool_name,
                            tool_args
                        )
                        print(f"   ✅ 工具执行成功: {tool_result}")
                        
                        tool_results.append({
                            "tool_call_id": getattr(tool_call, 'id', ''),
                            "role": "tool",
                            "content": str(tool_result),
                        })
                        
                    except json.JSONDecodeError as e:
                        print(f"   ❌ 参数解析失败: {e}")
                        tool_results.append({
                            "tool_call_id": getattr(tool_call, 'id', ''),
                            "role": "tool",
                            "content": f"参数解析错误: {e}",
                        })
                    except Exception as e:
                        print(f"   ❌ 工具执行失败: {e}")
                        tool_results.append({
                            "tool_call_id": getattr(tool_call, 'id', ''),
                            "role": "tool",
                            "content": f"工具执行错误: {e}",
                        })
                
                # 如果有工具结果，添加到消息历史并再次调用 LLM
                if tool_results:
                    # 添加原始工具调用到历史
                    result["tool_calls"] = [
                        {
                            "id": getattr(tc, 'id', ''),
                            "type": "function",
                            "function": {
                                "name": getattr(getattr(tc, 'function', None), 'name', ''),
                                "arguments": getattr(getattr(tc, 'function', None), 'arguments', '{}'),
                            }
                        }
                        for tc in message.tool_calls
                    ]
                    
                    # 添加工具结果到消息历史
                    messages_with_results = messages + [result] + tool_results
                    
                    # 再次调用 LLM 获取最终响应
                    final_response = self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=messages_with_results,  # type: ignore
                    )
                    
                    final_message = final_response.choices[0].message
                    result["content"] = final_message.content or ""
                    
                    return result
            
            return result
            
        except Exception as e:
            print(f"❌ chat() 错误: {e}")
            import traceback
            traceback.print_exc()
            return {
                "role": "assistant",
                "content": f"抱歉，发生了错误: {str(e)}",
            }
    
    async def loop(self):
        """交互式对话循环"""
        print("🤖 AI 助手已启动，输入 'exit' 或 'quit' 退出\n")
        
        async with self.mcp_client:
            print("✅ 已连接到 MCP Server")
            
            # 获取并显示可用工具
            tools = await self.mcp_client.list_tools()
            print(f"📊 可用工具: {[tool.name for tool in tools]}\n")
            
            while True:
                try:
                    question = input("User: ").strip()
                    
                    if question.lower() in ["exit", "quit", "退出"]:
                        print("👋 再见！")
                        break
                    
                    if not question:
                        continue
                    
                    # 添加用户消息
                    self.messages.append({"role": "user", "content": question})
                    
                    # 调用 chat 并获取响应
                    response_message = await self.chat(self.messages)
                    
                    # 打印响应
                    if response_message:
                        content = response_message.get("content", "")
                        if content:
                            print("AI:", content)
                        else:
                            print("AI: (空响应)")
                        
                        self.messages.append(response_message)
                    
                except KeyboardInterrupt:
                    print("\n👋 再见！")
                    break
                except Exception as e:
                    print(f"❌ 发生错误: {e}")


async def main():
    user_client = UserClient()
    await user_client.loop()

if __name__ == "__main__":
    asyncio.run(main())