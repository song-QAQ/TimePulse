import os
import csv
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

class TimeUtils:
    @staticmethod
    def format_duration(seconds):
        """将秒数格式化为时:分:秒格式"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def format_datetime(dt):
        """格式化日期时间为字符串"""
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def parse_datetime(dt_str):
        """将字符串解析为日期时间对象"""
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_date_range(days=7):
        """获取日期范围"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return start_date, end_date
    
    @staticmethod
    def calculate_duration(start_time, end_time):
        """计算两个时间点之间的持续时间（秒）"""
        if isinstance(start_time, str):
            start_time = TimeUtils.parse_datetime(start_time)
        if isinstance(end_time, str):
            end_time = TimeUtils.parse_datetime(end_time)
        
        duration = (end_time - start_time).total_seconds()
        return max(0, int(duration))
    
    @staticmethod
    def export_time_entries_to_csv(time_entries, filename):
        """将时间记录导出为CSV文件"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'category', 'start_time', 'end_time', 'duration', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entry in time_entries:
                start_time = TimeUtils.parse_datetime(entry['start_time'])
                end_time = TimeUtils.parse_datetime(entry['end_time']) if entry['end_time'] else datetime.now()
                duration = TimeUtils.calculate_duration(start_time, end_time)
                
                writer.writerow({
                    'id': entry['id'],
                    'category': entry['category_name'],
                    'start_time': entry['start_time'],
                    'end_time': entry['end_time'] if entry['end_time'] else '进行中',
                    'duration': TimeUtils.format_duration(duration),
                    'description': entry['description'] or ''
                })
    
    @staticmethod
    def export_time_entries_to_excel(time_entries, filename):
        """将时间记录导出为Excel文件"""
        data = []
        for entry in time_entries:
            start_time = TimeUtils.parse_datetime(entry['start_time'])
            end_time = TimeUtils.parse_datetime(entry['end_time']) if entry['end_time'] else datetime.now()
            duration = TimeUtils.calculate_duration(start_time, end_time)
            
            data.append({
                'ID': entry['id'],
                '类别': entry['category_name'],
                '开始时间': entry['start_time'],
                '结束时间': entry['end_time'] if entry['end_time'] else '进行中',
                '持续时间': TimeUtils.format_duration(duration),
                '描述': entry['description'] or ''
            })
        
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
    
    @staticmethod
    def create_time_distribution_chart(time_entries, output_file=None):
        """创建时间分布图表"""
        # 按类别汇总时间
        category_times = {}
        for entry in time_entries:
            if entry['end_time']:
                category = entry['category_name']
                start_time = TimeUtils.parse_datetime(entry['start_time'])
                end_time = TimeUtils.parse_datetime(entry['end_time'])
                duration = TimeUtils.calculate_duration(start_time, end_time)
                
                if category in category_times:
                    category_times[category] += duration
                else:
                    category_times[category] = duration
        
        # 准备数据
        categories = list(category_times.keys())
        times = [category_times[cat] / 3600 for cat in categories]  # 转换为小时
        
        # 创建图表
        plt.figure(figsize=(10, 6))
        colors = [to_rgba(entry['category_color'], 0.7) for entry in time_entries if entry['category_name'] in categories]
        
        plt.pie(times, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.axis('equal')
        plt.title('时间分布')
        
        if output_file:
            plt.savefig(output_file)
            plt.close()
        else:
            plt.show()
    
    @staticmethod
    def create_daily_time_chart(time_entries, days=7, output_file=None):
        """创建每日时间使用图表"""
        # 获取日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # 按日期和类别汇总时间
        daily_times = {}
        for entry in time_entries:
            if entry['end_time']:
                start_time = TimeUtils.parse_datetime(entry['start_time'])
                end_time = TimeUtils.parse_datetime(entry['end_time'])
                
                if start_time.date() >= start_date.date() and start_time.date() <= end_date.date():
                    date_str = start_time.strftime("%Y-%m-%d")
                    category = entry['category_name']
                    duration = TimeUtils.calculate_duration(start_time, end_time) / 3600  # 转换为小时
                    
                    if date_str not in daily_times:
                        daily_times[date_str] = {}
                    
                    if category in daily_times[date_str]:
                        daily_times[date_str][category] += duration
                    else:
                        daily_times[date_str][category] = duration
        
        # 准备数据
        dates = sorted(daily_times.keys())
        categories = list(set(cat for day in daily_times.values() for cat in day.keys()))
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        
        # 为每个类别创建堆叠柱状图
        bottom = [0] * len(dates)
        for category in categories:
            values = [daily_times[date].get(category, 0) for date in dates]
            plt.bar(dates, values, bottom=bottom, label=category)
            bottom = [b + v for b, v in zip(bottom, values)]
        
        plt.xlabel('日期')
        plt.ylabel('小时')
        plt.title(f'每日时间使用 ({days}天)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
            plt.close()
        else:
            plt.show() 