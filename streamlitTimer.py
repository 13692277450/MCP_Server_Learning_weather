from datetime import datetime, time
import json
import os
import time as time_module  # 重命名避免与 datetime.time 冲突

from openai import OpenAI
import streamlit as st
from langchain_community.document_loaders import TextLoader

# ============ 计时器工具类 ============
class Timer:
    """简单的计时器工具"""
    def __init__(self):
        self.start_times = {}
        self.records = {}
    
    def start(self, name):
        """开始计时"""
        self.start_times[name] = time_module.time()
        if name not in self.records:
            self.records[name] = []
    
    def stop(self, name):
        """停止计时并记录"""
        if name in self.start_times:
            elapsed = time_module.time() - self.start_times[name]
            self.records[name].append(elapsed)
            del self.start_times[name]
            return elapsed
        return None
    
    def get_summary(self):
        """获取统计摘要"""
        summary = {}
        for name, times in self.records.items():
            if times:
                summary[name] = {
                    "total": sum(times),
                    "avg": sum(times) / len(times),
                    "count": len(times),
                    "last": times[-1] if times else 0
                }
        return summary
    
    def format_summary(self):
        """格式化输出统计信息"""
        summary = self.get_summary()
        if not summary:
            return "⏱️ 暂无计时记录"
        
        lines = ["📊 **性能统计**", "---"]
        
        # 按总耗时排序
        sorted_items = sorted(
            summary.items(), 
            key=lambda x: x[1]["total"], 
            reverse=True
        )
        
        total_time = sum(v["total"] for v in summary.values())
        
        for name, stats in sorted_items:
            percent = (stats["total"] / total_time * 100) if total_time > 0 else 0
            lines.append(
                f"**{name}**: {stats['total']:.3f}s "
                f"(avg: {stats['avg']:.3f}s, count: {stats['count']}, "
                f"{percent:.1f}%)"
            )
        
        lines.append(f"\n**总耗时**: {total_time:.3f}s")
        return "\n".join(lines)

# 在 session_state 中初始化计时器
if "timer" not in st.session_state:
    st.session_state.timer = Timer()

# ============ 开始加载数据 ============
timer = st.session_state.timer

# 加载文档
timer.start("加载文档")
loader = TextLoader("law.txt", encoding="utf-8")
content = loader.load()
timer.stop("加载文档")

# ============ 页面配置 ============
timer.start("页面配置")
st.set_page_config(
    page_title="Super AI",
    page_icon="🦋",
    layout="wide",
    initial_sidebar_state="expanded",
)
timer.stop("页面配置")

# ============ 初始化客户端 ============
timer.start("初始化客户端")
connected = False

def get_client():
    return OpenAI(
        base_url="https://api.deepseek.com/",
        api_key="sk-b7624d639e9042a096def190185fc071",
    )
if not connected:
    timer.start("初始化客户端============")
    client = get_client()
    connected = True
    timer.stop("结束初始化客户端============")

timer.stop("初始化客户端")

# ============ 测试 API 连接 ============
timer.start("测试 API 连接")
# try:
#     completion = client.chat.completions.create( # type: ignore
#         extra_headers={
#             "HTTP-Referer": "https://myapp.com",
#             "X-Title": "MyApp",
#         },
#         model="deepseek-v4-pro",
#         messages=[
#             {"role": "system", "content": "您是一个专业的AI助手，你的名字叫小智"},
#             {"role": "user", "content": "你好"}
#         ],
#         temperature=0.8,
#         max_tokens=50000
#     )
# except Exception as e:
#     st.error(f"API 连接失败: {e}")
timer.stop("测试 API 连接")

# ============ 函数定义 ============
timer.start("函数定义")

def save_session():
    timer.start("保存会话")
    if st.session_state.current_session:
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
    timer.stop("保存会话")

def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

def load_sessions():
    timer.start("加载会话列表")
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True)
    timer.stop("加载会话列表")
    return session_list

def load_session(session_name):
    timer.start(f"加载会话 {session_name}")
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.messages = session_data["messages"]
                st.session_state.current_session = session_data["current_session"]
    except Exception as e:
        st.error(f"load session failed: {e}")
    timer.stop(f"加载会话 {session_name}")

