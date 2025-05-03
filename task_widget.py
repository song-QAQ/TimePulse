from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QTableWidget,
                             QTableWidgetItem, QDateEdit, QMessageBox, QFrame,
                             QDialog, QFormLayout, QSpinBox, QComboBox, QCheckBox,
                             QListWidget, QListWidgetItem, QGroupBox, QHeaderView,
                             QDialogButtonBox, QMenu)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QIcon, QColor
from datetime import datetime, timedelta
import os
import json

class TagDialog(QDialog):
    """标签管理对话框"""
    
    def __init__(self, parent=None, tags=None):
        super().__init__(parent)
        self.tags = tags or []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("管理标签")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        # 标签列表
        self.tag_list = QListWidget()
        for tag in self.tags:
            self.tag_list.addItem(tag)
        layout.addWidget(self.tag_list)
        
        # 添加标签
        add_layout = QHBoxLayout()
        self.tag_edit = QLineEdit()
        self.tag_edit.setPlaceholderText("输入新标签")
        add_button = QPushButton("添加")
        add_button.clicked.connect(self._on_add_clicked)
        
        add_layout.addWidget(self.tag_edit)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)
        
        # 删除标签
        delete_button = QPushButton("删除选中标签")
        delete_button.clicked.connect(self._on_delete_clicked)
        layout.addWidget(delete_button)
        
        # 确定取消按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def _on_add_clicked(self):
        """添加标签"""
        tag = self.tag_edit.text().strip()
        if not tag:
            return
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.tag_list.addItem(tag)
            self.tag_edit.clear()
    
    def _on_delete_clicked(self):
        """删除标签"""
        current_item = self.tag_list.currentItem()
        if not current_item:
            return
        
        tag = current_item.text()
        self.tags.remove(tag)
        self.tag_list.takeItem(self.tag_list.row(current_item))
    
    def get_tags(self):
        """获取标签列表"""
        return self.tags

class TaskDialog(QDialog):
    """任务对话框"""
    def __init__(self, parent=None, db=None, task=None):
        super().__init__(parent)
        self.db = db
        self.task = task
        self.tags = []
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('任务')
        layout = QFormLayout()
        
        # 标题
        self.title_edit = QLineEdit()
        if self.task:
            self.title_edit.setText(self.task['title'])
        layout.addRow('标题:', self.title_edit)
        
        # 描述
        self.desc_edit = QTextEdit()
        if self.task:
            self.desc_edit.setText(self.task['description'])
        layout.addRow('描述:', self.desc_edit)
        
        # 截止日期
        self.due_date_edit = QDateEdit()
        self.due_date_edit.setCalendarPopup(True)
        if self.task and self.task['due_date']:
            self.due_date_edit.setDate(QDate.fromString(self.task['due_date'], 'yyyy-MM-dd'))
        else:
            self.due_date_edit.setDate(QDate.currentDate())
        layout.addRow('截止日期:', self.due_date_edit)
        
        # 优先级
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['低', '中', '高'])
        if self.task:
            self.priority_combo.setCurrentText(str(self.task['priority']))
        layout.addRow('优先级:', self.priority_combo)
        
        # 标签
        self.tag_label = QLabel()
        if self.task and self.task.get('tags'):
            try:
                self.tags = json.loads(self.task['tags'])
                self.tag_label.setText(', '.join(self.tags))
            except json.JSONDecodeError:
                self.tags = []
                self.tag_label.setText('')
        
        tag_layout = QHBoxLayout()
        tag_layout.addWidget(self.tag_label)
        tag_btn = QPushButton('管理标签')
        tag_btn.clicked.connect(self._on_manage_tags_clicked)
        tag_layout.addWidget(tag_btn)
        layout.addRow('标签:', tag_layout)
        
        # 提醒设置
        reminder_group = QGroupBox('提醒设置')
        reminder_layout = QVBoxLayout()
        
        # 启用提醒
        self.reminder_check = QCheckBox('启用提醒')
        if self.task:
            self.reminder_check.setChecked(bool(self.task.get('reminder_time')))
        self.reminder_check.stateChanged.connect(self._on_reminder_changed)
        reminder_layout.addWidget(self.reminder_check)
        
        # 提醒时间设置
        reminder_time_layout = QHBoxLayout()
        self.reminder_hours_spin = QSpinBox()
        self.reminder_hours_spin.setRange(1, 72)
        self.reminder_hours_spin.setSuffix(' 小时')
        if self.task and self.task.get('reminder_hours'):
            self.reminder_hours_spin.setValue(int(self.task['reminder_hours']))
        else:
            self.reminder_hours_spin.setValue(24)
        self.reminder_hours_spin.setEnabled(self.reminder_check.isChecked())
        
        reminder_time_layout.addWidget(QLabel('提前'))
        reminder_time_layout.addWidget(self.reminder_hours_spin)
        reminder_time_layout.addWidget(QLabel('提醒'))
        reminder_time_layout.addStretch()
        reminder_layout.addLayout(reminder_time_layout)
        
        # 预览提醒时间
        self.reminder_preview = QLabel()
        self._update_reminder_preview()
        self.due_date_edit.dateChanged.connect(self._update_reminder_preview)
        self.reminder_hours_spin.valueChanged.connect(self._update_reminder_preview)
        reminder_layout.addWidget(self.reminder_preview)
        
        reminder_group.setLayout(reminder_layout)
        layout.addRow(reminder_group)
        
        # 按钮
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)
        
        self.setLayout(layout)
    
    def _on_manage_tags_clicked(self):
        """标签管理按钮点击处理"""
        dialog = TagDialog(self, self.tags)
        if dialog.exec():
            self.tags = dialog.get_tags()
            self.tag_label.setText(', '.join(self.tags))
    
    def _on_reminder_changed(self, state):
        """提醒复选框状态改变处理"""
        self.reminder_hours_spin.setEnabled(state == Qt.CheckState.Checked)
        self._update_reminder_preview()
    
    def _update_reminder_preview(self):
        """更新提醒时间预览"""
        if not self.reminder_check.isChecked():
            self.reminder_preview.setText('未启用提醒')
            return
            
        due_date = self.due_date_edit.date().toPyDate()
        hours = self.reminder_hours_spin.value()
        reminder_time = datetime.combine(due_date, datetime.min.time()) - timedelta(hours=hours)
        
        self.reminder_preview.setText(
            f'将在 {reminder_time.strftime("%Y-%m-%d %H:%M")} 提醒'
        )
    
    def get_task_data(self):
        """获取任务数据"""
        return {
            'title': self.title_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'due_date': self.due_date_edit.date().toPyDate(),
            'priority': self.priority_combo.currentText(),
            'tags': self.tags,
            'reminder': self.reminder_check.isChecked(),
            'reminder_hours': self.reminder_hours_spin.value()
        }

