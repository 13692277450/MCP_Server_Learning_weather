# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QMainWindow, QMenu,
    QMenuBar, QPlainTextEdit, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(917, 848)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditSelectAll))
        MainWindow.setWindowIcon(icon)
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionAbout_2 = QAction(MainWindow)
        self.actionAbout_2.setObjectName(u"actionAbout_2")
        self.actionShow_Logs = QAction(MainWindow)
        self.actionShow_Logs.setObjectName(u"actionShow_Logs")
        self.actionShow_run_logs = QAction(MainWindow)
        self.actionShow_run_logs.setObjectName(u"actionShow_run_logs")
        self.actionAI_LLM_Settings = QAction(MainWindow)
        self.actionAI_LLM_Settings.setObjectName(u"actionAI_LLM_Settings")
        self.actionMCS = QAction(MainWindow)
        self.actionMCS.setObjectName(u"actionMCS")
        self.actionSkills = QAction(MainWindow)
        self.actionSkills.setObjectName(u"actionSkills")
        self.actionApplication_Settings = QAction(MainWindow)
        self.actionApplication_Settings.setObjectName(u"actionApplication_Settings")
        self.actionLoad_AI_LLM_Settings = QAction(MainWindow)
        self.actionLoad_AI_LLM_Settings.setObjectName(u"actionLoad_AI_LLM_Settings")
        self.actionLoad_MCP_Settings = QAction(MainWindow)
        self.actionLoad_MCP_Settings.setObjectName(u"actionLoad_MCP_Settings")
        self.actionLoad_Skills_Settings = QAction(MainWindow)
        self.actionLoad_Skills_Settings.setObjectName(u"actionLoad_Skills_Settings")
        self.actionLoad_Application_Settings = QAction(MainWindow)
        self.actionLoad_Application_Settings.setObjectName(u"actionLoad_Application_Settings")
        self.actionSava_all_settings = QAction(MainWindow)
        self.actionSava_all_settings.setObjectName(u"actionSava_all_settings")
        self.actionEXIT = QAction(MainWindow)
        self.actionEXIT.setObjectName(u"actionEXIT")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.formLayout_MenuBar = QFormLayout()
        self.formLayout_MenuBar.setObjectName(u"formLayout_MenuBar")
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.pushButton_2)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        self.pushButton_3.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.pushButton_3)

        self.pushButton_4 = QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName(u"pushButton_4")
        self.pushButton_4.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.pushButton_4)

        self.pushButton_5 = QPushButton(self.centralwidget)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.pushButton_5)

        self.pushButton_7 = QPushButton(self.centralwidget)
        self.pushButton_7.setObjectName(u"pushButton_7")
        self.pushButton_7.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.pushButton_7)

        self.pushButton_8 = QPushButton(self.centralwidget)
        self.pushButton_8.setObjectName(u"pushButton_8")
        self.pushButton_8.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(5, QFormLayout.ItemRole.SpanningRole, self.pushButton_8)

        self.pushButton_6 = QPushButton(self.centralwidget)
        self.pushButton_6.setObjectName(u"pushButton_6")
        self.pushButton_6.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(6, QFormLayout.ItemRole.SpanningRole, self.pushButton_6)

        self.pushButton_9 = QPushButton(self.centralwidget)
        self.pushButton_9.setObjectName(u"pushButton_9")
        self.pushButton_9.setMinimumSize(QSize(0, 40))

        self.formLayout_MenuBar.setWidget(7, QFormLayout.ItemRole.SpanningRole, self.pushButton_9)


        self.gridLayout.addLayout(self.formLayout_MenuBar, 1, 0, 4, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 5, 0, 1, 1)

        self.formLayout_ChatSend = QFormLayout()
        self.formLayout_ChatSend.setObjectName(u"formLayout_ChatSend")
        self.plainTextEdit_ChatSend = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit_ChatSend.setObjectName(u"plainTextEdit_ChatSend")
        self.plainTextEdit_ChatSend.setLineWidth(2)

        self.formLayout_ChatSend.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.plainTextEdit_ChatSend)


        self.gridLayout.addLayout(self.formLayout_ChatSend, 4, 1, 1, 1)

        self.formLayout_MCP = QFormLayout()
        self.formLayout_MCP.setObjectName(u"formLayout_MCP")
        self.formLayout_MCP.setHorizontalSpacing(6)
        self.formLayout_MCP.setVerticalSpacing(6)
        self.formLayout_MCP.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_MCP = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit_MCP.setObjectName(u"plainTextEdit_MCP")
        self.plainTextEdit_MCP.setLineWidth(2)

        self.formLayout_MCP.setWidget(0, QFormLayout.ItemRole.LabelRole, self.plainTextEdit_MCP)


        self.gridLayout.addLayout(self.formLayout_MCP, 1, 3, 1, 1)

        self.formLayout_AILLM = QFormLayout()
        self.formLayout_AILLM.setObjectName(u"formLayout_AILLM")
        self.plainTextEdit_infor = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit_infor.setObjectName(u"plainTextEdit_infor")
        self.plainTextEdit_infor.setMaximumSize(QSize(16777215, 192))
        self.plainTextEdit_infor.setLineWidth(2)

        self.formLayout_AILLM.setWidget(0, QFormLayout.ItemRole.LabelRole, self.plainTextEdit_infor)


        self.gridLayout.addLayout(self.formLayout_AILLM, 3, 3, 2, 1)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        font = QFont()
        font.setBold(True)
        self.label_3.setFont(font)

        self.horizontalLayout.addWidget(self.label_3)

        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.horizontalLayout.addWidget(self.label_2)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.horizontalLayout.addWidget(self.label)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)


        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 4)

        self.formLayout_AIOut = QFormLayout()
        self.formLayout_AIOut.setObjectName(u"formLayout_AIOut")
        self.formLayout_AIOut.setHorizontalSpacing(6)
        self.formLayout_AIOut.setVerticalSpacing(6)
        self.formLayout_AIOut.setContentsMargins(0, 0, 0, 0)
        self.plainTextEdit_AIChat = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit_AIChat.setObjectName(u"plainTextEdit_AIChat")
        self.plainTextEdit_AIChat.setMinimumSize(QSize(409, 0))
        self.plainTextEdit_AIChat.setMaximumSize(QSize(16777215, 16777215))
        self.plainTextEdit_AIChat.setLineWidth(2)

        self.formLayout_AIOut.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.plainTextEdit_AIChat)


        self.gridLayout.addLayout(self.formLayout_AIOut, 1, 1, 3, 1)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.pushButton_ConnTest = QPushButton(self.centralwidget)
        self.pushButton_ConnTest.setObjectName(u"pushButton_ConnTest")
        self.pushButton_ConnTest.setMinimumSize(QSize(150, 30))
        self.pushButton_ConnTest.setMaximumSize(QSize(150, 30))
        self.pushButton_ConnTest.setAutoFillBackground(False)
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSend))
        self.pushButton_ConnTest.setIcon(icon1)
        self.pushButton_ConnTest.setCheckable(False)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.pushButton_ConnTest)


        self.gridLayout.addLayout(self.formLayout_2, 5, 3, 1, 1)

        self.formLayout_Skills = QFormLayout()
        self.formLayout_Skills.setObjectName(u"formLayout_Skills")
        self.plainTextEdit_Skills = QPlainTextEdit(self.centralwidget)
        self.plainTextEdit_Skills.setObjectName(u"plainTextEdit_Skills")
        self.plainTextEdit_Skills.setLineWidth(2)

        self.formLayout_Skills.setWidget(0, QFormLayout.ItemRole.LabelRole, self.plainTextEdit_Skills)


        self.gridLayout.addLayout(self.formLayout_Skills, 2, 3, 1, 1)

        self.formLayout_5 = QFormLayout()
        self.formLayout_5.setObjectName(u"formLayout_5")

        self.gridLayout.addLayout(self.formLayout_5, 5, 2, 1, 1)

        self.formLayout_6 = QFormLayout()
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMinimumSize(QSize(150, 30))
        self.pushButton.setMaximumSize(QSize(150, 30))
        self.pushButton.setIcon(icon1)

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.LabelRole, self.pushButton)

        self.pushButton_ClearAIChat = QPushButton(self.centralwidget)
        self.pushButton_ClearAIChat.setObjectName(u"pushButton_ClearAIChat")
        self.pushButton_ClearAIChat.setMinimumSize(QSize(150, 30))
        self.pushButton_ClearAIChat.setMaximumSize(QSize(150, 30))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditClear))
        self.pushButton_ClearAIChat.setIcon(icon2)

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.FieldRole, self.pushButton_ClearAIChat)


        self.gridLayout.addLayout(self.formLayout_6, 5, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 917, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuLogs = QMenu(self.menubar)
        self.menuLogs.setObjectName(u"menuLogs")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuLogs.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionLoad_AI_LLM_Settings)
        self.menuFile.addAction(self.actionLoad_MCP_Settings)
        self.menuFile.addAction(self.actionLoad_Skills_Settings)
        self.menuFile.addAction(self.actionLoad_Application_Settings)
        self.menuFile.addAction(self.actionSava_all_settings)
        self.menuFile.addAction(self.actionEXIT)
        self.menuSettings.addAction(self.actionAI_LLM_Settings)
        self.menuSettings.addAction(self.actionMCS)
        self.menuSettings.addAction(self.actionSkills)
        self.menuSettings.addAction(self.actionApplication_Settings)
        self.menuLogs.addAction(self.actionShow_Logs)
        self.menuLogs.addAction(self.actionShow_run_logs)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAbout_2)
        self.menuHelp.addSeparator()

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"New version?", None))
        self.actionAbout_2.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionShow_Logs.setText(QCoreApplication.translate("MainWindow", u"Show Logs", None))
        self.actionShow_run_logs.setText(QCoreApplication.translate("MainWindow", u"Show run logs", None))
        self.actionAI_LLM_Settings.setText(QCoreApplication.translate("MainWindow", u"AI LLM Settings", None))
        self.actionMCS.setText(QCoreApplication.translate("MainWindow", u"MCP Settings", None))
        self.actionSkills.setText(QCoreApplication.translate("MainWindow", u"Skills Settings", None))
        self.actionApplication_Settings.setText(QCoreApplication.translate("MainWindow", u"Application Settings", None))
        self.actionLoad_AI_LLM_Settings.setText(QCoreApplication.translate("MainWindow", u"Load AI LLM Settings", None))
        self.actionLoad_MCP_Settings.setText(QCoreApplication.translate("MainWindow", u"Load MCP Settings", None))
        self.actionLoad_Skills_Settings.setText(QCoreApplication.translate("MainWindow", u"Load Skills Settings", None))
        self.actionLoad_Application_Settings.setText(QCoreApplication.translate("MainWindow", u"Load Application Settings", None))
        self.actionSava_all_settings.setText(QCoreApplication.translate("MainWindow", u"Sava all settings", None))
        self.actionEXIT.setText(QCoreApplication.translate("MainWindow", u"EXIT", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_7.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.pushButton_9.setText(QCoreApplication.translate("MainWindow", u"PushButton", None))
        self.plainTextEdit_MCP.setPlainText(QCoreApplication.translate("MainWindow", u"MCP INFO", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"\U0001f341MENU", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"\U0001f978AI CHAT", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\U0001f4d2MCP SKILLS SYSTEM      ", None))
        self.plainTextEdit_AIChat.setPlainText("")
        self.pushButton_ConnTest.setText(QCoreApplication.translate("MainWindow", u"TEST CONNECTION", None))
        self.plainTextEdit_Skills.setPlainText(QCoreApplication.translate("MainWindow", u"SKILLS INFO", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u" CHAT SEND", None))
        self.pushButton_ClearAIChat.setText(QCoreApplication.translate("MainWindow", u"CLEAR CHAT", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuLogs.setTitle(QCoreApplication.translate("MainWindow", u"Logs", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
    # retranslateUi

