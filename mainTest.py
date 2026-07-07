from openai import OpenAI
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
                               QVBoxLayout, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QKeySequence, QShortcut

from mainWindow import Ui_MainWindow   # Qt Designer 生成的 UI 类

SystemMessage =""
# ============ AI 对话线程（避免界面卡顿） ============
class AIThread(QThread):
    reply_received = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def run(self):
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key="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",
            )
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://myapp.com",
                    "X-Title": "MyApp",
                },
                model="openrouter/free",
                messages=self.messages,
                temperature=0.8,
                max_tokens=500
            )
            reply = completion.choices[0].message.content
            self.reply_received.emit(reply)
        except Exception as e:
            self.error_occurred.emit(str(e))


# ============ 主窗口 ============
class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ============================================================
        # 关键修复：用布局管理器替换 Designer 的绝对坐标
        # 让窗口放大时控件同步放大
        # ============================================================
        central = self.ui.centralwidget

        # 清除 centralwidget 上可能存在的旧布局
        old_layout = central.layout()
        if old_layout is not None:
            # 把旧布局里的 widget 先取出来，避免被布局删除
            while old_layout.count():
                item = old_layout.takeAt(0)
                w = item.widget() # type: ignore
                if w:
                    w.setParent(None)

        # 水平布局：左(菜单按钮) | 中(AI 对话区) | 右(MCP/Skills/Info)
        root = QHBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # --- 左侧：菜单按钮区（固定宽度，不随窗口放大） ---
        left_widget = self.ui.formLayoutWidget_2
        left_widget.setMinimumWidth(180)
        left_widget.setMaximumWidth(180)
        left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) # type: ignore
        root.addWidget(left_widget)

        # --- 中间：AI 聊天显示框 + 底部输入框 ---
        mid_col = QVBoxLayout()
        mid_col.setSpacing(8)

        # AI 显示框：占主要空间
        self.ui.plainTextEdit_AIChat.setReadOnly(True)
        self.ui.plainTextEdit_AIChat.setPlaceholderText("AI 对话内容将显示在这里...")
        self.ui.plainTextEdit_AIChat.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # type: ignore
        mid_col.addWidget(self.ui.plainTextEdit_AIChat, 1)  # stretch=1

        # 用户输入框 + 发送按钮（水平排列）
        input_row = QHBoxLayout()
        self.ui.plainTextEdit_ChatSend.setPlaceholderText(
            "在这里输入消息（Ctrl+Enter 发送）..."
        )
        self.ui.plainTextEdit_ChatSend.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # type: ignore
        self.ui.plainTextEdit_ChatSend.setFixedHeight(70)
        input_row.addWidget(self.ui.plainTextEdit_ChatSend, 1)

        self.ui.pushButton.setText("CHAT SEND")
        self.ui.pushButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # type: ignore
        self.ui.pushButton.setFixedSize(120, 70)
        self.ui.pushButton.clicked.connect(self.on_send_chat)
        input_row.addWidget(self.ui.pushButton)

        mid_col.addLayout(input_row)

        mid_widget = QWidget()
        mid_widget.setLayout(mid_col)
        mid_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # type: ignore
        root.addWidget(mid_widget, 3)  # stretch=3, 中间列占大头

        # --- 右侧：MCP / Skills / AI LLM 信息区 ---
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        for w in [self.ui.formLayoutWidget_3,
                  self.ui.formLayoutWidget_4,
                  self.ui.formLayoutWidget_5]:
            w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            w.setMinimumHeight(150)
            right_col.addWidget(w, 1)

        right_widget = QWidget()
        right_widget.setLayout(right_col)
        right_widget.setMinimumWidth(220)
        right_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding) # type: ignore
        root.addWidget(right_widget)

        # ============================================================
        # Ctrl+Enter 发送消息
        # ============================================================
        self.shortcut_send = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.shortcut_send.activated.connect(self.on_send_chat)

        # 让输入框在回车（Enter 而非 Shift+Enter）时也能触发发送（可选）
        # 这里 Ctrl+Enter 作为主发送快捷键，普通 Enter 是换行，体验更自然

        # 对话历史
        self.messages = [
            {"role": "system", "content": "你是一个有用的AI助手。"}
        ]

    def on_send_chat(self):
        user_input = self.ui.plainTextEdit_ChatSend.toPlainText().strip()
        if not user_input:
            self.ui.plainTextEdit_AIChat.appendPlainText("\n[请先输入消息]\n")
            return

        # 显示用户消息
        self.messages.append({"role": "user", "content": user_input})
        self.ui.plainTextEdit_AIChat.appendPlainText(f"\n> You: {user_input}\n")

        # 清空输入框
        self.ui.plainTextEdit_ChatSend.clear()

        # 启动 AI 线程
        self.ai_thread = AIThread(self.messages.copy())
        self.ai_thread.reply_received.connect(self.on_ai_reply)
        self.ai_thread.error_occurred.connect(self.on_ai_error)
        self.ai_thread.start()

    def on_ai_reply(self, reply):
        self.messages.append({"role": "assistant", "content": reply})
        self.ui.plainTextEdit_AIChat.appendPlainText(f"AI: {reply}\n")

    def on_ai_error(self, err_msg):
        self.ui.plainTextEdit_AIChat.appendPlainText(f"\n[错误] {err_msg}\n")


if __name__ == "__main__":
    app = QApplication([])
    window = MyMainWindow()
    window.resize(1100, 800)    # 初始默认大小，放大后内部会自动适应
    window.show()
    app.exec()