class TaskWidget(QWidget):
    """任务管理界面组件"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_task_id = None
        self.reminder_timer = QTimer()
        self.reminder_timer.timeout.connect(self._check_reminders)
        self.reminder_timer.start(60000)  # 每分钟检查一次
        
        # 每天凌晨重置提醒状态
        self.reset_timer = QTimer()
        self.reset_timer.timeout.connect(self._reset_reminders)
        self._schedule_next_reset()
        
        self.init_ui()
        self.load_tasks()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 任务管理标题和按钮
        header_layout = QHBoxLayout()
        header_label = QLabel("任务管理")
        header_label.setStyleSheet("font-weight: bold;")
        
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
        
        header_layout.addWidget(header_label)
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
        filter_group = QGroupBox("筛选选项")
        filter_layout = QVBoxLayout(filter_group)
        
        # 状态筛选
        status_layout = QHBoxLayout()
        status_label = QLabel("状态:")
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "待处理", "进行中", "已完成", "已取消"])
        self.status_filter.currentIndexChanged.connect(self._on_filter_changed)
        
        # 截止日期筛选
        due_label = QLabel("截止日期:")
        self.due_filter = QComboBox()
        self.due_filter.addItems(["全部", "今天", "本周", "下周", "本月", "已逾期"])
        self.due_filter.currentIndexChanged.connect(self._on_filter_changed)
        
        # 优先级筛选
        priority_label = QLabel("优先级:")
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["全部", "低", "中", "高"])
        self.priority_filter.currentIndexChanged.connect(self._on_filter_changed)
        
        # 标签筛选
        tag_label = QLabel("标签:")
        self.tag_filter = QComboBox()
        self.tag_filter.addItem("全部")
        self.tag_filter.currentIndexChanged.connect(self._on_filter_changed)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_filter)
        status_layout.addWidget(due_label)
        status_layout.addWidget(self.due_filter)
        status_layout.addWidget(priority_label)
        status_layout.addWidget(self.priority_filter)
        status_layout.addWidget(tag_label)
        status_layout.addWidget(self.tag_filter)
        status_layout.addStretch()
        
        filter_layout.addLayout(status_layout)
        main_layout.addWidget(filter_group)
        
        # 任务统计
        stats_group = QGroupBox("任务统计")
        stats_layout = QHBoxLayout(stats_group)
        
        self.total_label = QLabel("总任务数: 0")
        self.pending_label = QLabel("待处理: 0")
        self.in_progress_label = QLabel("进行中: 0")
        self.completed_label = QLabel("已完成: 0")
        self.overdue_label = QLabel("已逾期: 0")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.pending_label)
        stats_layout.addWidget(self.in_progress_label)
        stats_layout.addWidget(self.completed_label)
        stats_layout.addWidget(self.overdue_label)
        stats_layout.addStretch()
        
        main_layout.addWidget(stats_group)
        
        # 任务表格
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "标题", "描述", "截止日期", "优先级", "状态", "标签", "提醒", "创建时间"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        
        main_layout.addWidget(self.table)
        
        # 设置表格的右键菜单
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._on_table_context_menu)
    
    def load_tasks(self):
        """加载任务"""
        self._update_task_table()
    
    def _update_task_table(self):
        """更新任务表格"""
        self.table.setRowCount(0)
        tasks = self.db.get_tasks()
        
        # 更新标签筛选
        all_tags = set()
        for task in tasks:
            if task.get('tags'):
                tags = json.loads(task['tags'])
                all_tags.update(tags)
        
        current_tag = self.tag_filter.currentText()
        self.tag_filter.blockSignals(True)  # 阻止信号
        self.tag_filter.clear()
        self.tag_filter.addItem("全部")
        for tag in sorted(all_tags):
            self.tag_filter.addItem(tag)
        
        if current_tag in all_tags:
            index = self.tag_filter.findText(current_tag)
            if index >= 0:
                self.tag_filter.setCurrentIndex(index)
        self.tag_filter.blockSignals(False)  # 恢复信号
        
        # 应用筛选
        status_filter = self.status_filter.currentText()
        due_filter = self.due_filter.currentText()
        priority_filter = self.priority_filter.currentText()
        tag_filter = self.tag_filter.currentText()
        
        filtered_tasks = []
        today = QDate.currentDate()
        
        # 统计数据
        total = len(tasks)
        pending = 0
        in_progress = 0
        completed = 0
        overdue = 0
        
        for task in tasks:
            # 更新统计
            if task['status'] == "待处理":
                pending += 1
            elif task['status'] == "进行中":
                in_progress += 1
            elif task['status'] == "已完成":
                completed += 1
            
            if task['due_date']:
                due_date = QDate.fromString(task['due_date'], "yyyy-MM-dd")
                if due_date < today and task['status'] not in ["已完成", "已取消"]:
                    overdue += 1
            
            # 状态筛选
            if status_filter != "全部" and task['status'] != status_filter:
                continue
            
            # 优先级筛选
            if priority_filter != "全部" and task['priority'] != priority_filter:
                continue
            
            # 标签筛选
            if tag_filter != "全部":
                task_tags = json.loads(task.get('tags', '[]'))
                if tag_filter not in task_tags:
                    continue
            
            # 截止日期筛选
            if due_filter != "全部":
                if not task['due_date']:
                    continue
                
                due_date = QDate.fromString(task['due_date'], "yyyy-MM-dd")
                
                if due_filter == "今天" and due_date != today:
                    continue
                elif due_filter == "本周" and not (today.daysTo(due_date) >= 0 and today.daysTo(due_date) < 7):
                    continue
                elif due_filter == "下周" and not (today.daysTo(due_date) >= 7 and today.daysTo(due_date) < 14):
                    continue
                elif due_filter == "本月" and not (due_date.month() == today.month() and due_date.year() == today.year()):
                    continue
                elif due_filter == "已逾期" and today.daysTo(due_date) >= 0:
                    continue
            
            filtered_tasks.append(task)
        
        # 更新统计标签
        self.total_label.setText(f"总任务数: {total}")
        self.pending_label.setText(f"待处理: {pending}")
        self.in_progress_label.setText(f"进行中: {in_progress}")
        self.completed_label.setText(f"已完成: {completed}")
        self.overdue_label.setText(f"已逾期: {overdue}")
        
        # 按优先级和截止日期排序
        filtered_tasks.sort(
            key=lambda x: (
                {'高': 0, '中': 1, '低': 2}[x['priority']],
                x['due_date'] or '9999-12-31'
            )
        )
        
        self.table.setRowCount(0)
        for task in filtered_tasks:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 标题
            title_item = QTableWidgetItem(task['title'])
            title_item.setData(Qt.ItemDataRole.UserRole, task['id'])
            self.table.setItem(row, 0, title_item)
            
            # 描述
            self.table.setItem(row, 1, QTableWidgetItem(task['description'] or ""))
            
            # 截止日期
            due_date = task['due_date'] or "无"
            due_item = QTableWidgetItem(due_date)
            
            # 设置颜色
            if task['due_date']:
                due_date_obj = QDate.fromString(task['due_date'], "yyyy-MM-dd")
                if due_date_obj < today and task['status'] not in ["已完成", "已取消"]:
                    due_item.setBackground(QColor("#ffcccc"))  # 红色背景表示已逾期
                elif due_date_obj == today and task['status'] not in ["已完成", "已取消"]:
                    due_item.setBackground(QColor("#ffffcc"))  # 黄色背景表示今天到期
            
            self.table.setItem(row, 2, due_item)
            
            # 优先级
            priority_item = QTableWidgetItem(task['priority'])
            priority_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 设置颜色
            if task['priority'] == "高":
                priority_item.setBackground(QColor("#ffcccc"))  # 红色背景表示高优先级
            elif task['priority'] == "中":
                priority_item.setBackground(QColor("#ffffcc"))  # 黄色背景表示中优先级
            
            self.table.setItem(row, 3, priority_item)
            
            # 状态
            status_item = QTableWidgetItem(task['status'])
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 设置颜色
            if task['status'] == "已完成":
                status_item.setBackground(QColor("#ccffcc"))  # 绿色背景表示已完成
            elif task['status'] == "已取消":
                status_item.setBackground(QColor("#cccccc"))  # 灰色背景表示已取消
            
            self.table.setItem(row, 4, status_item)
            
            # 标签
            tags = task.get('tags', [])
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except json.JSONDecodeError:
                    tags = []
            tag_item = QTableWidgetItem(", ".join(tags))
            self.table.setItem(row, 5, tag_item)
            
            # 提醒
            reminder_item = QTableWidgetItem()
            reminder_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if task.get('reminder_time'):
                if task.get('reminder_sent'):
                    reminder_item.setText('已提醒')
                    reminder_item.setBackground(QColor("#cccccc"))  # 灰色背景表示已提醒
                else:
                    reminder_time = datetime.strptime(task['reminder_time'], '%Y-%m-%d %H:%M:%S')
                    if datetime.now() >= reminder_time:
                        reminder_item.setText('待提醒')
                        reminder_item.setBackground(QColor("#ffffcc"))  # 黄色背景表示待提醒
                    else:
                        reminder_item.setText('已设置')
            else:
                reminder_item.setText('未设置')
            self.table.setItem(row, 6, reminder_item)
            
            # 创建时间
            created_at = datetime.strptime(task['created_at'], "%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 7, QTableWidgetItem(created_at.strftime("%Y-%m-%d %H:%M")))
    
    def _on_selection_changed(self):
        """选择变化处理"""
        selected_rows = self.table.selectedItems()
        has_selection = len(selected_rows) > 0
        
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
        if has_selection:
            self.current_task_id = selected_rows[0].data(Qt.ItemDataRole.UserRole)
        else:
            self.current_task_id = None
    
    def _on_add_clicked(self):
        """添加任务"""
        dialog = TaskDialog(self, self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()
            if not task_data['title']:
                QMessageBox.warning(self, "警告", "标题不能为空")
                return
                
            self.db.add_task(
                task_data['title'],
                task_data['description'],
                task_data['due_date'],
                task_data['priority'],
                '待处理',
                task_data['tags'],
                task_data['reminder'],
                task_data['reminder_hours']
            )
            self.load_tasks()
    
    def _on_edit_clicked(self):
        """编辑任务"""
        current_item = self.table.currentItem()
        if not current_item:
            return
            
        row = current_item.row()
        task_id = int(self.table.item(row, 0).text())
        task = self.db.get_task(task_id)
        
        dialog = TaskDialog(self, self.db, task)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            task_data = dialog.get_task_data()
            if not task_data['title']:
                QMessageBox.warning(self, "警告", "标题不能为空")
                return
                
            self.db.update_task(
                task_id,
                task_data['title'],
                task_data['description'],
                task_data['due_date'],
                task_data['priority'],
                task['status'],
                task_data['tags'],
                task_data['reminder'],
                task_data['reminder_hours']
            )
            self.load_tasks()
    
    def _on_delete_clicked(self):
        """删除按钮点击处理"""
        if not self.current_task_id:
            return
        
        reply = QMessageBox.question(
            self, "确认", "确定要删除这个任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_task(self.current_task_id)
            self.current_task_id = None
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.load_tasks()
    
    def _on_filter_changed(self, index):
        """过滤器改变时的处理"""
        self.load_tasks()
    
    def _schedule_next_reset(self):
        """安排下一次重置时间（每天凌晨00:00）"""
        now = datetime.now()
        next_reset = (now.replace(hour=0, minute=0, second=0, microsecond=0) + 
                     timedelta(days=1))
        delay = int((next_reset - now).total_seconds() * 1000)
        self.reset_timer.start(delay)

    def _reset_reminders(self):
        """重置提醒状态"""
        self.db.reset_task_reminders()
        self._schedule_next_reset()  # 安排下一次重置

    def _check_reminders(self):
        """检查任务提醒"""
        tasks = self.db.get_tasks_with_reminders()
        current_time = datetime.now()
        
        for task in tasks:
            try:
                reminder_time = datetime.strptime(task['reminder_time'], '%Y-%m-%d %H:%M:%S')
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
                
                # 如果当前时间在提醒时间和截止时间之间
                if current_time >= reminder_time and current_time < due_date:
                    QMessageBox.information(
                        self,
                        '任务提醒',
                        f'任务"{task["title"]}"将在{task["reminder_hours"]}小时后到期！\n'
                        f'截止时间：{task["due_date"]}\n'
                        f'优先级：{task["priority"]}\n'
                        f'描述：{task["description"] or "无"}'
                    )
                    # 更新提醒状态
                    self.db.update_task_reminder_sent(task['id'], True)
            except (ValueError, TypeError) as e:
                print(f"处理任务提醒时出错：{str(e)}")
                continue

    def _on_status_changed(self, task_id, new_status):
        """任务状态改变处理"""
        task = self.db.get_task(task_id)
        if not task:
            return
            
        # 如果任务已经是这个状态，不做任何操作
        if task['status'] == new_status:
            return
            
        # 如果任务已完成或已取消，记录完成时间
        completed_at = None
        if new_status in ['已完成', '已取消']:
            completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        # 更新任务状态
        self.db.update_task(
            task_id,
            task['title'],
            task['description'],
            task['due_date'],
            task['priority'],
            new_status,
            task['tags'],
            task.get('reminder_time') is not None,
            task.get('reminder_hours'),
            completed_at
        )
        self._update_task_table()

    def _create_status_menu(self, task_id):
        """创建状态菜单"""
        menu = QMenu(self)
        statuses = ['待处理', '进行中', '已完成', '已取消']
        
        task = self.db.get_task(task_id)
        if not task:
            return menu
            
        for status in statuses:
            action = menu.addAction(status)
            action.setCheckable(True)
            action.setChecked(task['status'] == status)
            action.triggered.connect(lambda checked, s=status: self._on_status_changed(task_id, s))
        
        return menu

    def _on_table_context_menu(self, pos):
        """表格右键菜单处理"""
        item = self.table.itemAt(pos)
        if not item:
            return
            
        row = item.row()
        task_id = int(self.table.item(row, 0).data(Qt.ItemDataRole.UserRole))
        
        menu = QMenu(self)
        
        # 编辑操作
        edit_action = menu.addAction('编辑')
        edit_action.triggered.connect(lambda: self._on_edit_clicked())
        
        # 状态子菜单
        status_menu = self._create_status_menu(task_id)
        menu.addMenu('更改状态').setMenu(status_menu)
        
        # 删除操作
        delete_action = menu.addAction('删除')
        delete_action.triggered.connect(lambda: self._on_delete_clicked())
        
        menu.exec(self.table.viewport().mapToGlobal(pos)) 

    def _update_task_stats(self):
        stats = self.db.get_task_stats()
        
        self.total_label.setText(f"总任务数: {stats['total']}")
        self.pending_label.setText(f"待处理: {stats['pending']}")
        self.in_progress_label.setText(f"进行中: {stats['in_progress']}")
        self.completed_label.setText(f"已完成: {stats['completed']}")
        self.cancelled_label.setText(f"已取消: {stats['cancelled']}")
        
        # 设置逾期任务数的颜色
        overdue_text = f"已逾期: {stats['overdue']}"
        self.overdue_label.setText(overdue_text)
        if stats['overdue'] > 0:
            self.overdue_label.setStyleSheet("color: red;")
        else:
            self.overdue_label.setStyleSheet("")
            
        # 设置本周完成任务数的颜色
        completed_week_text = f"本周完成: {stats['completed_this_week']}"
        self.completed_week_label.setText(completed_week_text)
        if stats['completed_this_week'] > 0:
            self.completed_week_label.setStyleSheet("color: green;")
        else:
            self.completed_week_label.setStyleSheet("")
            
        # 格式化平均完成时间
        avg_time = stats.get('avg_completion_time', 0)
        if avg_time:
            avg_time = round(avg_time, 1)
        self.avg_time_label.setText(f"平均完成时间: {avg_time}小时")