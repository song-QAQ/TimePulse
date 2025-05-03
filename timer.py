from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QSpinBox, QTimeEdit, QLineEdit, QMessageBox,
                            QRadioButton)
from PyQt6.QtCore import Qt, QTimer, QTime, pyqtSignal
from datetime import datetime

class Timer(QWidget):
    """计时器核心类"""
    
    time_updated = pyqtSignal(str)
    timer_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = QTime(0, 0)
        self.elapsed_time = QTime(0, 0)
        self.is_running = False
        self.is_countdown = False
        self.target_seconds = 0
    
    def start(self, is_countdown=False, target_seconds=0):
        """开始计时"""
        self.is_countdown = is_countdown
        self.target_seconds = target_seconds
        
        if is_countdown:
            # 倒计时模式
            hours = target_seconds // 3600
            minutes = (target_seconds % 3600) // 60
            seconds = target_seconds % 60
            self.remaining_time = QTime(hours, minutes, seconds)
        else:
            # 正计时模式
            self.elapsed_time = QTime(0, 0)
        
        self.timer.start(1000)  # 每秒更新一次
        self.is_running = True
        self.update_display()
    
    def pause(self):
        """暂停计时"""
        if self.is_running:
            self.timer.stop()
            self.is_running = False
    
    def resume(self):
        """恢复计时"""
        if not self.is_running:
            self.timer.start(1000)
            self.is_running = True
    
    def stop(self):
        """停止计时"""
        self.timer.stop()
        self.is_running = False
        if self.is_countdown:
            self.remaining_time = QTime(0, 0)
        else:
            self.elapsed_time = QTime(0, 0)
        self.update_display()
    
    def update_timer(self):
        """更新计时器"""
        if self.is_countdown:
            # 倒计时模式
            if self.remaining_time > QTime(0, 0):
                self.remaining_time = self.remaining_time.addSecs(-1)
                self.update_display()
            else:
                self.timer.stop()
                self.is_running = False
                self.timer_finished.emit()
        else:
            # 正计时模式
            self.elapsed_time = self.elapsed_time.addSecs(1)
            self.update_display()
    
    def update_display(self):
        """更新显示"""
        if self.is_countdown:
            time_str = self.remaining_time.toString("hh:mm:ss")
        else:
            time_str = self.elapsed_time.toString("hh:mm:ss")
        
        self.time_updated.emit(time_str)
    
    def get_elapsed_seconds(self):
        """获取已经过秒数"""
        if self.is_countdown:
            return self.target_seconds - (self.remaining_time.hour() * 3600 + 
                                         self.remaining_time.minute() * 60 + 
                                         self.remaining_time.second())
        else:
            return self.elapsed_time.hour() * 3600 + self.elapsed_time.minute() * 60 + self.elapsed_time.second()
    
    def is_active(self):
        """计时器是否正在运行"""
        return self.is_running

class SimpleTimerWidget(QWidget):
    """简单计时器界面组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        self.is_countdown = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 时间输入区域
        time_input = QHBoxLayout()
        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        
        time_input.addWidget(QLabel("时:"))
        time_input.addWidget(self.hours_spin)
        time_input.addWidget(QLabel("分:"))
        time_input.addWidget(self.minutes_spin)
        time_input.addWidget(QLabel("秒:"))
        time_input.addWidget(self.seconds_spin)
        
        # 模式选择
        mode_layout = QHBoxLayout()
        self.countdown_radio = QRadioButton("倒计时")
        self.countdown_radio.setChecked(True)
        self.countdown_radio.toggled.connect(self.on_mode_changed)
        self.stopwatch_radio = QRadioButton("正计时")
        mode_layout.addWidget(self.countdown_radio)
        mode_layout.addWidget(self.stopwatch_radio)
        
        # 显示区域
        self.time_label = QLabel("00:00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.time_label.font()
        font.setPointSize(24)
        self.time_label.setFont(font)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_timer)
        self.pause_button = QPushButton("暂停")
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset_timer)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.reset_button)
        
        layout.addLayout(time_input)
        layout.addLayout(mode_layout)
        layout.addWidget(self.time_label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def on_mode_changed(self, checked):
        self.is_countdown = checked
        self.reset_timer()
        if self.is_countdown:
            self.hours_spin.setEnabled(True)
            self.minutes_spin.setEnabled(True)
            self.seconds_spin.setEnabled(True)
        else:
            self.hours_spin.setEnabled(False)
            self.minutes_spin.setEnabled(False)
            self.seconds_spin.setEnabled(False)

    def start_timer(self):
        if not self.timer.isActive():
            if self.is_countdown:
                self.remaining_time = (
                    self.hours_spin.value() * 3600 +
                    self.minutes_spin.value() * 60 +
                    self.seconds_spin.value()
                )
                if self.remaining_time <= 0:
                    return
            else:
                self.remaining_time = 0
            self.timer.start(1000)
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.reset_button.setEnabled(True)

    def pause_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        if self.is_countdown:
            self.remaining_time = (
                self.hours_spin.value() * 3600 +
                self.minutes_spin.value() * 60 +
                self.seconds_spin.value()
            )
        else:
            self.remaining_time = 0
        self.update_display()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(False)

    def update_timer(self):
        if self.is_countdown:
            if self.remaining_time > 0:
                self.remaining_time -= 1
            else:
                self.timer.stop()
                self.start_button.setEnabled(True)
                self.pause_button.setEnabled(False)
                QMessageBox.information(self, "提示", "倒计时结束！")
        else:
            self.remaining_time += 1
        self.update_display()

    def update_display(self):
        hours = self.remaining_time // 3600
        minutes = (self.remaining_time % 3600) // 60
        seconds = self.remaining_time % 60
        self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}") 