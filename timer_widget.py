from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QSpinBox, QComboBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from timer import SimpleTimerWidget

class TimerWidget(QWidget):
    """计时器界面组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = SimpleTimerWidget(self)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 添加 SimpleTimerWidget
        main_layout.addWidget(self.timer)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        main_layout.addStretch()
    
    def get_elapsed_seconds(self):
        """获取已经过秒数"""
        return 0  # SimpleTimerWidget 不支持此功能
    
    def is_active(self):
        """计时器是否正在运行"""
        return self.timer.is_running 