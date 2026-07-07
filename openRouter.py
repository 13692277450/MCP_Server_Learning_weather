

from openai import OpenAI

# 初始化客户端
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# 初始化对话历史（包含系统提示词，可选）
messages = [
    {"role": "system", "content": "你是一个有用的AI助手。"}
]

def chat_with_ai(user_input):
    """发送消息并获取回复，自动维护对话历史"""
    # 添加用户消息到历史
    messages.append({"role": "user", "content": user_input})
    
    # 调用 API
    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://myapp.com",
            "X-Title": "MyApp",
        },
        model="openrouter/free",
        messages=messages,  # 发送完整的历史记录 # type: ignore
        temperature=0.8,
        max_tokens=500
    )
    
    # 获取 AI 回复
    assistant_reply = completion.choices[0].message.content
    
    # 将 AI 回复也添加到历史中
    messages.append({"role": "assistant", "content": assistant_reply}) # type: ignore
    
    return assistant_reply

# 持续对话循环
print("🤖 开始对话（输入 'quit' 或 'exit' 退出）\n")

while True:
    user_input = input("你: ")
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("👋 再见！")
        break
    
    if not user_input.strip():
        print("⚠️ 请输入有效内容\n")
        continue
    
    try:
        reply = chat_with_ai(user_input)
        print(f"🤖 AI: {reply}\n")
    except Exception as e:
        print(f"❌ 发生错误: {e}\n")
# from openai import OpenAI

# client = OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key="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",
# )

# completion = client.chat.completions.create(
#     extra_headers={
#         "HTTP-Referer": "https://myapp.com",   # 必填
#         "X-Title": "MyApp",                    # 必填
#     },
#     model="openrouter/free",   
#     messages=[
#         {"role": "user", "content": "写一个python的函数,实现a+b=?"}
#     ],
#     temperature=0.8,
#     max_tokens=200
# )

# print(completion.choices[0].message.content)
