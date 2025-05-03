from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDateEdit, QTimeEdit, QLineEdit,
                             QMessageBox, QHeaderView, QFrame, QDialog,
                             QFormLayout, QSpinBox, QColorDialog)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
import os
from datetime import datetime, timedelta

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

class TimeRecordDialog(QDialog):
    """添加/编辑时间记录对话框"""
    
    def __init__(self, parent=None, record=None, categories=None):
        super().__init__(parent)
        self.record = record
        self.categories = categories or []
        self.init_ui()
        self.load_categories()
        
        if record:
            self.setWindowTitle("编辑时间记录")
            self._load_record()
        else:
            self.setWindowTitle("添加时间记录")
    
    def init_ui(self):
        """初始化UI"""
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # 类别
        self.category_combo = QComboBox()
        layout.addRow("类别:", self.category_combo)
        
        # 日期
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.record:
            self.date_edit.setDate(QDate.fromString(self.record['start_time'].split()[0], "yyyy-MM-dd"))
        else:
            self.date_edit.setDate(QDate.currentDate())
        layout.addRow("日期:", self.date_edit)
        
        # 开始时间
        self.start_time_edit = QTimeEdit()
        if self.record:
            self.start_time_edit.setTime(QTime.fromString(self.record['start_time'].split()[1], "HH:mm:ss"))
        else:
            self.start_time_edit.setTime(QTime.currentTime())
        layout.addRow("开始时间:", self.start_time_edit)
        
        # 结束时间
        self.end_time_edit = QTimeEdit()
        if self.record and self.record['end_time']:
            self.end_time_edit.setTime(QTime.fromString(self.record['end_time'].split()[1], "HH:mm:ss"))
        else:
            self.end_time_edit.setTime(QTime.currentTime())
        layout.addRow("结束时间:", self.end_time_edit)
        
        # 描述
        self.description_edit = QLineEdit()
        if self.record:
            self.description_edit.setText(self.record['description'] or "")
        layout.addRow("描述:", self.description_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addRow("", button_layout)
        
        # 加载类别列表
        self.load_categories()
        
        # 如果是编辑模式，设置当前类别
        if self.record:
            index = self.category_combo.findData(self.record['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
    
    def load_categories(self):
        """加载类别列表"""
        self.category_combo.clear()
        if not self.categories:
            return
            
        for category in self.categories:
            self.category_combo.addItem(category['name'], category['id'])
            
        # 如果没有选择类别，默认选择第一个
        if self.category_combo.count() > 0 and not self.record:
            self.category_combo.setCurrentIndex(0)
    
    def _load_record(self):
        """加载记录数据"""
        self.category_combo.setCurrentIndex(self.category_combo.findData(self.record['category_id']))
        self.date_edit.setDate(QDate.fromString(self.record['start_time'].split()[0], "yyyy-MM-dd"))
        self.start_time_edit.setTime(QTime.fromString(self.record['start_time'].split()[1], "HH:mm:ss"))
        self.end_time_edit.setTime(QTime.fromString(self.record['end_time'].split()[1], "HH:mm:ss"))
        self.description_edit.setText(self.record['description'] or "")
    
    def get_record_data(self):
        """获取记录数据"""
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        start_time = f"{date_str} {self.start_time_edit.time().toString('HH:mm:ss')}"
        end_time = f"{date_str} {self.end_time_edit.time().toString('HH:mm:ss')}"
        
        return {
            'category_id': self.category_combo.currentData(),
            'start_time': start_time,
            'end_time': end_time,
            'description': self.description_edit.text().strip()
        }

class TimeRecordsWidget(QWidget):
    """时间记录界面组件"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.load_categories()
        self.load_records() # Initial load uses filters
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和按钮
        header_layout = QHBoxLayout()
        title_label = QLabel("时间记录")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        self.add_button = QPushButton("新建")
        self.add_button.setIcon(QIcon(os.path.join("icons", "add.png")))
        self.add_button.clicked.connect(self._on_add_clicked)
        
        self.edit_button = QPushButton("编辑")
        self.edit_button.setIcon(QIcon(os.path.join("icons", "edit.png")))
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.setIcon(QIcon(os.path.join("icons", "delete.png")))
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.delete_button.setEnabled(False)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(header_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # 筛选选项
        filter_layout = QHBoxLayout()
        
        # 日期范围
        date_label = QLabel("日期范围:")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        
        # 类别筛选
        category_label = QLabel("类别:")
        self.category_filter = QComboBox()
        self.category_filter.addItem("全部")
        
        # 筛选按钮
        self.filter_button = QPushButton("筛选")
        self.filter_button.clicked.connect(self._on_filter_clicked)
        
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("至"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addWidget(category_label)
        filter_layout.addWidget(self.category_filter)
        filter_layout.addWidget(self.filter_button)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # 时间记录表格
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
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        main_layout.addWidget(self.table)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.total_time_label = QLabel("总时间: 0小时0分钟")
        self.category_time_label = QLabel("类别时间: --")
        
        stats_layout.addWidget(self.total_time_label)
        stats_layout.addWidget(self.category_time_label)
        stats_layout.addStretch()
        
        main_layout.addLayout(stats_layout)
    
    def load_categories(self):
        """加载类别列表"""
        self.category_filter.clear()
        self.category_filter.addItem("全部")
        
        categories = self.db.get_categories()
        for category in categories:
            self.category_filter.addItem(category['name'], category['id'])
    
    def load_records(self, refresh_all=False):
        """加载时间记录"""
        start_date = None
        end_date = None
        category_id = None

        if not refresh_all:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
            category_id = self.category_filter.currentData()
            # Ensure full day range for filtering
            start_datetime_str = start_date + " 00:00:00"
            end_datetime_str = end_date + " 23:59:59"
            records = self.db.get_time_entries(start_datetime_str, end_datetime_str, category_id)
        else:
            # Fetch all records when refresh_all is True
            records = self.db.get_time_entries()

        self.table.setRowCount(0)
        total_seconds = 0
        category_times = {}
        
        for record in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 类别
            category_item = QTableWidgetItem(record['category_name'])
            # 处理category_color为None的情况
            if record['category_color']:
                category_item.setBackground(QColor(record['category_color']))
            else:
                # 使用默认颜色
                category_item.setBackground(QColor("#3498db"))
            category_item.setData(Qt.ItemDataRole.UserRole, record['id'])  # 存储记录ID
            self.table.setItem(row, 0, category_item)
            
            # 开始时间
            start_time = datetime.strptime(record['start_time'], "%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 1, QTableWidgetItem(start_time.strftime("%Y-%m-%d %H:%M:%S")))
            
            # 结束时间
            if record['end_time']:
                end_time = datetime.strptime(record['end_time'], "%Y-%m-%d %H:%M:%S")
                self.table.setItem(row, 2, QTableWidgetItem(end_time.strftime("%Y-%m-%d %H:%M:%S")))
                
                # 持续时间
                duration = (end_time - start_time).total_seconds()
                total_seconds += duration
                
                # 更新类别时间
                category_name = record['category_name']
                if category_name in category_times:
                    category_times[category_name] += duration
                else:
                    category_times[category_name] = duration
                
                hours = int(duration // 3600)
                minutes = int((duration % 3600) // 60)
                self.table.setItem(row, 3, QTableWidgetItem(f"{hours:02d}:{minutes:02d}"))
            else:
                self.table.setItem(row, 2, QTableWidgetItem("进行中"))
                self.table.setItem(row, 3, QTableWidgetItem("--:--"))
            
            # 描述
            self.table.setItem(row, 4, QTableWidgetItem(record['description'] or ""))
        
        # 更新统计信息
        total_hours = int(total_seconds // 3600)
        total_minutes = int((total_seconds % 3600) // 60)
        self.total_time_label.setText(f"总时间: {total_hours}小时{total_minutes}分钟")
        
        if category_times:
            category_text = "类别时间: "
            for category, seconds in category_times.items():
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                category_text += f"{category}({hours}小时{minutes}分钟) "
            self.category_time_label.setText(category_text)
        else:
            self.category_time_label.setText("类别时间: --")
    
    def _on_selection_changed(self):
        """选择变化处理"""
        selected_rows = self.table.selectedItems()
        has_selection = len(selected_rows) > 0
        
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
    
    def _on_add_clicked(self):
        """添加记录"""
        dialog = TimeRecordDialog(self, categories=self.db.get_categories())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_record_data()
            # 使用新的add_time_entry方法添加记录
            self.db.add_time_entry(
                category_id=data['category_id'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                description=data['description']
            )
            self.load_records(refresh_all=True) # Refresh all records
    
    def _on_edit_clicked(self):
        """编辑记录"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return
            
        # 从类别项中获取记录ID
        category_item = self.table.item(current_row, 0)
        record_id = category_item.data(Qt.ItemDataRole.UserRole)
        
        # 获取当前记录数据
        record = self.db.get_time_entry(record_id)
        if not record:
            return
            
        dialog = TimeRecordDialog(self, record, categories=self.db.get_categories())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_record_data()
            # Use correct update method signature from database.py
            self.db.update_time_entry(
                entry_id=record_id, 
                category_id=data['category_id'], 
                start_time=data['start_time'], 
                end_time=data['end_time'], 
                description=data['description']
            )
            self.load_records(refresh_all=True) # Refresh all records
    
    def _on_delete_clicked(self):
        """删除按钮点击处理"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        row = selected_items[0].row()
        record_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "确认", "确定要删除这条记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_time_entry(record_id)
            self.load_records(refresh_all=True) # Refresh all records
    
    def _on_filter_clicked(self):
        """筛选按钮点击处理"""
        # Load records using current filter settings
        self.load_records(refresh_all=False)

# The TimeRecordDialog class remains unchanged below
        self.load_categories()
        
        # 如果是编辑模式，设置当前类别
        if self.record:
            index = self.category_combo.findData(self.record['category_id'])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)