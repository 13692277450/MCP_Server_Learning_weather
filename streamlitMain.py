from datetime import datetime, time
import json
import os

from openai import OpenAI
import streamlit as st
from langchain_community.document_loaders import TextLoader
from mcp_client import call_tool_sync


# loader = TextLoader("law.txt", encoding="utf-8")
# content = loader.load()
st.set_page_config(
    page_title="Super AI",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
        
    # }
)

def get_client():
    return OpenAI(
    base_url="https://api.deepseek.com/",
    api_key="sk-b7624d639e9042a096def190185fc071",
    
)
client = get_client()
# completion = client.chat.completions.create(
#                 extra_headers={
#                     "HTTP-Referer": "https://myapp.com",
#                     "X-Title": "MyApp",
#                 },
#                 # model="openrouter/free",
#                 model="deepseek-v4-pro",
#                 messages=[
#                     {"role": "system", "content": "您是一个专业的AI助手，你的名字叫小智"},
#                     {"role": "user", "content": "你好"}],
#                 temperature=0.8,
#                 max_tokens=50000

#             )
#大标题
def save_session():
        if st.session_state.current_session: #保存当前会话
            session_data = {
                "nick_name": st.session_state.nick_name,
                "nature": st.session_state.nature,
                "messages": st.session_state.messages,
                "current_session": st.session_state.current_session,
            }
            if not os.path.exists("sessions"):
                os.makedirs("sessions")
            with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=4, ensure_ascii=False)
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H_%M_%S") # type: ignore
def load_sessions():
    session_list=[]
    if os.path.exists("sessions"):
        file_list=os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)
    return session_list
def load_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            with open(f"sessions/{st.session_state.current_session}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.messages = session_data["messages"]
                st.session_state.current_session = session_data["current_session"]
    except Exception as e:
        st.error(f"load session failed: {e}")
def delete_session(session_name):
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            os.remove(f'sessions/{session_name}.json')
            if st.session_state.current_session == session_name:
                st.session_state
                st.session_state.current_session =generate_session_name() # type: ignore
                # save_session()
            st.success(f"会话 {session_name} 已删除")
        else:
            st.error(f"会话 {session_name} 不存在")
    except Exception as e:
        st.error(f"delete session failed: {e}")
def get_disk_info():
    """Streamlit 中调用 MCP 工具"""
    script_path = os.path.join(os.path.dirname(__file__), "mcp_diskInfoServer.py")
    return call_tool_sync(script_path, "get_disk_info")

st.set_page_config(page_title="磁盘信息", layout="wide")
st.title("💾 磁盘信息仪表盘")

if st.button("刷新数据"):
    with st.spinner("正在获取磁盘信息..."):
        result = get_disk_info()
        
        if result and result.get("status") == "success":
            data = result.get("data", {})
            
            # 显示汇总
            summary = data.get("total_summary", {})
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("总容量", f"{summary.get('total_size_gb', 0):.1f} GB")
            col2.metric("已使用", f"{summary.get('total_used_gb', 0):.1f} GB")
            col3.metric("剩余", f"{summary.get('total_free_gb', 0):.1f} GB")
            col4.metric("使用率", f"{summary.get('total_usage_percent', 0):.1f}%")
            
            # 显示分区
            partitions = data.get("partitions", [])
            for part in partitions:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{part.get('drive_letter', '未知')}** - {part.get('volume_name', '未命名')}")
                        st.progress(part.get('usage_percent', 0) / 100)
                    with col2:
                        st.write(f"{part.get('used_gb', 0):.1f} / {part.get('size_gb', 0):.1f} GB")
        else:
            st.error(f"获取失败: {result.get('message', '未知错误')}")
system_prompt = '''

你叫%s,现在是用户的真实助手,请完全代入助手角色。:

规则:

1. 每次必须回2条消息

2. 禁止任何场景或状态描述性文字

3. 匹配用户的语言

4. 回复简短,像微信聊天一样

5. 有需要的话可以用🍁😊等emoji表情

6. 用符合助手性格的方式对话

7. 回复的内容,要充分体现助手的性格特征
8. 助手必须严格遵守用户的指令
9. 必要时可以使用 Yes,sir等专业术语
助手性格:

- %s

你必须严格遵守上述规则来回复用户。
'''

st.title("Super AI")
st.logo("logo.jpg")
# system_prompt = "您是一个专业的AI助手，你的名字叫小智"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nature" not in st.session_state:
    st.session_state.nature = "编程高手"
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "自信满满"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name() # type: ignore
prompt = st.chat_input("请输入您的问题:")

with st.sidebar:  # with st.sidebar 是streamlit的上下文管理器,用于在侧边栏中显示内容
    st.subheader("系统菜单")
    if st.button("新建会话", width="stretch", icon="🔄"):
        save_session()
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name() # type: ignore
            save_session()
            st.rerun()
    st.text("会话历史:")
    session_list=load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            if st.button(session, key=session, icon="📒",icon_position="left", width="stretch", type="primary" if session == st.session_state.current_session  else "secondary" ):
                st.session_state.current_session = session
                load_session(session)
                
                st.rerun()
        with col2:
            if st.button("", key=f"delete_{session}", icon="❌",icon_position="right", width="stretch"):
                # os.remove(f'sessions/{session}.json')
                # session_list.remove(session)
                # st.session_state.current_session = session
                delete_session(session)
                st.rerun()
    st.divider()

    nick_name=st.sidebar.text_input("昵称:", placeholder="请输入昵称", value = st.session_state.nick_name )
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("助手性格:", placeholder="请输入您的助手性格", value = st.session_state.nature )
    if nature:
        st.session_state.nature = nature
    

#展示聊天信息

st.text(f"当前会话: {st.session_state.current_session}")
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
    response = client.chat.completions.create( # type: ignore
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
    
    save_session()

