from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                               QPlainTextEdit, QWidget, QVBoxLayout,
                               QHBoxLayout, QToolButton, QLabel)
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QSize


# ========== 左侧栏：10个带彩色图标的菜单按钮 ==========
class MainMenuBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 固定宽度 = 屏幕宽度的 10%
        screen_width = QApplication.primaryScreen().availableGeometry().width()
        self.setFixedWidth(int(screen_width * 0.10))

        # 背景色
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2d42;
                border-right: 1px solid #3d405b;
            }
            QToolButton {
                color: #edf2f4;
                background-color: #3d405b;
                border: none;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
            }
            QToolButton:hover {
                background-color: #5c677d;
                color: #ffffff;
            }
            QToolButton:pressed {
                background-color: #ef8354;
            }
            QLabel#title {
                color: #ef8354;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 10px;
                border-bottom: 1px solid #3d405b;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(8)

        # 顶部标题
        title = QLabel("MENU")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter) # type: ignore
        layout.addWidget(title)

        # 10 个菜单项 (名称, 颜色)
        menu_items = [
            ("Home",       "#4ECDC4"),
            ("Weather",    "#FF6B6B"),
            ("AI Chat",    "#FFE66D"),
            ("MCP",        "#A8E6CF"),
            ("Tools",      "#B8B8FF"),
            ("Settings",   "#FFAAA5"),
            ("Logs",       "#FFD3B6"),
            ("Database",   "#95E1D3"),
            ("Network",    "#FCBAD3"),
            ("About",      "#F38181"),
        ]

        # 用函数生成彩色图标
        def make_icon(color_hex, size=24):
            pix = QPixmap(size, size)
            pix.fill(Qt.transparent) # pyright: ignore[reportAttributeAccessIssue]
            p = QPainter(pix)
            p.setRenderHint(QPainter.Antialiasing) # type: ignore
            p.setBrush(QColor(color_hex))
            p.setPen(Qt.NoPen) # type: ignore
            p.drawEllipse(1, 1, size - 2, size - 2)
            p.setPen(QColor("#2b2d42"))
            f = QFont()
            f.setBold(True)
            f.setPointSize(9)
            p.setFont(f)
            p.drawText(pix.rect(), Qt.AlignCenter, "●") # type: ignore
            p.end()
            return QIcon(pix)

        # 生成10个按钮
        self.buttons = []
        for name, color in menu_items:
            btn = QToolButton()
            btn.setText(name)
            btn.setIcon(make_icon(color))
            btn.setIconSize(QSize(20, 20))
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon) # type: ignore
            btn.setMinimumHeight(36)
            btn.setFixedWidth(int(screen_width * 0.10) - 16)
            self.buttons.append(btn)
            layout.addWidget(btn)

        # 底部空白占位，让按钮靠上排列
        layout.addStretch()


# ========== 主窗口 ==========
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PERCY SOFTWARE')

        # ===== 顶部菜单栏 =====
        menu_file = self.menuBar().addMenu('File')
        menu_file.addAction('Open')
        menu_file.addAction('Save')
        action_exit = menu_file.addAction('Exit')
        action_exit.triggered.connect(self.close)

        menu_help = self.menuBar().addMenu('Help')
        menu_help.addAction('About')

        # ===== 中心容器：水平布局 = 左侧栏 + 右侧主区 =====
        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # --- 左侧栏 ---
        self.sidebar = MainMenuBar()
        root.addWidget(self.sidebar)

        # --- 右侧主区 ---
        right_area = QWidget()
        right_layout = QVBoxLayout(right_area)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(10)
        root.addWidget(right_area, 1)  # stretch=1 占满剩余空间

        # 文本编辑器（两个水平并排居中）
        screen_geo = self.screen().availableGeometry()
        editor_width = int(screen_geo.width() * 0.5 / 2) - 20  # 每块约屏幕 1/4

        textEditAIChat = QPlainTextEdit()
        textEditAIChat.setPlaceholderText("AI Chat")
        textEditAIChat.setFixedWidth(editor_width)

        textEditMCP = QPlainTextEdit()
        textEditMCP.setPlaceholderText("MCP")
        textEditMCP.setFixedWidth(editor_width)

        text_hlayout = QHBoxLayout()
        text_hlayout.addStretch()
        text_hlayout.addWidget(textEditAIChat)
        text_hlayout.addWidget(textEditMCP)
        text_hlayout.addStretch()
        right_layout.addLayout(text_hlayout)
        text_hlayout.addStretch()

        textEditCMD = QPlainTextEdit()
        textEditCMD.setPlaceholderText("CMD")
        textEditCMD.setFixedWidth(editor_width)
        textEditCMD.setFixedHeight(100)
        textCMD_vlayout = QVBoxLayout()
        textCMD_vlayout.addWidget(textEditCMD)
        textCMD_vlayout.addStretch()
        right_layout.addLayout(textCMD_vlayout)


        # 底部3个按钮
        for btn_text in ['CHAT SEND', 'CLEAR', 'EXIT']:
            btn = QPushButton(btn_text)
            btn.setFixedSize(120, 32)
            if btn_text == 'EXIT':
                btn.clicked.connect(self.close)
            row = QHBoxLayout()
            row.addStretch()
            row.addWidget(btn)
            row.addStretch()
            right_layout.addLayout(row)


app = QApplication([])
window = MainWindow()
window.showMaximized()
app.exec()