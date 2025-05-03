from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QComboBox, QFileDialog,
                             QMessageBox, QFrame, QGroupBox, QRadioButton,
                             QButtonGroup, QCheckBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
import os
from utils import TimeUtils
import pandas as pd
import csv
from datetime import datetime

class ExportWidget(QWidget):
    """数据导出界面组件"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("数据导出")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(line)
        
        # 时间记录导出
        time_group = QGroupBox("时间记录导出")
        time_layout = QVBoxLayout(time_group)
        
        # 日期范围
        date_layout = QHBoxLayout()
        date_label = QLabel("日期范围:")
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("至"))
        date_layout.addWidget(self.end_date_edit)
        date_layout.addStretch()
        
        time_layout.addLayout(date_layout)
        
        # 类别筛选
        category_layout = QHBoxLayout()
        category_label = QLabel("类别:")
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("全部")
        categories = self.db.get_categories()
        for category in categories:
            self.category_combo.addItem(category['name'], category['id'])
        
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        
        time_layout.addLayout(category_layout)
        
        # 导出格式
        format_layout = QHBoxLayout()
        format_label = QLabel("导出格式:")
        
        self.format_group = QButtonGroup(self)
        
        self.csv_radio = QRadioButton("CSV")
        self.csv_radio.setChecked(True)
        self.format_group.addButton(self.csv_radio)
        
        self.excel_radio = QRadioButton("Excel")
        self.format_group.addButton(self.excel_radio)
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.csv_radio)
        format_layout.addWidget(self.excel_radio)
        format_layout.addStretch()
        
        time_layout.addLayout(format_layout)
        
        # 导出按钮
        button_layout = QHBoxLayout()
        self.export_time_button = QPushButton("导出时间记录")
        self.export_time_button.setIcon(QIcon(os.path.join("icons", "export.png")))
        self.export_time_button.clicked.connect(self._on_export_time_clicked)
        
        button_layout.addWidget(self.export_time_button)
        button_layout.addStretch()
        
        time_layout.addLayout(button_layout)
        
        main_layout.addWidget(time_group)
        
        # 图表导出
        chart_group = QGroupBox("图表导出")
        chart_layout = QVBoxLayout(chart_group)
        
        # 图表类型
        chart_type_layout = QHBoxLayout()
        chart_type_label = QLabel("图表类型:")
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["时间分布饼图", "每日时间使用柱状图"])
        
        chart_type_layout.addWidget(chart_type_label)
        chart_type_layout.addWidget(self.chart_type_combo)
        chart_type_layout.addStretch()
        
        chart_layout.addLayout(chart_type_layout)
        
        # 日期范围
        chart_date_layout = QHBoxLayout()
        chart_date_label = QLabel("日期范围:")
        
        self.chart_start_date_edit = QDateEdit()
        self.chart_start_date_edit.setCalendarPopup(True)
        self.chart_start_date_edit.setDate(QDate.currentDate().addDays(-7))
        
        self.chart_end_date_edit = QDateEdit()
        self.chart_end_date_edit.setCalendarPopup(True)
        self.chart_end_date_edit.setDate(QDate.currentDate())
        
        chart_date_layout.addWidget(chart_date_label)
        chart_date_layout.addWidget(self.chart_start_date_edit)
        chart_date_layout.addWidget(QLabel("至"))
        chart_date_layout.addWidget(self.chart_end_date_edit)
        chart_date_layout.addStretch()
        
        chart_layout.addLayout(chart_date_layout)
        
        # 导出按钮
        chart_button_layout = QHBoxLayout()
        self.export_chart_button = QPushButton("导出图表")
        self.export_chart_button.setIcon(QIcon(os.path.join("icons", "export.png")))
        self.export_chart_button.clicked.connect(self._on_export_chart_clicked)
        
        chart_button_layout.addWidget(self.export_chart_button)
        chart_button_layout.addStretch()
        
        chart_layout.addLayout(chart_button_layout)
        
        main_layout.addWidget(chart_group)
        
        # 日记导出
        journal_group = QGroupBox("日记导出")
        journal_layout = QVBoxLayout(journal_group)
        
        # 日期范围
        journal_date_layout = QHBoxLayout()
        journal_date_label = QLabel("日期范围:")
        
        self.journal_start_date_edit = QDateEdit()
        self.journal_start_date_edit.setCalendarPopup(True)
        self.journal_start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        
        self.journal_end_date_edit = QDateEdit()
        self.journal_end_date_edit.setCalendarPopup(True)
        self.journal_end_date_edit.setDate(QDate.currentDate())
        
        journal_date_layout.addWidget(journal_date_label)
        journal_date_layout.addWidget(self.journal_start_date_edit)
        journal_date_layout.addWidget(QLabel("至"))
        journal_date_layout.addWidget(self.journal_end_date_edit)
        journal_date_layout.addStretch()
        
        journal_layout.addLayout(journal_date_layout)
        
        # 导出格式
        journal_format_layout = QHBoxLayout()
        journal_format_label = QLabel("导出格式:")
        
        self.journal_format_group = QButtonGroup(self)
        
        self.journal_csv_radio = QRadioButton("CSV")
        self.journal_csv_radio.setChecked(True)
        self.journal_format_group.addButton(self.journal_csv_radio)
        
        self.journal_excel_radio = QRadioButton("Excel")
        self.journal_format_group.addButton(self.journal_excel_radio)
        
        journal_format_layout.addWidget(journal_format_label)
        journal_format_layout.addWidget(self.journal_csv_radio)
        journal_format_layout.addWidget(self.journal_excel_radio)
        journal_format_layout.addStretch()
        
        journal_layout.addLayout(journal_format_layout)
        
        # 导出按钮
        journal_button_layout = QHBoxLayout()
        self.export_journal_button = QPushButton("导出日记")
        self.export_journal_button.setIcon(QIcon(os.path.join("icons", "export.png")))
        self.export_journal_button.clicked.connect(self._on_export_journal_clicked)
        
        journal_button_layout.addWidget(self.export_journal_button)
        journal_button_layout.addStretch()
        
        journal_layout.addLayout(journal_button_layout)
        
        main_layout.addWidget(journal_group)
        
        # 任务导出
        task_group = QGroupBox("任务导出")
        task_layout = QVBoxLayout(task_group)
        
        # 状态筛选
        task_status_layout = QHBoxLayout()
        task_status_label = QLabel("状态:")
        
        self.task_status_combo = QComboBox()
        self.task_status_combo.addItems(["全部", "待处理", "进行中", "已完成", "已取消"])
        
        task_status_layout.addWidget(task_status_label)
        task_status_layout.addWidget(self.task_status_combo)
        task_status_layout.addStretch()
        
        task_layout.addLayout(task_status_layout)
        
        # 导出格式
        task_format_layout = QHBoxLayout()
        task_format_label = QLabel("导出格式:")
        
        self.task_format_group = QButtonGroup(self)
        
        self.task_csv_radio = QRadioButton("CSV")
        self.task_csv_radio.setChecked(True)
        self.task_format_group.addButton(self.task_csv_radio)
        
        self.task_excel_radio = QRadioButton("Excel")
        self.task_format_group.addButton(self.task_excel_radio)
        
        task_format_layout.addWidget(task_format_label)
        task_format_layout.addWidget(self.task_csv_radio)
        task_format_layout.addWidget(self.task_excel_radio)
        task_format_layout.addStretch()
        
        task_layout.addLayout(task_format_layout)
        
        # 导出按钮
        task_button_layout = QHBoxLayout()
        self.export_task_button = QPushButton("导出任务")
        self.export_task_button.setIcon(QIcon(os.path.join("icons", "export.png")))
        self.export_task_button.clicked.connect(self._on_export_task_clicked)
        
        task_button_layout.addWidget(self.export_task_button)
        task_button_layout.addStretch()
        
        task_layout.addLayout(task_button_layout)
        
        main_layout.addWidget(task_group)
        
        main_layout.addStretch()
    
    def _on_export_time_clicked(self):
        """导出时间记录按钮点击处理"""
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        category_id = self.category_combo.currentData()
        
        # 获取时间记录
        entries = self.db.get_time_entries(start_date, end_date, category_id)
        if not entries:
            QMessageBox.information(self, "提示", "没有找到符合条件的时间记录")
            return
        
        # 选择保存路径
        file_filter = "CSV文件 (*.csv)" if self.csv_radio.isChecked() else "Excel文件 (*.xlsx)"
        file_extension = ".csv" if self.csv_radio.isChecked() else ".xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", file_filter
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名正确
        if not file_path.endswith(file_extension):
            file_path += file_extension
        
        try:
            # 导出数据
            if self.csv_radio.isChecked():
                self._export_time_to_csv(entries, file_path)
            else:
                self._export_time_to_excel(entries, file_path)
            
            QMessageBox.information(self, "成功", f"数据已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _export_time_to_csv(self, entries, filename):
        """将时间记录导出为CSV文件"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'date', 'start_time', 'end_time', 'duration', 'category', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entry in entries:
                writer.writerow({
                    'id': entry['id'],
                    'date': entry['date'],
                    'start_time': entry['start_time'],
                    'end_time': entry['end_time'],
                    'duration': entry['duration'],
                    'category': entry['category_name'],
                    'description': entry['description'] or ''
                })
    
    def _export_time_to_excel(self, entries, filename):
        """将时间记录导出为Excel文件"""
        data = []
        for entry in entries:
            data.append({
                'ID': entry['id'],
                '日期': entry['date'],
                '开始时间': entry['start_time'],
                '结束时间': entry['end_time'],
                '持续时间': entry['duration'],
                '分类': entry['category_name'],
                '描述': entry['description'] or ''
            })
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
    
    def _on_export_chart_clicked(self):
        """导出图表按钮点击处理"""
        start_date = self.chart_start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.chart_end_date_edit.date().toString("yyyy-MM-dd")
        chart_type = self.chart_type_combo.currentText()
        
        # 获取时间记录
        entries = self.db.get_time_entries(start_date, end_date)
        if not entries:
            QMessageBox.information(self, "提示", "没有找到符合条件的时间记录")
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存图表", "", "PNG图片 (*.png)"
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名正确
        if not file_path.endswith(".png"):
            file_path += ".png"
        
        try:
            # 导出图表
            if chart_type == "时间分布饼图":
                self._create_time_distribution_chart(entries, file_path)
            else:  # 每日时间使用柱状图
                days = (self.chart_end_date_edit.date().toPyDate() - 
                        self.chart_start_date_edit.date().toPyDate()).days + 1
                self._create_daily_time_chart(entries, days, file_path)
            
            QMessageBox.information(self, "成功", f"图表已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _create_time_distribution_chart(self, entries, filename):
        """创建时间分布饼图"""
        import matplotlib.pyplot as plt
        
        # 按分类统计时间
        category_times = {}
        for entry in entries:
            category = entry['category_name']
            duration = entry['duration']
            if category in category_times:
                category_times[category] += duration
            else:
                category_times[category] = duration
        
        # 创建饼图
        plt.figure(figsize=(10, 8))
        plt.pie(category_times.values(), labels=category_times.keys(), autopct='%1.1f%%')
        plt.title('时间分布')
        plt.axis('equal')
        
        # 保存图表
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_daily_time_chart(self, entries, days, filename):
        """创建每日时间使用柱状图"""
        import matplotlib.pyplot as plt
        from datetime import datetime, timedelta
        
        # 按日期统计时间
        daily_times = {}
        start_date = datetime.strptime(entries[0]['date'], '%Y-%m-%d')
        for i in range(days):
            date = start_date + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            daily_times[date_str] = 0
        
        for entry in entries:
            date = entry['date']
            duration = entry['duration']
            daily_times[date] += duration
        
        # 创建柱状图
        plt.figure(figsize=(12, 6))
        plt.bar(daily_times.keys(), daily_times.values())
        plt.title('每日时间使用')
        plt.xlabel('日期')
        plt.ylabel('时间（小时）')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _on_export_journal_clicked(self):
        """导出日记按钮点击处理"""
        start_date = self.journal_start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.journal_end_date_edit.date().toString("yyyy-MM-dd")
        
        # 获取日记条目
        entries = self.db.get_journal_entries(start_date, end_date)
        if not entries:
            QMessageBox.information(self, "提示", "没有找到符合条件的日记条目")
            return
        
        # 选择保存路径
        file_filter = "CSV文件 (*.csv)" if self.journal_csv_radio.isChecked() else "Excel文件 (*.xlsx)"
        file_extension = ".csv" if self.journal_csv_radio.isChecked() else ".xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", file_filter
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名正确
        if not file_path.endswith(file_extension):
            file_path += file_extension
        
        try:
            # 导出数据
            if self.journal_csv_radio.isChecked():
                self._export_journal_to_csv(entries, file_path)
            else:
                self._export_journal_to_excel(entries, file_path)
            
            QMessageBox.information(self, "成功", f"数据已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _export_journal_to_csv(self, entries, filename):
        """将日记导出为CSV文件"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'date', 'title', 'content', 'mood', 'weather', 'tags']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entry in entries:
                writer.writerow({
                    'id': entry['id'],
                    'date': entry['date'],
                    'title': entry['title'] or '',
                    'content': entry['content'] or '',
                    'mood': entry['mood'] or '',
                    'weather': entry['weather'] or '',
                    'tags': ','.join(entry['tags']) if entry['tags'] else ''
                })
    
    def _export_journal_to_excel(self, entries, filename):
        """将日记导出为Excel文件"""
        data = []
        for entry in entries:
            data.append({
                'ID': entry['id'],
                '日期': entry['date'],
                '标题': entry['title'] or '',
                '内容': entry['content'] or '',
                '心情': entry['mood'] or '',
                '天气': entry['weather'] or '',
                '标签': ','.join(entry['tags']) if entry['tags'] else ''
            })
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
    
    def _on_export_task_clicked(self):
        """导出任务按钮点击处理"""
        status = self.task_status_combo.currentText()
        
        # 获取任务
        tasks = self.db.get_tasks(status if status != "全部" else None)
        if not tasks:
            QMessageBox.information(self, "提示", "没有找到符合条件的任务")
            return
        
        # 选择保存路径
        file_filter = "CSV文件 (*.csv)" if self.task_csv_radio.isChecked() else "Excel文件 (*.xlsx)"
        file_extension = ".csv" if self.task_csv_radio.isChecked() else ".xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", file_filter
        )
        
        if not file_path:
            return
        
        # 确保文件扩展名正确
        if not file_path.endswith(file_extension):
            file_path += file_extension
        
        try:
            # 导出数据
            if self.task_csv_radio.isChecked():
                self._export_task_to_csv(tasks, file_path)
            else:
                self._export_task_to_excel(tasks, file_path)
            
            QMessageBox.information(self, "成功", f"数据已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _export_task_to_csv(self, tasks, filename):
        """将任务导出为CSV文件"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'id', 'title', 'description', 'due_date', 'priority', 'status',
                'tags', 'reminder_time', 'reminder_hours', 'created_at', 'updated_at'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for task in tasks:
                writer.writerow({
                    'id': task['id'],
                    'title': task['title'],
                    'description': task['description'] or '',
                    'due_date': task['due_date'] or '',
                    'priority': task['priority'],
                    'status': task['status'],
                    'tags': ','.join(task['tags']) if task['tags'] else '',
                    'reminder_time': task['reminder_time'] or '',
                    'reminder_hours': task['reminder_hours'] or '',
                    'created_at': task['created_at'],
                    'updated_at': task['updated_at'] or ''
                })
    
    def _export_task_to_excel(self, tasks, filename):
        """将任务导出为Excel文件"""
        data = []
        for task in tasks:
            data.append({
                'ID': task['id'],
                '标题': task['title'],
                '描述': task['description'] or '',
                '截止日期': task['due_date'] or '',
                '优先级': task['priority'],
                '状态': task['status'],
                '标签': ','.join(task['tags']) if task['tags'] else '',
                '提醒时间': task['reminder_time'] or '',
                '提前提醒(小时)': task['reminder_hours'] or '',
                '创建时间': task['created_at'],
                '更新时间': task['updated_at'] or ''
            })
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False) 