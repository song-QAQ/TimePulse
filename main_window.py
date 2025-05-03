from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QTabWidget, QMessageBox,
                             QFrame, QSystemTrayIcon, QMenu, QDialog, QFormLayout,
                             QLineEdit, QTextEdit, QComboBox, QSpinBox, QDateEdit,
                             QColorDialog, QCheckBox)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QIcon, QAction, QColor
import os
from database import Database
from timer_widget import TimerWidget
from time_tracker_widget import TimeTrackerWidget
from journal_widget import JournalWidget
from task_widget import TaskWidget
from export_widget import ExportWidget

class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 基本设置
        basic_group = QFrame()
        basic_group.setFrameShape(QFrame.Shape.StyledPanel)
        basic_layout = QFormLayout(basic_group)
        
        # 启动时自动开始计时
        self.auto_start_check = QCheckBox("启动时自动开始计时")
        basic_layout.addRow("", self.auto_start_check)
        
        # 最小化到系统托盘
        self.minimize_to_tray_check = QCheckBox("最小化到系统托盘")
        basic_layout.addRow("", self.minimize_to_tray_check)
        
        # 开机自启动
        self.startup_check = QCheckBox("开机自启动")
        basic_layout.addRow("", self.startup_check)
        
        layout.addWidget(basic_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def get_settings(self):
        """获取设置"""
        return {
            'auto_start': self.auto_start_check.isChecked(),
            'minimize_to_tray': self.minimize_to_tray_check.isChecked(),
            'startup': self.startup_check.isChecked()
        }
    
    def set_settings(self, settings):
        """设置设置"""
        self.auto_start_check.setChecked(settings.get('auto_start', False))
        self.minimize_to_tray_check.setChecked(settings.get('minimize_to_tray', False))
        self.startup_check.setChecked(settings.get('startup', False))

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        self.init_menu()
        self.init_tray()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("时间管理工具")
        self.setMinimumSize(800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 计时器标签页
        self.timer_widget = TimerWidget()
        self.tab_widget.addTab(self.timer_widget, "计时器")
        
        # 时间记录标签页
        self.time_tracker_widget = TimeTrackerWidget(self.db)
        self.tab_widget.addTab(self.time_tracker_widget, "时间记录")
        
        # 日记标签页
        self.journal_widget = JournalWidget(self.db)
        self.tab_widget.addTab(self.journal_widget, "日记")
        
        # 任务标签页
        self.task_widget = TaskWidget(self.db)
        self.tab_widget.addTab(self.task_widget, "任务")
        
        # 数据导出标签页
        self.export_widget = ExportWidget(self.db)
        self.tab_widget.addTab(self.export_widget, "数据导出")
        
        main_layout.addWidget(self.tab_widget)
    
    def init_menu(self):
        """初始化菜单"""
        # 文件菜单
        file_menu = self.menuBar().addMenu("文件")
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = self.menuBar().addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join("icons", "app.png")))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        show_action = QAction("显示", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("隐藏", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def load_settings(self):
        """加载设置"""
        # TODO: 从配置文件加载设置
        self.settings = {
            'auto_start': False,
            'minimize_to_tray': True,
            'startup': False
        }
        
        # 应用设置
        if self.settings['auto_start']:
            self.timer_widget.start()
    
    def save_settings(self):
        """保存设置"""
        # TODO: 保存设置到配置文件
        pass
    
    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.set_settings(self.settings)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()
            self.save_settings()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于",
            "时间管理工具 v1.0\n\n"
            "一个功能强大的时间管理工具，帮助你更好地管理时间。\n\n"
            "功能特点：\n"
            "- 计时器\n"
            "- 时间记录\n"
            "- 日记\n"
            "- 任务管理\n"
            "- 数据导出\n\n"
            "作者：Your Name\n"
            "版权所有 © 2024"
        )
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.settings['minimize_to_tray']:
            event.ignore()
            self.hide()
        else:
            self.db.close()
            event.accept()
    
    def changeEvent(self, event):
        """窗口状态改变事件处理"""
        if event.type() == Qt.WindowType.WindowStateChange:
            if self.isMinimized() and self.settings['minimize_to_tray']:
                event.ignore()
                self.hide()
                self.tray_icon.showMessage(
                    "时间管理工具",
                    "应用程序已最小化到系统托盘",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                ) 