from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QLineEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit,
                             QFrame, QDialog, QFormLayout, QColorDialog)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from datetime import datetime, timedelta
import os

class CategoryDialog(QDialog):
    """类别编辑对话框"""
    
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.category = category
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑类别")
        self.setMinimumWidth(300)
        
        layout = QFormLayout(self)
        
        # 类别名称
        self.name_edit = QLineEdit()
        if self.category:
            self.name_edit.setText(self.category['name'])
        layout.addRow("名称:", self.name_edit)
        
        # 类别颜色
        color_layout = QHBoxLayout()
        self.color_button = QPushButton()
        self.color_button.setFixedSize(50, 25)
        self.color = self.category['color'] if self.category else "#3498db"
        self._update_color_button()
        self.color_button.clicked.connect(self._on_color_clicked)
        
        color_layout.addWidget(self.color_button)
        color_layout.addStretch()
        layout.addRow("颜色:", color_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
    
    def _update_color_button(self):
        """更新颜色按钮"""
        self.color_button.setStyleSheet(f"background-color: {self.color};")
    
    def _on_color_clicked(self):
        """颜色按钮点击处理"""
        color = QColorDialog.getColor(QColor(self.color), self, "选择颜色")
        if color.isValid():
            self.color = color.name()
            self._update_color_button()
    
    def get_category_data(self):
        """获取类别数据"""
        return {
            'name': self.name_edit.text().strip(),
            'color': self.color
        }

class TimeTrackerWidget(QWidget):
    """时间追踪界面组件"""
    
    # 信号定义
    time_entry_started = pyqtSignal(int, str)  # 开始时间记录信号
    time_entry_ended = pyqtSignal(int)         # 结束时间记录信号
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.active_entry_id = None
        self.active_category_id = None
        
        self.init_ui()
        self.load_categories()
        self.load_time_entries()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 当前活动
        current_activity_layout = QHBoxLayout()
        current_activity_label = QLabel("当前活动:")
        self.current_activity_label = QLabel("无")
        self.current_activity_label.setStyleSheet("font-weight: bold;")
        
        current_activity_layout.addWidget(current_activity_label)
        current_activity_layout.addWidget(self.current_activity_label)
        current_activity_layout.addStretch()
        
        self.stop_button = QPushButton("停止")
        self.stop_button.setIcon(QIcon(os.path.join("icons", "stop.png")))
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)
        current_activity_layout.addWidget(self.stop_button)
        
        main_layout.addLayout(current_activity_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # 开始新活动
        new_activity_layout = QHBoxLayout()
        new_activity_label = QLabel("开始新活动:")
        
        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(150)
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("活动描述（可选）")
        
        self.start_button = QPushButton("开始")
        self.start_button.setIcon(QIcon(os.path.join("icons", "play.png")))
        self.start_button.clicked.connect(self._on_start_clicked)
        
        new_activity_layout.addWidget(new_activity_label)
        new_activity_layout.addWidget(self.category_combo)
        new_activity_layout.addWidget(self.description_edit)
        new_activity_layout.addWidget(self.start_button)
        
        main_layout.addLayout(new_activity_layout)
        
        # 类别管理
        category_layout = QHBoxLayout()
        category_label = QLabel("类别管理:")
        
        self.add_category_button = QPushButton("添加")
        self.add_category_button.setIcon(QIcon(os.path.join("icons", "add.png")))
        self.add_category_button.clicked.connect(self._on_add_category_clicked)
        
        self.edit_category_button = QPushButton("编辑")
        self.edit_category_button.setIcon(QIcon(os.path.join("icons", "edit.png")))
        self.edit_category_button.clicked.connect(self._on_edit_category_clicked)
        
        self.delete_category_button = QPushButton("删除")
        self.delete_category_button.setIcon(QIcon(os.path.join("icons", "delete.png")))
        self.delete_category_button.clicked.connect(self._on_delete_category_clicked)
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.add_category_button)
        category_layout.addWidget(self.edit_category_button)
        category_layout.addWidget(self.delete_category_button)
        category_layout.addStretch()
        
        main_layout.addLayout(category_layout)
        
        # 时间记录表格
        table_label = QLabel("时间记录:")
        main_layout.addWidget(table_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["类别", "开始时间", "结束时间", "持续时间", "描述"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.table)
        
        # 日期筛选
        filter_layout = QHBoxLayout()
        filter_label = QLabel("日期筛选:")
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        
        self.filter_button = QPushButton("筛选")
        self.filter_button.clicked.connect(self._on_filter_clicked)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("至"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addWidget(self.filter_button)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
    
    def load_categories(self):
        """加载类别"""
        self.category_combo.clear()
        categories = self.db.get_categories()
        
        for category in categories:
            self.category_combo.addItem(category['name'], category['id'])
    
    def load_time_entries(self, start_date=None, end_date=None):
        """加载时间记录"""
        if not start_date:
            start_date = self.start_date_edit.date().toPyDate().strftime("%Y-%m-%d")
        if not end_date:
            end_date = self.end_date_edit.date().toPyDate().strftime("%Y-%m-%d")
        
        entries = self.db.get_time_entries(start_date, end_date)
        
        self.table.setRowCount(0)
        for entry in entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 类别
            category_item = QTableWidgetItem(entry['category_name'])
            category_item.setBackground(QColor(entry['category_color']))
            self.table.setItem(row, 0, category_item)
            
            # 开始时间
            start_time = datetime.strptime(entry['start_time'], "%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 1, QTableWidgetItem(start_time.strftime("%Y-%m-%d %H:%M:%S")))
            
            # 结束时间
            if entry['end_time']:
                end_time = datetime.strptime(entry['end_time'], "%Y-%m-%d %H:%M:%S")
                self.table.setItem(row, 2, QTableWidgetItem(end_time.strftime("%Y-%m-%d %H:%M:%S")))
                
                # 持续时间
                duration = (end_time - start_time).total_seconds()
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                self.table.setItem(row, 3, QTableWidgetItem(f"{hours:02d}:{minutes:02d}"))
            else:
                self.table.setItem(row, 2, QTableWidgetItem("进行中"))
                self.table.setItem(row, 3, QTableWidgetItem("--:--"))
            
            # 描述
            self.table.setItem(row, 4, QTableWidgetItem(entry['description'] or ""))
    
    def _on_start_clicked(self):
        """开始按钮点击处理"""
        if self.active_entry_id:
            QMessageBox.warning(self, "警告", "已有活动正在进行中")
            return
        
        category_id = self.category_combo.currentData()
        description = self.description_edit.text().strip()
        
        entry_id = self.db.start_time_entry(category_id, description)
        if entry_id:
            self.active_entry_id = entry_id
            self.active_category_id = category_id
            self.current_activity_label.setText(f"{self.category_combo.currentText()}: {description or '无描述'}")
            self.stop_button.setEnabled(True)
            self.start_button.setEnabled(False)
            self.description_edit.clear()
            
            self.time_entry_started.emit(category_id, description)
            self.load_time_entries()
    
    def _on_stop_clicked(self):
        """停止按钮点击处理"""
        if not self.active_entry_id:
            return
        
        self.db.end_time_entry(self.active_entry_id)
        self.time_entry_ended.emit(self.active_entry_id)
        
        self.active_entry_id = None
        self.active_category_id = None
        self.current_activity_label.setText("无")
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)
        
        self.load_time_entries()
    
    def _on_add_category_clicked(self):
        """添加类别按钮点击处理"""
        dialog = CategoryDialog(self)
        if dialog.exec():
            category_data = dialog.get_category_data()
            if not category_data['name']:
                QMessageBox.warning(self, "警告", "类别名称不能为空")
                return
            
            if self.db.add_category(category_data['name'], category_data['color']):
                self.load_categories()
            else:
                QMessageBox.warning(self, "警告", "类别名称已存在")
    
    def _on_edit_category_clicked(self):
        """编辑类别按钮点击处理"""
        category_id = self.category_combo.currentData()
        if not category_id:
            return
        
        categories = self.db.get_categories()
        category = next((c for c in categories if c['id'] == category_id), None)
        if not category:
            return
        
        dialog = CategoryDialog(self, category)
        if dialog.exec():
            category_data = dialog.get_category_data()
            if not category_data['name']:
                QMessageBox.warning(self, "警告", "类别名称不能为空")
                return
            
            self.db.update_category(category_id, category_data['name'], category_data['color'])
            self.load_categories()
    
    def _on_delete_category_clicked(self):
        """删除类别按钮点击处理"""
        category_id = self.category_combo.currentData()
        if not category_id:
            return
        
        reply = QMessageBox.question(
            self, "确认", "确定要删除这个类别吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_category(category_id)
            self.load_categories()
    
    def _on_filter_clicked(self):
        """筛选按钮点击处理"""
        self.load_time_entries()
    
    def get_active_entry(self):
        """获取当前活动的时间记录"""
        if not self.active_entry_id:
            return None
        
        entries = self.db.get_time_entries()
        return next((e for e in entries if e['id'] == self.active_entry_id), None) 