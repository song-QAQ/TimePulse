import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTabWidget, QPushButton, QLabel)
from PyQt6.QtCore import Qt
from database import Database
from timer_widget import TimerWidget
from time_records import TimeRecordsWidget
from journal_widget import JournalWidget
from task_widget import TaskWidget
from export_widget import ExportWidget

class TimeManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle('时间管理器')
        self.setGeometry(100, 100, 800, 600)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建标签页
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # 添加计时器标签页
        tab_widget.addTab(TimerWidget(), "计时器")

        # 添加时间记录标签页
        tab_widget.addTab(TimeRecordsWidget(self.db), "时间记录")

        # 添加日记标签页
        tab_widget.addTab(JournalWidget(self.db), "日记")

        # 添加任务标签页
        tab_widget.addTab(TaskWidget(self.db), "任务")

        # 添加数据导出标签页
        tab_widget.addTab(ExportWidget(self.db), "数据导出")

def main():
    """应用程序入口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("时间管理工具")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Company(暂无)")
    app.setOrganizationDomain("company.com(哈哈哈还是没)")
    
    # 创建并显示主窗口
    window = TimeManagerApp()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 