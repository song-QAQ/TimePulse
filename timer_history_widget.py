from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QComboBox, QFileDialog, QMessageBox,
                             QHeaderView, QFrame, QGroupBox, QRadioButton,
                             QButtonGroup, QSplitter, QTabWidget)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure

class TimerHistoryWidget(QWidget):
    """计时器历史记录查看组件"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.load_events()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("计时器历史记录")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title_label)
        
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
        
        # 事件名称筛选
        event_label = QLabel("事件名称:")
        self.event_filter = QComboBox()
        self.event_filter.addItem("全部")
        
        # 筛选按钮
        self.filter_button = QPushButton("筛选")
        self.filter_button.clicked.connect(self._on_filter_clicked)
        
        # 删除按钮
        delete_btn = QPushButton("删除选中")
        delete_btn.clicked.connect(self._on_delete_clicked)
        
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.start_date_edit)
        filter_layout.addWidget(QLabel("至"))
        filter_layout.addWidget(self.end_date_edit)
        filter_layout.addWidget(event_label)
        filter_layout.addWidget(self.event_filter)
        filter_layout.addWidget(self.filter_button)
        filter_layout.addWidget(delete_btn)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 历史记录标签页
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        # 历史记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["事件名称", "开始时间", "结束时间", "持续时间", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 100)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        history_layout.addWidget(self.table)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("导出历史记录")
        self.export_button.clicked.connect(self._on_export_clicked)
        export_layout.addWidget(self.export_button)
        export_layout.addStretch()
        
        history_layout.addLayout(export_layout)
        
        # 统计分析标签页
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        # 统计信息
        stats_group = QGroupBox("统计信息")
        stats_group_layout = QVBoxLayout(stats_group)
        
        self.total_events_label = QLabel("总事件数: 0")
        self.total_duration_label = QLabel("总计时时间: 0小时0分钟")
        self.avg_duration_label = QLabel("平均每次计时: 0小时0分钟")
        self.most_common_event_label = QLabel("最常见事件: 无")
        
        stats_group_layout.addWidget(self.total_events_label)
        stats_group_layout.addWidget(self.total_duration_label)
        stats_group_layout.addWidget(self.avg_duration_label)
        stats_group_layout.addWidget(self.most_common_event_label)
        
        stats_layout.addWidget(stats_group)
        
        # 图表
        chart_group = QGroupBox("图表")
        chart_group_layout = QVBoxLayout(chart_group)
        
        # 图表类型选择
        chart_type_layout = QHBoxLayout()
        chart_type_label = QLabel("图表类型:")
        
        self.chart_type_group = QButtonGroup(self)
        
        self.pie_chart_radio = QRadioButton("饼图")
        self.pie_chart_radio.setChecked(True)
        self.chart_type_group.addButton(self.pie_chart_radio)
        
        self.bar_chart_radio = QRadioButton("柱状图")
        self.chart_type_group.addButton(self.bar_chart_radio)
        
        self.line_chart_radio = QRadioButton("折线图")
        self.chart_type_group.addButton(self.line_chart_radio)
        
        chart_type_layout.addWidget(chart_type_label)
        chart_type_layout.addWidget(self.pie_chart_radio)
        chart_type_layout.addWidget(self.bar_chart_radio)
        chart_type_layout.addWidget(self.line_chart_radio)
        chart_type_layout.addStretch()
        
        chart_group_layout.addLayout(chart_type_layout)
        
        # 图表显示区域
        self.chart_label = QLabel("图表将在这里显示")
        self.chart_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_label.setMinimumHeight(300)
        self.chart_label.setStyleSheet("border: 1px solid #ccc;")
        
        chart_group_layout.addWidget(self.chart_label)
        
        # 更新图表按钮
        update_chart_layout = QHBoxLayout()
        self.update_chart_button = QPushButton("更新图表")
        self.update_chart_button.clicked.connect(self._update_chart)
        update_chart_layout.addWidget(self.update_chart_button)
        update_chart_layout.addStretch()
        
        chart_group_layout.addLayout(update_chart_layout)
        
        stats_layout.addWidget(chart_group)
        
        # 添加标签页
        tab_widget.addTab(history_tab, "历史记录")
        tab_widget.addTab(stats_tab, "统计分析")
        
        main_layout.addWidget(tab_widget)
    
    def load_events(self, start_date=None, end_date=None, event_name=None):
        """加载计时器事件"""
        if not start_date:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        if not end_date:
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        # 获取事件列表
        events = self.db.get_timer_events(start_date, end_date)
        
        # 更新事件名称筛选下拉框
        self.event_filter.clear()
        self.event_filter.addItem("全部")
        
        event_names = set()
        for event in events:
            event_names.add(event['event_name'])
        
        for name in sorted(event_names):
            self.event_filter.addItem(name)
        
        # 如果指定了事件名称，则筛选
        if event_name and event_name != "全部":
            events = [e for e in events if e['event_name'] == event_name]
        
        # 更新表格
        self.table.setRowCount(0)
        for event in events:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 事件名称
            self.table.setItem(row, 0, QTableWidgetItem(event['event_name']))
            
            # 开始时间
            start_time = datetime.strptime(event['start_time'], "%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 1, QTableWidgetItem(start_time.strftime("%Y-%m-%d %H:%M:%S")))
            
            # 结束时间
            end_time = datetime.strptime(event['end_time'], "%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 2, QTableWidgetItem(end_time.strftime("%Y-%m-%d %H:%M:%S")))
            
            # 持续时间
            duration = event['duration']
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            self.table.setItem(row, 3, QTableWidgetItem(f"{hours:02d}:{minutes:02d}"))
            
            # 操作按钮
            delete_button = QPushButton("删除")
            delete_button.clicked.connect(lambda checked, e=event: self._on_delete_clicked(e))
            self.table.setCellWidget(row, 4, delete_button)
        
        # 更新统计信息
        self._update_stats(events)
    
    def _update_stats(self, events):
        """更新统计信息"""
        if not events:
            self.total_events_label.setText("总事件数: 0")
            self.total_duration_label.setText("总计时时间: 0小时0分钟")
            self.avg_duration_label.setText("平均每次计时: 0小时0分钟")
            self.most_common_event_label.setText("最常见事件: 无")
            return
        
        # 总事件数
        total_events = len(events)
        self.total_events_label.setText(f"总事件数: {total_events}")
        
        # 总计时时间
        total_duration = sum(event['duration'] for event in events)
        total_hours = total_duration // 3600
        total_minutes = (total_duration % 3600) // 60
        self.total_duration_label.setText(f"总计时时间: {total_hours}小时{total_minutes}分钟")
        
        # 平均每次计时
        avg_duration = total_duration / total_events
        avg_hours = int(avg_duration // 3600)
        avg_minutes = int((avg_duration % 3600) // 60)
        self.avg_duration_label.setText(f"平均每次计时: {avg_hours}小时{avg_minutes}分钟")
        
        # 最常见事件
        event_counts = {}
        for event in events:
            name = event['event_name']
            if name in event_counts:
                event_counts[name] += 1
            else:
                event_counts[name] = 1
        
        most_common = max(event_counts.items(), key=lambda x: x[1])
        self.most_common_event_label.setText(f"最常见事件: {most_common[0]} ({most_common[1]}次)")
    
    def _update_chart(self):
        """更新图表"""
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        event_name = self.event_filter.currentText()
        
        # 获取事件数据
        events = self.db.get_timer_events(start_date, end_date)
        
        # 如果指定了事件名称，则筛选
        if event_name and event_name != "全部":
            events = [e for e in events if e['event_name'] == event_name]
        
        if not events:
            self.chart_label.setText("没有数据可供显示")
            return
        
        # 根据选择的图表类型创建图表
        plt.figure(figsize=(8, 6))
        
        if self.pie_chart_radio.isChecked():
            # 饼图：按事件名称分组
            event_durations = {}
            for event in events:
                name = event['event_name']
                if name in event_durations:
                    event_durations[name] += event['duration']
                else:
                    event_durations[name] = event['duration']
            
            # 转换为小时
            for name in event_durations:
                event_durations[name] = event_durations[name] / 3600
            
            plt.pie(event_durations.values(), labels=event_durations.keys(), autopct='%1.1f%%')
            plt.title('各事件时间分布')
        
        elif self.bar_chart_radio.isChecked():
            # 柱状图：按日期分组
            date_durations = {}
            for event in events:
                date = event['start_time'].split()[0]
                if date in date_durations:
                    date_durations[date] += event['duration']
                else:
                    date_durations[date] = event['duration']
            
            # 转换为小时
            for date in date_durations:
                date_durations[date] = date_durations[date] / 3600
            
            plt.bar(date_durations.keys(), date_durations.values())
            plt.title('每日计时时间')
            plt.xlabel('日期')
            plt.ylabel('小时')
            plt.xticks(rotation=45)
        
        else:  # 折线图
            # 折线图：按日期分组
            date_durations = {}
            for event in events:
                date = event['start_time'].split()[0]
                if date in date_durations:
                    date_durations[date] += event['duration']
                else:
                    date_durations[date] = event['duration']
            
            # 转换为小时
            for date in date_durations:
                date_durations[date] = date_durations[date] / 3600
            
            # 按日期排序
            sorted_dates = sorted(date_durations.keys())
            sorted_durations = [date_durations[date] for date in sorted_dates]
            
            plt.plot(sorted_dates, sorted_durations, marker='o')
            plt.title('每日计时时间趋势')
            plt.xlabel('日期')
            plt.ylabel('小时')
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # 保存图表到临时文件
        temp_file = "temp_chart.png"
        plt.savefig(temp_file)
        plt.close()
        
        # 显示图表
        self.chart_label.setPixmap(QIcon(temp_file).pixmap(self.chart_label.size()))
        
        # 删除临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    def _on_filter_clicked(self):
        """筛选按钮点击处理"""
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        event_name = self.event_filter.currentText()
        
        self.load_events(start_date, end_date, event_name)
    
    def _on_delete_clicked(self, event):
        """删除按钮点击处理"""
        reply = QMessageBox.question(
            self, "确认", f"确定要删除事件 '{event['event_name']}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 从数据库中删除事件
            self.db.delete_timer_event(event['id'])
            
            # 重新加载事件
            self.load_events()
    
    def _on_export_clicked(self):
        """导出按钮点击处理"""
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        event_name = self.event_filter.currentText()
        
        # 获取事件数据
        events = self.db.get_timer_events(start_date, end_date)
        
        # 如果指定了事件名称，则筛选
        if event_name and event_name != "全部":
            events = [e for e in events if e['event_name'] == event_name]
        
        if not events:
            QMessageBox.information(self, "提示", "没有数据可供导出")
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文件", "", "Excel文件 (*.xlsx);;CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            # 准备数据
            data = []
            for event in events:
                start_time = datetime.strptime(event['start_time'], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(event['end_time'], "%Y-%m-%d %H:%M:%S")
                duration = event['duration']
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                
                data.append({
                    '事件名称': event['event_name'],
                    '开始时间': start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    '结束时间': end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    '持续时间(小时)': f"{hours}.{minutes:02d}",
                    '持续时间(分钟)': duration // 60
                })
            
            # 导出数据
            if file_path.endswith('.xlsx'):
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False)
            else:
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            QMessageBox.information(self, "成功", f"数据已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}") 