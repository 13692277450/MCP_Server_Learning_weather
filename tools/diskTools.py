# ai_chat_with_tools.py
import json
import os
import sys
from typing import Optional
from openai import OpenAI
from mcppackages.mcp_diskinfoClient import get_disk_info, print_disk_info

# ============ 配置 ============
DEEPSEEK_API_KEY = "sk-c703c80f917848549e082b36e0bf0538"  # 替换为你的 API Key
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PATH = os.path.join(SCRIPT_DIR, "mcp_diskInfoServer.py")

# ============ 初始化客户端 ============
client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=DEEPSEEK_API_KEY,
)

# ============ 定义工具（Tools） ============
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_disk_info",
            "description": "获取电脑的硬盘分区和硬件详细信息，包括：分区大小、已使用空间、剩余空间、使用率、物理磁盘型号、品牌、接口类型、IO统计等",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_health": {
                        "type": "boolean",
                        "description": "是否包含磁盘健康状态信息，默认为 false"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["simple", "detailed"],
                        "description": "返回格式：simple 返回摘要，detailed 返回完整信息"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_disk_health",
            "description": "获取磁盘健康状态和 SMART 信息",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# ============ 工具执行函数 ============
def execute_tool_call(tool_name: str, arguments: dict):
    """执行工具调用"""
    if tool_name == "get_disk_info":
        include_health = arguments.get("include_health", False)
        format_type = arguments.get("format", "simple")
        # 调用 MCP Server
        result = get_disk_info()
        
        if result.get("status") != "success":
            return json.dumps({"error": result.get("message", "获取失败")})
        data = result.get("data", {})
        return json.dumps(data, ensure_ascii=False)
    return json.dumps({"error": f"未知工具: {tool_name}"})

# ============ AI 对话函数 ============
def chat_with_ai(user_message: str, messages: Optional[list] = None):
    """
    与 AI 对话，自动处理工具调用
    
    Args:
        user_message: 用户输入
        messages: 历史消息列表
    
    Returns:
        AI 的回复
    """
    if messages is None:
        messages = [
            {
                "role": "system",
                "content": """你是一个智能助手，可以帮助用户获取电脑磁盘信息。
                
当用户询问磁盘、硬盘、分区、存储空间等相关问题时，你应该使用 get_disk_info 工具来获取信息。

工具使用规则：
1. 如果用户问 "磁盘有多大"、"硬盘还剩多少空间"、"分区使用率" 等，调用 get_disk_info
2. 如果用户想了解磁盘健康状态，调用 get_disk_info 并设置 include_health=true
3. 如果用户想了解详细硬件信息，调用 get_disk_info 并设置 format="detailed"
4. 根据用户的问题，用通俗易懂的语言解释数据

回复风格：
- 用友好的语气
- 如果数据量大，用表格或列表展示
- 如果有警告（如使用率 > 90%），要提醒用户
"""
            },
            {"role": "user", "content": user_message}
        ]
    else:
        messages.append({"role": "user", "content": user_message})
    
    # 第一次调用：让 AI 决定是否需要调用工具
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # AI 自动决定是否调用
        temperature=0.7,
    )
    
    message = response.choices[0].message
    
    # 检查是否有工具调用
    if message.tool_calls:
        print(f"🔧 AI 决定调用工具: {[t.function.name for t in message.tool_calls]}")
        
        # 添加 AI 的响应到消息历史
        messages.append(message)
        
        # 执行所有工具调用
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"   📞 调用 {tool_name}({arguments})")
            
            # 执行工具
            tool_result = execute_tool_call(tool_name, arguments)
            
            # 添加工具结果到消息历史
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })
        
        # 第二次调用：AI 基于工具结果生成最终回复
        final_response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
        )
        
        final_message = final_response.choices[0].message
        messages.append(final_message)
        
        return final_message.content, messages
    
    else:
        # 没有工具调用，直接返回
        messages.append(message)
        return message.content, messages

# ============ 交互式对话 ============
def interactive_chat():
    """交互式对话"""
    print("=" * 60)
    print("💬 AI 助手 - 支持磁盘信息查询")
    print("=" * 60)
    print("\n你可以问:")
    print("  - 我的硬盘有多大？")
    print("  - C盘还剩多少空间？")
    print("  - 磁盘使用率是多少？")
    print("  - 详细硬件信息")
    print("  - 输入 'quit' 退出\n")
    
    messages = None
    
    while True:
        user_input = input("\n👤 你: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 再见！")
            break
        
        if not user_input:
            continue
        
        print("🤔 AI 正在思考...")
        
        try:
            reply, messages = chat_with_ai(user_input, messages)
            print(f"\n🤖 AI: {reply}")
        except Exception as e:
            print(f"❌ 错误: {e}")

# ============ 测试示例 ============
def test_single_query():
    """测试单个查询"""
    queries = [
        "我的电脑硬盘有多大？",
        "C盘还剩多少空间？",
        "磁盘使用率是多少？",
        "帮我看看磁盘的详细信息",
    ]
    
    for query in queries:
        print("\n" + "=" * 60)
        print(f"👤 用户: {query}")
        print("=" * 60)
        
        reply, _ = chat_with_ai(query)
        print(f"\n🤖 AI: {reply}\n")

if __name__ == "__main__":
    # 交互模式
    interactive_chat()
    
    # 或者测试模式
    # test_single_query()