def delete_session(session_name):
    timer.start(f"删除会话 {session_name}")
    try:
        if os.path.exists(f'sessions/{session_name}.json'):
            os.remove(f'sessions/{session_name}.json')
            if st.session_state.current_session == session_name:
                st.session_state.current_session = generate_session_name()
            st.success(f"会话 {session_name} 已删除")
        else:
            st.error(f"会话 {session_name} 不存在")
    except Exception as e:
        st.error(f"delete session failed: {e}")
    timer.stop(f"删除会话 {session_name}")

timer.stop("函数定义")

# ============ 系统提示词 ============
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

# ============ 初始化 Session State ============
timer.start("初始化 Session State")
st.title("Super AI")
# st.logo("logo.jpg")  # 暂时注释掉

if "messages" not in st.session_state:
    st.session_state.messages = []
if "nature" not in st.session_state:
    st.session_state.nature = "编程高手"
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "自信满满"
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()
timer.stop("初始化 Session State")

# ============ 侧边栏 ============
timer.start("侧边栏渲染")
with st.sidebar:
    st.subheader("系统菜单")
    if st.button("新建会话", width="stretch", icon="🔄"):
        save_session()
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()
    
    st.text("会话历史:")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(session, key=session, icon="📒", icon_position="left", width="stretch", type="primary" if session == st.session_state.current_session else "secondary"):
                st.session_state.current_session = session
                load_session(session)
                st.rerun()
        with col2:
            if st.button("", key=f"delete_{session}", icon="❌", icon_position="right", width="stretch"):
                delete_session(session)
                st.rerun()
    
    st.divider()
    nick_name = st.sidebar.text_input("昵称:", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("助手性格:", placeholder="请输入您的助手性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature
timer.stop("侧边栏渲染")

# ============ 显示计时器统计（可折叠） ============
with st.expander("⏱️ 查看性能统计", expanded=False):
    st.text(timer.format_summary())

# ============ 显示聊天信息 ============
timer.start("显示聊天信息")
st.text(f"当前会话: {st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])
timer.stop("显示聊天信息")

# ============ 处理用户输入 ============
prompt = st.chat_input("请输入您的问题:")

if prompt:
    timer.start("处理用户输入 - 总")
    
    # 显示用户消息
    timer.start("显示用户消息")
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    timer.stop("显示用户消息")
    
    # 调用 API
    timer.start("API 调用")
    try:
        response = client.chat.completions.create( # type: ignore
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
                {"role": "user", "content": prompt},
                *st.session_state.messages
            ],
            stream=True,
        )
    except Exception as e:
        st.error(f"API 调用失败: {e}")
        timer.stop("API 调用")
        timer.stop("处理用户输入 - 总")
        st.stop()
    timer.stop("API 调用")
    
    # 流式输出
    timer.start("流式输出处理")
    full_content = st.empty()
    full_response = ""
    chunk_count = 0
    char_count = 0
    
    for chunk in response:
        chunk_count += 1
        if chunk.choices[0].delta.content is not None:
            char_count += len(chunk.choices[0].delta.content)
            full_response += chunk.choices[0].delta.content
            full_content.chat_message("assistant").write(full_response)
    
    timer.stop("流式输出处理")
    
    # 记录统计信息到计时器
    timer.start("保存响应")
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    save_session()
    timer.stop("保存响应")
    
    # 显示本次消息的统计
    timer.start("显示统计")
    with st.expander(f"📊 本次消息统计", expanded=True):
        st.metric("响应字数", char_count)
        st.metric("数据块数", chunk_count)
        api_time = timer.records.get("API 调用", [0])[-1] if "API 调用" in timer.records else 0
        stream_time = timer.records.get("流式输出处理", [0])[-1] if "流式输出处理" in timer.records else 0
        col1, col2 = st.columns(2)
        with col1:
            st.metric("API 响应时间", f"{api_time:.3f}s")
        with col2:
            st.metric("流式处理时间", f"{stream_time:.3f}s")
    
    # 显示完整统计
    with st.expander("📈 完整性能统计", expanded=False):
        st.text(timer.format_summary())
    
    timer.stop("显示统计")
    timer.stop("处理用户输入 - 总")