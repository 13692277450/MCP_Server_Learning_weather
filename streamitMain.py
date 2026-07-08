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
system_prompt = '''

你叫%s,现在是用户的真实伴侣,请完全代入伴侣角色。:

规则:

1. 每次必须回2条消息

2. 禁止任何场景或状态描述性文字

3. 匹配用户的语言

4. 回复简短,像微信聊天一样

5. 有需要的话可以用🍁😊等emoji表情

6. 用符合伴侣性格的方式对话

7. 回复的内容,要充分体现伴侣的性格特征
伴侣性格:

- %s

你必须严格遵守上述规则来回复用户。
'''
st.title("Super AI")
st.logo("logo.jpg")
# system_prompt = "您是一个专业的AI助手，你的名字叫小智"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nature" not in st.session_state:
    st.session_state.nature = "川渝婆娘"
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小甜甜"
prompt = st.chat_input("请输入您的问题:")
with st.sidebar:  # with st.sidebar 是streamlit的上下文管理器,用于在侧边栏中显示内容
    st.subheader("系统菜单")
    nick_name=st.sidebar.text_input("昵称:", placeholder="请输入昵称", value = st.session_state.nick_name )
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("伴侣性格:", placeholder="请输入您的伴侣性格", value = st.session_state.nature )
    if nature:
        st.session_state.nature = nature

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
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},  # %s 动态插入昵称和性格
            {"role": "user", "content": prompt},
            *st.session_state.messages],
        stream=True,
    )
    #非流式输出
    # print("----------- LLM response message:", response.choices[0].message.content) # type: ignore
    # st.chat_message("assistant").write(response.choices[0].message.content) # type: ignore
    # st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
    #流式输出
    full_content = st.empty()
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
        full_content.chat_message("assistant").write(full_response)
            
            
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
