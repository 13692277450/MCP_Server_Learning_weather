from openai import OpenAI
import streamlit as st

st.set_page_config(
    page_title="Super AI",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        
    }
)
client = OpenAI(
    base_url="https://api.deepseek.com/",
    api_key="sk-b7624d639e9042a096def190185fc071",
    
)
completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://myapp.com",
                    "X-Title": "MyApp",
                },
                # model="openrouter/free",
                model="deepseek-v4-pro",
                messages=[
                    {"role": "system", "content": "您是一个专业的AI助手，你的名字叫小智"},
                    {"role": "user", "content": "你好"}],
                temperature=0.8,
                max_tokens=50000

            )
#大标题
st.title("Super AI")
st.logo("logo.jpg")
prompt = st.chat_input("请输入您的问题")
system_prompt = "您是一个专业的AI助手，你的名字叫小智"
if "messages" not in st.session_state:
    st.session_state.messages = []
#展示聊天信息
for message in st.session_state.messages:
    #简化
    st.chat_message(message["role"]).write(message["content"])
    # if message["role"] == "user":
    #     st.chat_message("user").write(message["content"])
    # elif message["role"] == "assistant":
    #     st.chat_message("assistant").write(message["content"])
if prompt:
    # st.write(f"您输入的问题是：{prompt}")
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
            *st.session_state.messages],
        stream=False,
    )
    print("----------- LLM response message:", response.choices[0].message.content) # type: ignore
    st.chat_message("assistant").write(response.choices[0].message.content) # type: ignore
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
