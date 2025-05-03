from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTextEdit, QListWidget,
                             QListWidgetItem, QDateEdit, QMessageBox, QFrame,
                             QDialog, QFormLayout, QComboBox, QCalendarWidget,
                             QCheckBox, QFileDialog, QColorDialog, QFontDialog,
                             QToolBar, QStatusBar, QSplitter, QScrollArea)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QColor, QFont, QTextCharFormat, QTextCursor, QAction
from datetime import datetime
import os
import json
import html

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
        self.update_tag_list()
        layout.addWidget(self.tag_list)
        
        # 添加标签
        add_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("输入新标签")
        add_button = QPushButton("添加")
        add_button.clicked.connect(self.add_tag)
        
        add_layout.addWidget(self.tag_input)
        add_layout.addWidget(add_button)
        layout.addLayout(add_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        delete_button = QPushButton("删除选中")
        delete_button.clicked.connect(self.delete_tag)
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(delete_button)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
    
    def update_tag_list(self):
        """更新标签列表"""
        self.tag_list.clear()
        for tag in self.tags:
            self.tag_list.addItem(tag)
    
    def add_tag(self):
        """添加标签"""
        tag = self.tag_input.text().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.update_tag_list()
            self.tag_input.clear()
    
    def delete_tag(self):
        """删除标签"""
        current_item = self.tag_list.currentItem()
        if current_item:
            tag = current_item.text()
            self.tags.remove(tag)
            self.update_tag_list()
    
    def get_tags(self):
        """获取标签列表"""
        return self.tags

class JournalEntryDialog(QDialog):
    """日记编辑对话框"""
    
    def __init__(self, parent=None, entry=None):
        super().__init__(parent)
        self.entry = entry
        self.tags = entry['tags'] if entry else []
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑日记")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # 表单布局
        form_layout = QFormLayout()
        
        # 日期
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        if self.entry:
            self.date_edit.setDate(QDate.fromString(self.entry['date'], "yyyy-MM-dd"))
        else:
            self.date_edit.setDate(QDate.currentDate())
        form_layout.addRow("日期:", self.date_edit)
        
        # 标题
        self.title_edit = QLineEdit()
        if self.entry:
            self.title_edit.setText(self.entry['title'] or "")
        form_layout.addRow("标题:", self.title_edit)
        
        # 心情
        self.mood_combo = QComboBox()
        self.mood_combo.addItems(["开心", "平静", "疲惫", "焦虑", "兴奋", "其他"])
        if self.entry and self.entry['mood']:
            index = self.mood_combo.findText(self.entry['mood'])
            if index >= 0:
                self.mood_combo.setCurrentIndex(index)
        form_layout.addRow("心情:", self.mood_combo)
        
        # 天气
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["晴朗", "多云", "阴天", "小雨", "大雨", "雪", "其他"])
        if self.entry and self.entry['weather']:
            index = self.weather_combo.findText(self.entry['weather'])
            if index >= 0:
                self.weather_combo.setCurrentIndex(index)
        form_layout.addRow("天气:", self.weather_combo)
        
        # 标签
        tag_layout = QHBoxLayout()
        self.tag_label = QLabel(", ".join(self.tags) if self.tags else "无标签")
        tag_button = QPushButton("管理标签")
        tag_button.clicked.connect(self.manage_tags)
        
        tag_layout.addWidget(self.tag_label)
        tag_layout.addWidget(tag_button)
        form_layout.addRow("标签:", tag_layout)
        
        layout.addLayout(form_layout)
        
        # 内容编辑工具栏
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # 加粗
        bold_action = QAction("加粗", self)
        bold_action.triggered.connect(lambda: self.format_text("bold"))
        toolbar.addAction(bold_action)
        
        # 斜体
        italic_action = QAction("斜体", self)
        italic_action.triggered.connect(lambda: self.format_text("italic"))
        toolbar.addAction(italic_action)
        
        # 下划线
        underline_action = QAction("下划线", self)
        underline_action.triggered.connect(lambda: self.format_text("underline"))
        toolbar.addAction(underline_action)
        
        toolbar.addSeparator()
        
        # 字体
        font_action = QAction("字体", self)
        font_action.triggered.connect(self.change_font)
        toolbar.addAction(font_action)
        
        # 颜色
        color_action = QAction("颜色", self)
        color_action.triggered.connect(self.change_color)
        toolbar.addAction(color_action)
        
        layout.addWidget(toolbar)
        
        # 内容
        self.content_edit = QTextEdit()
        if self.entry:
            self.content_edit.setHtml(self.entry['content'] or "")
        layout.addWidget(self.content_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def manage_tags(self):
        """管理标签"""
        dialog = TagDialog(self, self.tags)
        if dialog.exec():
            self.tags = dialog.get_tags()
            self.tag_label.setText(", ".join(self.tags) if self.tags else "无标签")
    
    def format_text(self, format_type):
        """格式化文本"""
        cursor = self.content_edit.textCursor()
        format = QTextCharFormat()
        
        if format_type == "bold":
            format.setFontWeight(QFont.Weight.Bold if cursor.charFormat().fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal)
        elif format_type == "italic":
            format.setFontItalic(not cursor.charFormat().fontItalic())
        elif format_type == "underline":
            format.setFontUnderline(not cursor.charFormat().fontUnderline())
        
        cursor.mergeCharFormat(format)
    
    def change_font(self):
        """更改字体"""
        cursor = self.content_edit.textCursor()
        current_font = cursor.charFormat().font()
        
        font, ok = QFontDialog.getFont(current_font, self, "选择字体")
        if ok:
            format = QTextCharFormat()
            format.setFont(font)
            cursor.mergeCharFormat(format)
    
    def change_color(self):
        """更改颜色"""
        cursor = self.content_edit.textCursor()
        current_color = cursor.charFormat().foreground().color()
        
        color = QColorDialog.getColor(current_color, self, "选择颜色")
        if color.isValid():
            format = QTextCharFormat()
            format.setForeground(color)
            cursor.mergeCharFormat(format)
    
    def get_entry_data(self):
        """获取日记数据"""
        return {
            'date': self.date_edit.date().toString("yyyy-MM-dd"),
            'title': self.title_edit.text().strip(),
            'mood': self.mood_combo.currentText(),
            'weather': self.weather_combo.currentText(),
            'tags': self.tags,
            'content': self.content_edit.toHtml()
        }

class JournalWidget(QWidget):
    """日记界面组件"""
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.current_entry_id = None
        self.filtered_entries = []
        
        self.init_ui()
        self.load_entries()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 左侧：日历和日记列表
        left_layout = QVBoxLayout()
        
        # 日历
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_calendar_clicked)
        left_layout.addWidget(self.calendar)
        
        # 日记列表标题和按钮
        list_header_layout = QHBoxLayout()
        list_label = QLabel("日记列表")
        list_label.setStyleSheet("font-weight: bold;")
        
        self.add_button = QPushButton("新建")
        self.add_button.setIcon(QIcon(os.path.join("icons", "add.png")))
        self.add_button.clicked.connect(self._on_add_clicked)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.setIcon(QIcon(os.path.join("icons", "delete.png")))
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.delete_button.setEnabled(False)
        
        list_header_layout.addWidget(list_label)
        list_header_layout.addStretch()
        list_header_layout.addWidget(self.add_button)
        list_header_layout.addWidget(self.delete_button)
        
        left_layout.addLayout(list_header_layout)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键词搜索")
        self.search_edit.textChanged.connect(self.filter_entries)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        left_layout.addLayout(search_layout)
        
        # 标签筛选
        tag_layout = QHBoxLayout()
        tag_label = QLabel("标签:")
        self.tag_combo = QComboBox()
        self.tag_combo.addItem("全部")
        self.tag_combo.currentIndexChanged.connect(self.filter_entries)
        
        tag_layout.addWidget(tag_label)
        tag_layout.addWidget(self.tag_combo)
        
        left_layout.addLayout(tag_layout)
        
        # 日记列表
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_entry_selected)
        left_layout.addWidget(self.list_widget)
        
        # 日期筛选
        filter_layout = QHBoxLayout()
        filter_label = QLabel("日期筛选:")
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        
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
        
        left_layout.addLayout(filter_layout)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        self.export_html_button = QPushButton("导出为HTML")
        self.export_html_button.clicked.connect(self._on_export_html_clicked)
        self.export_text_button = QPushButton("导出为文本")
        self.export_text_button.clicked.connect(self._on_export_text_clicked)
        
        export_layout.addWidget(self.export_html_button)
        export_layout.addWidget(self.export_text_button)
        export_layout.addStretch()
        
        left_layout.addLayout(export_layout)
        
        # 创建左侧部件
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMaximumWidth(300)
        
        # 右侧：日记详情
        right_layout = QVBoxLayout()
        
        # 日记详情标题和按钮
        detail_header_layout = QHBoxLayout()
        detail_label = QLabel("日记详情")
        detail_label.setStyleSheet("font-weight: bold;")
        
        self.edit_button = QPushButton("编辑")
        self.edit_button.setIcon(QIcon(os.path.join("icons", "edit.png")))
        self.edit_button.clicked.connect(self._on_edit_clicked)
        self.edit_button.setEnabled(False)
        
        detail_header_layout.addWidget(detail_label)
        detail_header_layout.addStretch()
        detail_header_layout.addWidget(self.edit_button)
        
        right_layout.addLayout(detail_header_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        right_layout.addWidget(line)
        
        # 日记详情
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        
        # 日期
        self.date_label = QLabel()
        self.date_label.setStyleSheet("font-weight: bold;")
        detail_layout.addWidget(self.date_label)
        
        # 标题
        self.title_label = QLabel()
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        detail_layout.addWidget(self.title_label)
        
        # 心情和天气
        mood_weather_layout = QHBoxLayout()
        self.mood_label = QLabel()
        self.weather_label = QLabel()
        
        mood_weather_layout.addWidget(self.mood_label)
        mood_weather_layout.addWidget(self.weather_label)
        mood_weather_layout.addStretch()
        
        detail_layout.addLayout(mood_weather_layout)
        
        # 标签
        self.tag_label = QLabel()
        detail_layout.addWidget(self.tag_label)
        
        # 分隔线
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        detail_layout.addWidget(line2)
        
        # 内容
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_label.setTextFormat(Qt.TextFormat.RichText)
        
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.content_label)
        scroll_area.setWidgetResizable(True)
        
        detail_layout.addWidget(scroll_area)
        
        detail_layout.addStretch()
        right_layout.addWidget(self.detail_widget)
        
        # 创建右侧部件
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # 使用分割器组合左右部件
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter)
    
    def load_entries(self, start_date=None, end_date=None):
        """加载日记条目"""
        if not start_date:
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        if not end_date:
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        entries = self.db.get_journal_entries(start_date, end_date)
        self.filtered_entries = entries
        
        # 更新标签下拉框
        all_tags = set()
        for entry in entries:
            all_tags.update(entry['tags'])
        
        self.tag_combo.clear()
        self.tag_combo.addItem("全部")
        for tag in sorted(all_tags):
            self.tag_combo.addItem(tag)
        
        self.update_entry_list()
    
    def update_entry_list(self):
        """更新日记列表"""
        self.list_widget.clear()
        
        for entry in self.filtered_entries:
            item = QListWidgetItem()
            
            # 格式化显示
            date_str = entry['date']
            title = entry['title'] or "无标题"
            mood = entry['mood'] or "无心情"
            
            item.setText(f"{date_str} - {title} ({mood})")
            item.setData(Qt.ItemDataRole.UserRole, entry['id'])
            
            self.list_widget.addItem(item)
    
    def filter_entries(self):
        """筛选日记条目"""
        search_text = self.search_edit.text().lower()
        selected_tag = self.tag_combo.currentText()
        
        filtered = []
        for entry in self.db.get_journal_entries(
            self.start_date_edit.date().toString("yyyy-MM-dd"),
            self.end_date_edit.date().toString("yyyy-MM-dd")
        ):
            # 搜索文本匹配
            if search_text and not (
                search_text in (entry['title'] or "").lower() or
                search_text in (entry['content'] or "").lower()
            ):
                continue
            
            # 标签匹配
            if selected_tag != "全部" and selected_tag not in entry['tags']:
                continue
            
            filtered.append(entry)
        
        self.filtered_entries = filtered
        self.update_entry_list()
    
    def on_calendar_clicked(self, date):
        """日历点击处理"""
        date_str = date.toString("yyyy-MM-dd")
        self.start_date_edit.setDate(date)
        self.end_date_edit.setDate(date)
        self.load_entries(date_str, date_str)
    
    def _on_entry_selected(self, current, previous):
        """日记条目选择处理"""
        if not current:
            self.current_entry_id = None
            self._clear_detail()
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
        
        self.current_entry_id = current.data(Qt.ItemDataRole.UserRole)
        entry = self.db.get_journal_entry(self.current_entry_id)
        
        if entry:
            self._update_detail(entry)
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
    
    def _update_detail(self, entry):
        """更新日记详情"""
        self.date_label.setText(f"日期: {entry['date']}")
        self.title_label.setText(entry['title'] or "无标题")
        self.mood_label.setText(f"心情: {entry['mood'] or '无'}")
        self.weather_label.setText(f"天气: {entry['weather'] or '无'}")
        self.tag_label.setText(f"标签: {', '.join(entry['tags']) if entry['tags'] else '无'}")
        self.content_label.setText(entry['content'] or "无内容")
    
    def _clear_detail(self):
        """清空日记详情"""
        self.date_label.setText("")
        self.title_label.setText("")
        self.mood_label.setText("")
        self.weather_label.setText("")
        self.tag_label.setText("")
        self.content_label.setText("")
    
    def _on_add_clicked(self):
        """新建按钮点击处理"""
        dialog = JournalEntryDialog(self)
        if dialog.exec():
            entry_data = dialog.get_entry_data()
            if not entry_data['title'] and not entry_data['content']:
                QMessageBox.warning(self, "警告", "标题和内容不能同时为空")
                return
            
            self.db.add_journal_entry(
                entry_data['date'],
                entry_data['title'],
                entry_data['content'],
                entry_data['mood'],
                entry_data['weather'],
                entry_data['tags']
            )
            self.load_entries()
    
    def _on_edit_clicked(self):
        """编辑按钮点击处理"""
        if not self.current_entry_id:
            return
        
        entry = self.db.get_journal_entry(self.current_entry_id)
        if not entry:
            return
        
        dialog = JournalEntryDialog(self, entry)
        if dialog.exec():
            entry_data = dialog.get_entry_data()
            if not entry_data['title'] and not entry_data['content']:
                QMessageBox.warning(self, "警告", "标题和内容不能同时为空")
                return
            
            self.db.update_journal_entry(
                self.current_entry_id,
                entry_data['title'],
                entry_data['content'],
                entry_data['mood'],
                entry_data['weather'],
                entry_data['tags']
            )
            self.load_entries()
    
    def _on_delete_clicked(self):
        """删除按钮点击处理"""
        if not self.current_entry_id:
            return
        
        reply = QMessageBox.question(
            self, "确认", "确定要删除这篇日记吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db.delete_journal_entry(self.current_entry_id)
            self.current_entry_id = None
            self._clear_detail()
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.load_entries()
    
    def _on_filter_clicked(self):
        """筛选按钮点击处理"""
        self.load_entries()
    
    def _on_export_html_clicked(self):
        """导出为HTML按钮点击处理"""
        if not self.filtered_entries:
            QMessageBox.information(self, "提示", "没有可导出的日记")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为HTML", "", "HTML文件 (*.html)"
        )
        
        if not file_path:
            return
        
        if not file_path.endswith(".html"):
            file_path += ".html"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>我的日记</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        .entry { margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom: 20px; }
                        .date { font-weight: bold; color: #333; }
                        .title { font-size: 18px; font-weight: bold; margin: 10px 0; }
                        .meta { color: #666; margin-bottom: 10px; }
                        .content { line-height: 1.6; }
                    </style>
                </head>
                <body>
                    <h1>我的日记</h1>
                """)
                
                for entry in self.filtered_entries:
                    f.write(f"""
                    <div class="entry">
                        <div class="date">{entry['date']}</div>
                        <div class="title">{html.escape(entry['title'] or "无标题")}</div>
                        <div class="meta">
                            心情: {html.escape(entry['mood'] or "无")} | 
                            天气: {html.escape(entry['weather'] or "无")} | 
                            标签: {html.escape(", ".join(entry['tags']) if entry['tags'] else "无")}
                        </div>
                        <div class="content">{entry['content'] or "无内容"}</div>
                    </div>
                    """)
                
                f.write("""
                </body>
                </html>
                """)
            
            QMessageBox.information(self, "成功", f"日记已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
    
    def _on_export_text_clicked(self):
        """导出为文本按钮点击处理"""
        if not self.filtered_entries:
            QMessageBox.information(self, "提示", "没有可导出的日记")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出为文本", "", "文本文件 (*.txt)"
        )
        
        if not file_path:
            return
        
        if not file_path.endswith(".txt"):
            file_path += ".txt"
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("我的日记\n\n")
                
                for entry in self.filtered_entries:
                    f.write(f"日期: {entry['date']}\n")
                    f.write(f"标题: {entry['title'] or '无标题'}\n")
                    f.write(f"心情: {entry['mood'] or '无'}\n")
                    f.write(f"天气: {entry['weather'] or '无'}\n")
                    f.write(f"标签: {', '.join(entry['tags']) if entry['tags'] else '无'}\n")
                    f.write("\n")
                    
                    # 将HTML内容转换为纯文本
                    content = entry['content'] or "无内容"
                    # 这里可以添加HTML到纯文本的转换逻辑
                    
                    f.write(f"{content}\n")
                    f.write("\n" + "-"*50 + "\n\n")
            
            QMessageBox.information(self, "成功", f"日记已成功导出到 {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}") 