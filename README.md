# TimePulse

![版本](https://img.shields.io/badge/版本-1.0.0-blue) ![许可证](https://img.shields.io/badge/许可证-MIT-green) ![Python版本](https://img.shields.io/badge/Python-3.8%2B-yellow)

基于PyQt6的多功能时间管理应用，集成计时器、时间记录、日记和任务管理功能，帮助用户高效追踪和管理时间，提升工作效率与生活质量。支持数据可视化分析和多种格式导出，注：作者可以算是一个小白，所以有很多不足之处，希望海涵
A PyQt6-based multi-functional time management application.Note: The author is still a novice developer, so there may be imperfections in the project. Your kind understanding is appreciated.

// 看前提醒，以下是我把代码丢给人工智能，在他写的文档的基础上面，我再修改的readme文件。这个项目确实还有一些缺陷存在，比如时间记录的类别栏还无法选择，严格上讲，这个项目算是一个半成品，但是已经可以使用并且有了对应功能了，我也经常使用他来记录，我便想上传上来分享给大家并且接受大家的建议和批评。我其实算是第一年实际接触编程，代码很多也是人工智能帮助我写就的，上传上来之前我也非常紧张，担心有质疑和我都看不懂的修改提交，那我该怎么办啊（笑），最后还是传上来了，人总不能畏手畏脚的，总要前进嘛。在这里谢谢每一个看到的人，感谢大家！
// Important Note
It still has some deficiencies - for example, the category selection for time entries isn't functional yet. Strictly speaking, this is a semi-finished product, but it's already usable with core functionalities intact. I personally use it regularly for time tracking and decided to share it publicly to gather suggestions and critiques.
﻿
As someone in my first year of practical programming experience, much of the code was written with the help of AI. I uploaded it with nervousness - worried about potential question and modification requests I might not understand (laughs) - but ultimately decided to proceed anyway. We can't stay timid forever – progress requires moving forward.
﻿
Thank you to everyone reading this. Your time and attention are deeply appreciated!

> 📌 **时间是最宝贵的资源，让我们一起学会更好地管理它！**

## 📋 目录

- [功能特点](#功能特点)
- [安装说明](#安装说明)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [项目结构](#项目结构)
- [许可证](#许可证)

## ✨ 功能特点

### 1. 计时器
   - ⏱️ 支持正计时和倒计时模式
   - 🎯 自定义计时目标
   - ⏯️ 开始/暂停/重置功能
   - 📊 计时历史记录和统计

### 2. 时间记录
   - 📝 记录每日时间使用情况
   - 🏷️ 按类别分类
   - ✏️ 支持添加、编辑和删除记录
   - 🔍 按日期和类别筛选记录
   - 📈 时间使用分析和可视化
 
### 3. 日记
   - 📔 记录每日活动和想法
   - 📝 支持富文本编辑
   - 📅 按日期查看
   - 🏷️ 支持标签管理
   - 😊 支持心情和天气记录
   - 📤 支持导出为HTML或文本格式

### 4. 任务管理
   - ✅ 创建和管理任务
   - ⭐ 设置优先级和截止日期
   - 📊 任务状态追踪
   - 🏷️ 支持标签管理
   - 🔔 任务提醒功能
   - 📊 任务完成统计功能

### 5. 数据导出
   - 📊 导出时间记录
   - 📈 导出统计图表
   - 📔 导出日记内容
   - 📋 导出任务列表
   - 🔄 支持多种导出格式


## 🔧 安装说明

### 前提条件

- Python 3.8或更高版本
- pip包管理器

### 安装步骤

1. 克隆仓库到本地：
```bash
git clone https://github.com/song-QAQ/TimePulse.git
cd python-time
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 🚀 快速开始

运行应用程序：

```bash
python main.py
```

## 📖 使用指南

### 计时器
1. 在主界面选择"计时器"选项卡
2. 选择正计时或倒计时模式
3. 设置目标时间（如需要）
4. 点击"开始"按钮开始计时

### 时间记录
1. 在主界面选择"时间记录"选项卡
2. 点击"添加记录"按钮创建新记录
3. 填写活动名称、类别、开始和结束时间
4. 点击"保存"按钮保存记录

### 日记
1. 在主界面选择"日记"选项卡
2. 选择日期或点击"新建"按钮
3. 使用富文本编辑器记录您的想法和活动
4. 添加标签、心情和天气信息
5. 点击"保存"按钮保存日记

### 任务管理
1. 在主界面选择"任务"选项卡
2. 点击"添加任务"按钮创建新任务
3. 设置任务名称、优先级、截止日期和标签
4. 点击"保存"按钮保存任务

## 🗂️ 项目结构

- `main.py`: 应用程序入口
- `main_window.py`: 主窗口界面
- `database.py`: 数据库操作
- `timer.py`: 计时器核心功能
- `timer_widget.py`: 计时器界面组件
- `timer_history_widget.py`: 计时历史记录
- `time_records.py`: 时间记录功能
- `time_tracker_widget.py`: 时间追踪界面
- `journal_widget.py`: 日记功能
- `task_widget.py`: 任务管理功能
- `export_widget.py`: 数据导出功能
- `utils.py`: 工具函数

## 📄 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件

---

**感谢您的关注和支持！**
=======