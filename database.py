import sqlite3
import os
from datetime import datetime, timedelta
import json

class Database:
    def __init__(self, db_file="timemanager.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """连接到SQLite数据库"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        """创建数据库表"""
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT "#3498db"
            );

            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                description TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            );

            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                mood TEXT,
                weather TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                due_date DATE,
                priority TEXT CHECK(priority IN ('低', '中', '高')) DEFAULT '中',
                status TEXT CHECK(status IN ('待处理', '进行中', '已完成', '已取消')) DEFAULT '待处理',
                tags TEXT,
                reminder_time DATETIME,
                reminder_hours INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME,
                completed_at DATETIME,
                reminder_sent INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS timer_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_name TEXT NOT NULL,
                duration INTEGER NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        self.conn.commit()
    
    # 类别相关方法
    def add_category(self, name, color="#3498db"):
        """添加新的时间类别"""
        try:
            self.cursor.execute("INSERT INTO categories (name, color) VALUES (?, ?)", (name, color))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_categories(self):
        """获取所有时间类别"""
        self.cursor.execute("SELECT * FROM categories ORDER BY name")
        return self.cursor.fetchall()
    
    def update_category(self, category_id, name, color):
        """更新时间类别"""
        self.cursor.execute("UPDATE categories SET name = ?, color = ? WHERE id = ?", 
                           (name, color, category_id))
        self.conn.commit()
    
    def delete_category(self, category_id):
        """删除时间类别"""
        self.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.commit()
    
    # 时间记录相关方法
    def start_time_entry(self, category_id, description=""):
        """开始一个新的时间记录"""
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO time_entries (category_id, start_time, description) VALUES (?, ?, ?)",
            (category_id, start_time, description)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def end_time_entry(self, entry_id):
        """结束一个时间记录"""
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "UPDATE time_entries SET end_time = ? WHERE id = ?",
            (end_time, entry_id)
        )
        self.conn.commit()
    
    def get_active_time_entry(self):
        """获取当前活动的时间记录"""
        self.cursor.execute(
            "SELECT * FROM time_entries WHERE end_time IS NULL ORDER BY start_time DESC LIMIT 1"
        )
        return self.cursor.fetchone()
    
    def get_time_entries(self, start_date=None, end_date=None, category_id=None):
        """获取时间记录"""
        query = "SELECT te.*, c.name as category_name, c.color as category_color " \
                "FROM time_entries te " \
                "LEFT JOIN categories c ON te.category_id = c.id " \
                "WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND te.start_time >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND te.start_time <= ?"
            params.append(end_date)
        
        if category_id:
            query += " AND te.category_id = ?"
            params.append(category_id)
        
        query += " ORDER BY te.start_time DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def add_time_entry(self, category_id, start_time, end_time, description=""):
        """手动添加一个时间记录"""
        self.cursor.execute(
            "INSERT INTO time_entries (category_id, start_time, end_time, description) VALUES (?, ?, ?, ?)",
            (category_id, start_time, end_time, description)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_time_entry(self, entry_id, category_id, start_time, end_time, description=""):
        """更新时间记录"""
        self.cursor.execute(
            "UPDATE time_entries SET category_id = ?, start_time = ?, end_time = ?, description = ? WHERE id = ?",
            (category_id, start_time, end_time, description, entry_id)
        )
        self.conn.commit()
    
    def delete_time_entry(self, entry_id):
        """删除时间记录"""
        self.cursor.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
        self.conn.commit()
    
    def get_time_entry(self, entry_id):
        """获取单个时间记录"""
        self.cursor.execute("""
            SELECT te.*, c.name as category_name, c.color as category_color
            FROM time_entries te
            JOIN categories c ON te.category_id = c.id
            WHERE te.id = ?
        """, (entry_id,))
        return self.cursor.fetchone()
    
    # 日记相关方法
    def add_journal_entry(self, date, title, content, mood=None, weather=None, tags=None):
        """添加日记条目"""
        tags_json = None
        if tags:
            tags_json = json.dumps(tags, ensure_ascii=False)
        
        self.cursor.execute(
            "INSERT INTO journal_entries (date, title, content, mood, weather, tags) VALUES (?, ?, ?, ?, ?, ?)",
            (date, title, content, mood, weather, tags_json)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_journal_entry(self, entry_id, title, content, mood=None, weather=None, tags=None):
        """更新日记条目"""
        tags_json = None
        if tags:
            tags_json = json.dumps(tags, ensure_ascii=False)
        
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "UPDATE journal_entries SET title = ?, content = ?, mood = ?, weather = ?, tags = ?, updated_at = ? WHERE id = ?",
            (title, content, mood, weather, tags_json, updated_at, entry_id)
        )
        self.conn.commit()
    
    def get_journal_entries(self, start_date=None, end_date=None):
        """获取日记条目"""
        query = "SELECT * FROM journal_entries WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC"
        
        self.cursor.execute(query, params)
        entries = self.cursor.fetchall()
        
        # 将sqlite3.Row对象转换为字典并处理tags
        result = []
        for entry in entries:
            entry_dict = dict(entry)
            if entry_dict['tags']:
                try:
                    entry_dict['tags'] = json.loads(entry_dict['tags'])
                except json.JSONDecodeError:
                    entry_dict['tags'] = []
            else:
                entry_dict['tags'] = []
            result.append(entry_dict)
        
        return result
    
    def get_journal_entry(self, entry_id):
        """获取单个日记条目"""
        self.cursor.execute("SELECT * FROM journal_entries WHERE id = ?", (entry_id,))
        entry = self.cursor.fetchone()
        
        if entry:
            # 将sqlite3.Row对象转换为字典
            entry_dict = dict(entry)
            if entry_dict['tags']:
                try:
                    entry_dict['tags'] = json.loads(entry_dict['tags'])
                except json.JSONDecodeError:
                    entry_dict['tags'] = []
            else:
                entry_dict['tags'] = []
            return entry_dict
        return None
    
    def delete_journal_entry(self, entry_id):
        """删除日记条目"""
        self.cursor.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))
        self.conn.commit()
    
    # 任务相关方法
    def add_task(self, title, description, due_date, priority, status, tags, reminder, reminder_hours):
        """添加任务"""
        reminder_time = None
        if reminder and due_date:
            due_date_obj = datetime.strptime(str(due_date), '%Y-%m-%d')
            reminder_time = (due_date_obj - timedelta(hours=reminder_hours)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 确保标签是JSON字符串
        if isinstance(tags, list):
            tags_json = json.dumps(tags, ensure_ascii=False)
        else:
            tags_json = tags

        self.cursor.execute("""
            INSERT INTO tasks (
                title, description, due_date, priority, status, tags,
                reminder_time, reminder_hours, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, description, str(due_date), priority, status, tags_json,
            reminder_time, reminder_hours if reminder else None,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_task(self, task_id, title, description, due_date, priority, status, tags, reminder, reminder_hours, completed_at=None):
        """更新任务"""
        reminder_time = None
        if reminder and due_date:
            due_date_obj = datetime.strptime(str(due_date), '%Y-%m-%d')
            reminder_time = (due_date_obj - timedelta(hours=reminder_hours)).strftime('%Y-%m-%d %H:%M:%S')

        # 确保标签是JSON字符串
        if isinstance(tags, list):
            tags_json = json.dumps(tags, ensure_ascii=False)
        else:
            tags_json = tags

        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("""
            UPDATE tasks
            SET title = ?, description = ?, due_date = ?, priority = ?, status = ?, 
                tags = ?, reminder_time = ?, reminder_hours = ?, updated_at = ?,
                completed_at = ?, reminder_sent = ?
            WHERE id = ?
        """, (
            title, description, str(due_date), priority, status, tags_json,
            reminder_time, reminder_hours if reminder else None,
            updated_at, completed_at,
            1 if status in ['已完成', '已取消'] else 0,
            task_id
        ))
        self.conn.commit()
    
    def get_tasks(self, status=None, due_before=None):
        """获取任务列表"""
        query = """
            SELECT id, title, description, due_date, priority, status, tags,
                   reminder_time, reminder_hours, created_at, updated_at
            FROM tasks WHERE 1=1
        """
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if due_before:
            query += " AND due_date <= ?"
            params.append(due_before)

        query += " ORDER BY CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 WHEN '低' THEN 3 END, due_date ASC"

        self.cursor.execute(query, params)
        tasks = self.cursor.fetchall()
        result = []
        for task in tasks:
            task_dict = dict(task)
            if task_dict['tags']:
                try:
                    task_dict['tags'] = json.loads(task_dict['tags'])
                except json.JSONDecodeError:
                    task_dict['tags'] = []
            else:
                task_dict['tags'] = []
            result.append(task_dict)
        return result
    
    def get_task(self, task_id):
        """获取单个任务"""
        self.cursor.execute("""
            SELECT id, title, description, due_date, priority, status, tags,
                   reminder_time, reminder_hours, created_at, updated_at
            FROM tasks
            WHERE id = ?
        """, (task_id,))
        task = self.cursor.fetchone()
        if task:
            task_dict = dict(task)
            if task_dict['tags']:
                try:
                    task_dict['tags'] = json.loads(task_dict['tags'])
                except json.JSONDecodeError:
                    task_dict['tags'] = []
            else:
                task_dict['tags'] = []
            return task_dict
        return None
    
    def delete_task(self, task_id):
        """删除任务"""
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
    
    def update_task_reminder_sent(self, task_id, sent):
        """更新任务提醒状态"""
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("""
            UPDATE tasks
            SET reminder_sent = ?, updated_at = ?
            WHERE id = ?
        """, (1 if sent else 0, updated_at, task_id))
        self.conn.commit()
    
    def get_tasks_with_reminders(self):
        """获取需要提醒的任务"""
        self.cursor.execute("""
            SELECT id, title, description, due_date, priority, status, tags,
                   reminder_time, reminder_hours, created_at, updated_at, reminder_sent
            FROM tasks
            WHERE status NOT IN ('已完成', '已取消')
            AND reminder_time IS NOT NULL
            AND reminder_hours IS NOT NULL
            AND reminder_sent = 0
            AND due_date >= date('now')
            ORDER BY due_date ASC
        """)
        tasks = self.cursor.fetchall()
        result = []
        for task in tasks:
            task_dict = dict(task)
            if task_dict['tags']:
                try:
                    task_dict['tags'] = json.loads(task_dict['tags'])
                except json.JSONDecodeError:
                    task_dict['tags'] = []
            else:
                task_dict['tags'] = []
            result.append(task_dict)
        return result

    def reset_task_reminders(self):
        """重置所有任务的提醒状态"""
        updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("""
            UPDATE tasks
            SET reminder_sent = 0, updated_at = ?
            WHERE status NOT IN ('已完成', '已取消')
            AND reminder_time IS NOT NULL
            AND reminder_hours IS NOT NULL
            AND due_date >= date('now')
        """, (updated_at,))
        self.conn.commit()
    
    def get_task_stats(self):
        """获取任务统计信息"""
        # 获取总任务数
        self.cursor.execute("SELECT COUNT(*) FROM tasks")
        total = self.cursor.fetchone()[0]
        
        # 获取各状态任务数
        self.cursor.execute("""
            SELECT status, COUNT(*)
            FROM tasks
            GROUP BY status
        """)
        status_counts = dict(self.cursor.fetchall())
        
        # 获取逾期任务数
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE due_date < date('now')
            AND status NOT IN ('已完成', '已取消')
        """)
        overdue = self.cursor.fetchone()[0]
        
        # 获取本周完成的任务数
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM tasks
            WHERE completed_at >= date('now', '-7 days')
            AND status = '已完成'
        """)
        completed_this_week = self.cursor.fetchone()[0]
        
        # 获取平均完成时间（小时）
        self.cursor.execute("""
            SELECT AVG(
                CAST(
                    (julianday(completed_at) - julianday(created_at)) * 24
                    AS INTEGER
                )
            )
            FROM tasks
            WHERE status = '已完成'
            AND completed_at IS NOT NULL
        """)
        avg_completion_time = self.cursor.fetchone()[0]
        
        return {
            'total': total,
            'pending': status_counts.get('待处理', 0),
            'in_progress': status_counts.get('进行中', 0),
            'completed': status_counts.get('已完成', 0),
            'cancelled': status_counts.get('已取消', 0),
            'overdue': overdue,
            'completed_this_week': completed_this_week,
            'avg_completion_time': round(avg_completion_time) if avg_completion_time else 0
        }
    
    # 计时器事件相关方法
    def add_timer_event(self, event_name, duration, start_time, end_time):
        """添加计时器事件记录"""
        self.cursor.execute("""
            INSERT INTO timer_events (event_name, duration, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """, (event_name, duration, start_time, end_time))
        self.conn.commit()

    def get_timer_events(self, start_date=None, end_date=None):
        """获取计时器事件记录"""
        query = "SELECT * FROM timer_events"
        params = []
        
        if start_date and end_date:
            query += " WHERE date(start_time) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += " ORDER BY start_time DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_timer_event_stats(self, start_date=None, end_date=None):
        """获取计时器事件统计信息"""
        query = """
            SELECT 
                event_name,
                COUNT(*) as count,
                SUM(duration) as total_duration,
                AVG(duration) as avg_duration
            FROM timer_events
        """
        params = []
        
        if start_date and end_date:
            query += " WHERE date(start_time) BETWEEN ? AND ?"
            params.extend([start_date, end_date])
        
        query += " GROUP BY event_name"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def delete_timer_event(self, event_id):
        """删除计时器事件"""
        self.cursor.execute("DELETE FROM timer_events WHERE id = ?", (event_id,))
        self.conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close() 