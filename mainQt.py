
from typing import Dict, List

from openai import OpenAI
import time
from fastmcp import FastMCP
from fastmcp import Client
import mainWindow
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QPlainTextEdit, QWidget, QVBoxLayout,
                               QHBoxLayout, QToolButton, QLabel)
from PySide6.QtGui import QIcon, QKeySequence, QPixmap, QPainter, QColor, QFont, QShortcut, QTextCursor
from PySide6.QtCore import QEvent, QThread, Qt, QSize, Signal
from PySide6.QtWidgets import QApplication, QMainWindow

from mainWindow import Ui_MainWindow   # 导入 Qt Designer 生成的类

class AutoClearPlainTextEdit(QPlainTextEdit):
    """自定义文本框：获得焦点时自动清空"""
    def focusInEvent(self, event):
            self.clear()
            super().focusInEvent(event)
    # ui.setupUi(window)   # 把 Designer 里设计的控件"安装"到窗口
# ============ AI 对话线程（避免界面卡顿） ============
class AIThread(QThread):
    # 定义信号，用于更新界面
    reply_received = Signal(str)
    error_occurred = Signal(str)
    """只做一次最小化调用，验证 API 是否通"""
    test_ok = Signal(str)     # 成功时发射 model 名称或其它信息
    test_fail = Signal(str)   # 失败时发射错误信息
    

    def __init__(self, messages, script="weatherServer.py"):
        super().__init__()
        self.mcp_client = Client(script)
        self.messages = messages
    
    def run(self):
        try:
            client = OpenAI(
                # base_url="https://openrouter.ai/api/v1",
                # api_key="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",
                api_key="sk-b7624d639e9042a096def190185fc071",  #test after b
                base_url="https://api.deepseek.com/v1",
            )
            
            
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://myapp.com",
                    "X-Title": "MyApp",
                },
                # model="openrouter/free",
                model="deepseek-v4-pro",
                messages=self.messages,
                temperature=0.8,
                max_tokens=50000

            )
            self.tools = []
            self._ensure_client() # type: ignore
            self.tools = self.prepare_tools() # type: ignore
            reply = completion.choices[0].message.content
            content = completion.choices[0].message.content or "(empty)"

            self.reply_received.emit(reply)
            self.test_ok.emit(
            f"[OK] AI 连接成功\n"
            f"  base_url: https://openrouter.ai/api/v1\n"
            f"  model:    openrouter/free\n"
            f"  reply:    {content.strip()[:120]}..." # type: ignore
        )      
        except Exception as e:
            self.test_fail.emit(f"[FAIL] OpenAI 连接失败: {str(e)}")
        async def _ensure_client(self):
            if self.mcp_client is None:
                self.mcp_client = await Client(self.model).__aenter__()
            return self.mcp_client
        
        async def prepare_tools(self):
            tools = await self.mcp_client.list_tools()
            tools = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,  # ⭐ 用 parameters，不是 input_schema
                },
            } for tool in tools]
            return tools
        async def chat(self, messages: List[Dict]):
            async with self.mcp_client:
                if not self.tools:
                    self.tools = await self.prepare_tools()
                # ⭐ 循环：只要 LLM 说要调用工具，就继续对话
                while True:
                    response = self.openai_client.chat.completions.create(
                        model=self.model,
                        messages=messages,  # type: ignore
                        tools=self.tools,  # type: ignore
                    )
                    message = response.choices[0].message

                    # ① 如果不需要调用工具，直接返回回答.`qwe`
                    if response.choices[0].finish_reason != "tool_calls" or not message.tool_calls:
                        return message

                    # ② 把 LLM 的 tool_calls 消息加入对话历史
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
                    messages.append(tool_calls_message)  # type: ignore

                    # ③ 逐个调用工具，把结果加回对话
                    for tool_call in message.tool_calls:
                        # self.ui.plainTextEdit_MCP.appendPlainText(f"\nTool Call: {tool_call.function.name}")
                        args = json.loads(tool_call.function.arguments) # type: ignore
                        self.ui.plainTextEdit_AIChat.appendPlainText(f"🔧 调用工具: {tool_call.function.name}, 参数: {args}") # type: ignore
                        tool_result = await self.mcp_client.call_tool(
                            tool_call.function.name, args # type: ignore
                        )
                        self.ui.plainTextEdit_AIChat.appendPlainText(f"📦 工具结果: {tool_result}")

                        # 把工具结果加回对话
                        messages.append({  # type: ignore
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(tool_result),
                        })

                    # ④ 循环继续，让 LLM 用工具结果生成最终回答

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ai_thread = AIThread("你好，你是谁？ 你可以做什么？")
        self.ui.setupUi(self)
        self._install_autoclear()
        # 初始化对话历史
        # GridLayout 行 1（AI 显示框所在行）设为主要扩展行
        self.ui.gridLayout.setRowStretch(1, 5)   # AI 显示框区域占大头
        # GridLayout 列 1（中间列）设为主要扩展列
        self.ui.gridLayout.setColumnStretch(1, 5)
        self.messages = [
            {"role": "system", "content": "你是一个有用的AI助手。"}
        ]
        self.ui.plainTextEdit_infor.setPlaceholderText("System information...\n\n")

        # 连接信号槽
        self.ai_thread.reply_received.connect(self.ui.plainTextEdit_AIChat.appendPlainText)
        self.ai_thread.error_occurred.connect(self.ui.plainTextEdit_infor.appendPlainText)
        self.ai_thread.start()
        # 显示框：只读
        self.ui.plainTextEdit_AIChat.setReadOnly(True)
        self.ui.plainTextEdit_AIChat.setPlaceholderText("AI 对话内容将显示在这里...")
        # 输入框
        # self.ui.plainTextEdit_ChatSend.installEventFilter(self)
        # self.eventFilter(self.ui.plainTextEdit_ChatSend, QEvent(QEvent.FocusIn)) # type: ignore
        # if self.ui.plainTextEdit_ChatSend.hasFocus():
        #     self.ui.plainTextEdit_ChatSend.clear()
        self.ui.plainTextEdit_ChatSend.setPlaceholderText(
            "在这里输入消息（Ctrl+Enter 发送）..."
        )
        self.ui.plainTextEdit_AIChat.appendPlainText("\n[系统提示] 对话信息窗口，请等待 AI 连接成功... \n")
        # 发送按钮
        self.ui.pushButton.setText("CHAT SEND")
        self.ui.pushButton.clicked.connect(self.on_send_chat)

        # —— Ctrl+Enter 发送消息 ——
        self.shortcut_send = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut_send.activated.connect(self.on_send_chat)
        # System Information 面板：只读
        self.ui.plainTextEdit_infor.setReadOnly(True)
        # ====== 启动时跑一次连接测试 ======
        self.on_conn_test("")
        time.sleep(5)
        if self.on_conn_ok:
            # self.ui.plainTextEdit_AIChat.clear()
            # self.ui.plainTextEdit_AIChat.moveCursor(QTextCursor.Start)  # type: ignore
            self.ui.plainTextEdit_AIChat.appendPlainText("\n[系统信息：AI 连接成功] 可以开始对话：\n")
        else:
            # self.ui.plainTextEdit_AIChat.clear()
            # self.ui.plainTextEdit_AIChat.moveCursor(QTextCursor.Start)  # type: ignore
            self.ui.plainTextEdit_AIChat.appendPlainText("\n[系统信息：AI 连接失败] 请检查网络设置或稍后重试...\n")
            
        self.ui.pushButton_ConnTest.clicked.connect(self.on_conn_test)
        self.ui.pushButton_ClearAIChat.clicked.connect(self.clear_textEdit_AIChat)
    
    def clear_textEdit_AIChat(self):
        self.ui.plainTextEdit_AIChat.clear()
        self.ui.plainTextEdit_AIChat.moveCursor(QTextCursor.Start)  # type: ignore
        self.ui.plainTextEdit_AIChat.appendPlainText("\n[系统提示] 与AI对话信息窗口... \n")
    def on_conn_test(self, result):
        self.ui.plainTextEdit_infor.appendPlainText(
            "  🚜🚜🚜正在测试 AI 连接...🚜🚜🚜\n"
        )
        self.conn_test = AIThread(self.messages.copy())
        result = self.conn_test.test_ok.connect(self.on_conn_ok)
        self.conn_test.test_fail.connect(self.on_conn_fail)
        self.conn_test.start()
        # print("result:", result)
        return result
        # ====== 点击按钮或 Ctrl+Enter 时调用 ======
    def on_send_chat(self):
        user_input = self.ui.plainTextEdit_ChatSend.toPlainText().strip()
        if not user_input:
            self.ui.plainTextEdit_AIChat.appendPlainText("\n[请先输入消息]\n")
            return

        # 显示用户消息
        self.messages.append({"role": "user", "content": user_input})
        # self.ui.plainTextEdit_AIChat.appendPlainText(f"\n🥸You: ")
        # self.ui.plainTextEdit_AIChat.appendHtml(f'<p style="color:#5F1FD6;">{user_input}</p>\n')
        self.ui.plainTextEdit_AIChat.appendHtml(f'<p><span style="color:#5F1FD6;">🥸 You: </span>'
        f'<span style="color:#5F1FD6;">{user_input}</span></p>')
        # 清空输入框
        self.ui.plainTextEdit_ChatSend.clear()

        # 启动 AI 线程
        self.ai_thread = AIThread(self.messages.copy())
        self.ai_thread.reply_received.connect(self.on_ai_reply)
        self.ai_thread.error_occurred.connect(self.on_ai_error)
        self.ai_thread.start()
        
    def on_ai_reply(self, reply):
            self.messages.append({"role": "assistant", "content": reply})
            self.ui.plainTextEdit_AIChat.appendPlainText(f"🤖AI: {reply}\n")

    def on_ai_error(self, err_msg): 
            self.ui.plainTextEdit_AIChat.appendPlainText(f"\n[错误] {err_msg}\n")
    
    # ========== 连接测试回调 ==========
    def on_conn_ok(self, msg):
        """连接测试成功：把消息追加到 System Information 面板"""
        self.ui.plainTextEdit_infor.appendPlainText(msg + "\n")
        self.ui.plainTextEdit_AIChat.clear()
        self.ui.plainTextEdit_AIChat.moveCursor(QTextCursor.Start)  # type: ignore
        self.ui.plainTextEdit_AIChat.appendPlainText("\n[系统信息：AI 连接成功] 可以开始对话：\n")

    def on_conn_fail(self, msg):
        """连接测试失败：把错误信息追加到 System Information 面板"""
        self.ui.plainTextEdit_infor.appendPlainText(msg + "\n")
        self.ui.plainTextEdit_AIChat.clear()
        self.ui.plainTextEdit_AIChat.moveCursor(QTextCursor.Start)  # type: ignore
        self.ui.plainTextEdit_AIChat.appendPlainText("\n[系统信息：AI 连接失败] 请检查网络设置或稍后重试...\n")

    def closeEvent(self, event):
        for t in [self.ai_thread, self.conn_test]:
            if t is not None and t.isRunning():
                t.quit()
                t.wait(200)
        super().closeEvent(event)
    # ============ 加一个新方法：事件过滤器 ============
    def eventFilter(self, obj, event):
        if obj == self.ui.plainTextEdit_ChatSend:
            # 当输入框获得焦点（鼠标点击 / Tab 进入）时
            if event.type() == QEvent.FocusIn: # type: ignore
                self.ui.plainTextEdit_ChatSend.clear()
                # 清掉后 placeholderText 会自动显示
        # 让父类继续处理其他事件
        return super().eventFilter(obj, event)
    def _install_autoclear(self):
        widget = self.ui.plainTextEdit_ChatSend

        # 保存原方法（必须先保存再覆盖）
        original_mouse_press = widget.mousePressEvent

        def custom_mouse_press(event):
            widget.clear()  # 点击就清空
            
            original_mouse_press(event)  # 调用原方法，让光标正常定位到点击位置

        widget.mousePressEvent = custom_mouse_press  # 覆盖方法
        widget.setPlaceholderText("")
        print("[调试] autoclear 已安装 ✅")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.showMaximized()
    app.exec()
