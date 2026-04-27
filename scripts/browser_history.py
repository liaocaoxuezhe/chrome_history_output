#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser History Exporter & AI Daily Report Generator

从 Chrome、Edge、Safari、Arc 等浏览器提取历史记录，
并使用 AI 生成分析日报（Markdown 格式）。

用法:
    python browser_history.py              # 分析昨天的记录
    python browser_history.py --today      # 分析今天的记录
    python browser_history.py --date 2025-03-15  # 分析指定日期

首次使用:
    1. 复制 config.example.json 为 config.json
    2. 填写你的 api_key（支持任意 OpenAI 兼容 API）
    3. 运行 python detect_browser_paths.py --init 自动检测浏览器路径
"""

import os
import sqlite3
import csv
import json
import argparse
from datetime import datetime, timedelta
import platform
import glob
from typing import List

# 加载配置文件（脚本在 scripts/ 目录，配置在项目根目录）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(_PROJECT_ROOT, 'config.json')
CONFIG_EXAMPLE_PATH = os.path.join(_PROJECT_ROOT, 'config.example.json')


def load_config():
    """加载配置文件，如果不存在则尝试自动生成或提示用户"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 尝试自动检测并生成配置
    try:
        from detect_browser_paths import generate_config
        print("未找到 config.json，正在自动检测浏览器路径并生成配置...")
        return generate_config(CONFIG_PATH)
    except Exception as e:
        print(f"无法自动生成配置: {e}")
        print("请手动复制 config.example.json 为 config.json 并填写配置")
        return {}


config = load_config()

# API 配置（优先环境变量，其次配置文件）
API_KEY = os.getenv('API_KEY', config.get('api', {}).get('api_key', ''))
BASE_URL = os.getenv('BASE_URL', config.get('api', {}).get('base_url', ''))
MODEL_NAME = os.getenv('MODEL_NAME', config.get('api', {}).get('model_name', ''))

# 输出配置
RELATIVE_DAY = int(os.getenv('RELATIVE_DAY', config.get('output', {}).get('relative_day', -1)))
TIMEZONE_OFFSET = int(os.getenv('TIMEZONE_OFFSET', config.get('output', {}).get('timezone_offset', 8)))
MAX_RECORDS = int(os.getenv('MAX_RECORDS', config.get('output', {}).get('max_records', 800)))

# 加载 Prompt
DEFAULT_PROMPT = '''# 任务
分析我今天的浏览记录，生成一份结构化但内容丰富的日报分析报告。

## 输出格式要求

```
# 📊 {日期} 浏览记录日报

---

## 🕐 一、时间线概览

按时间段展示主要活动，每个时间段内按实际任务流转细分阶段：

### 🌅 上午 (06:00-12:00)
#### 阶段一：[具体时间如 09:30-10:30] - [任务名称]
- **做了什么**: [详细描述此阶段的具体行为和目标，不要笼统]
- **访问的网站**: [列举具体访问的网页标题和用途，2-4个]
- **获得/产出**: [具体说明此阶段了解了什么信息、完成了什么]

#### 阶段二：[具体时间如 10:30-12:00] - [任务名称]
- **做了什么**: [详细描述此阶段的具体行为和目标]
- **访问的网站**: [列举具体访问的网页标题和用途]
- **获得/产出**: [具体说明此阶段了解了什么信息、完成了什么]

### 🌞 下午 (12:00-18:00)
#### 阶段一：[具体时间] - [任务名称]
- **做了什么**: [详细描述]
- **访问的网站**: [具体列举]
- **获得/产出**: [具体内容]

[如有更多阶段继续列出...]

### 🌙 晚上 (18:00-02:00)
#### 阶段一：[具体时间] - [任务名称]
- **做了什么**: [详细描述]
- **访问的网站**: [具体列举]
- **获得/产出**: [具体内容]

#### 阶段二：[具体时间如 23:00-01:30] - [深夜任务]
- **做了什么**: [如果凌晨有浏览记录，必须单独列出]
- **访问的网站**: [具体列举]
- **获得/产出**: [具体内容]

---

## 📋 二、任务分类统计

| 任务类别 | 时间估算 | 占比 | 主要网站/工具 |
|---------|---------|-----|-------------|
| [具体任务名] | X小时X分钟 | XX% | [相关网站] |
| [具体任务名] | X小时X分钟 | XX% | [相关网站] |
| **总计** | **X小时X分钟** | **100%** | - |

> 💡 **时间估算说明**: 基于访问频率和停留时间估算，仅供参考

---

## 🔍 三、深度洞察

这部分不要套模板，基于实际浏览内容给出真实、个性化的洞察：

### 1. 浏览模式分析
- **主题流转路径**: 分析用户是如何从一个话题自然过渡到另一个话题的，找出浏览的内在逻辑
- **信息获取特点**: 是深度阅读型还是广度探索型？偏向官方文档还是社区讨论？
- **工作节奏**: 分析专注时段和休息切换的规律

### 2. 今日核心关注点
基于实际访问内容，提炼出2-3个今天真正关心的核心问题或主题，并说明：
- 为什么这些主题吸引了用户
- 用户在每个主题上深入到什么程度
- 这些主题之间有什么关联

### 3. 有趣发现与反思
- **意外发现**: 今天有没有偶然发现的有趣内容？
- **知识盲区**: 从浏览路径看，用户在哪些地方表现出犹豫或反复搜索？
- **行为模式**: 有什么独特的浏览习惯或偏好？

### 4. 效率与状态评估
- **生产力评分**: ⭐⭐⭐⭐☆ (X/5)
- **状态描述**: 用一句话描述今天整体的工作/学习状态
- **高光时刻**: 哪个时间段效率最高？为什么？

---

## 📝 四、总结与建议

### ✅ 今日亮点
[基于实际行为，给出2-3点具体的正面评价，要具体不要笼统]

### 💡 观察与建议
[基于浏览模式，给出1-2个建设性的观察，可以是发现的高效习惯或潜在优化点]

### 🎯 明日展望
[一句鼓励的话，可以结合今天的主题延续性]
```

## 分析要求

### 时间线部分（重点）
1. **时间段划分**: 上午(06:00-12:00)、下午(12:00-18:00)、晚上(18:00-02:00)，必须覆盖到凌晨2点
2. **阶段细分**: 每个大时段内根据实际任务变化细分为多个阶段，不要一个时段一句话带过
3. **具体时间**: 每个阶段标注大致的起止时间
4. **内容详细**: 每个阶段必须包含"做了什么、访问了哪些网站、获得了什么"三个要素
5. **真实具体**: 引用实际的网页标题，描述实际的行为，不要概括性描述

### 深度洞察部分（重点）
1. **拒绝模板化**: 不要套用固定的"高频主题、信息路径、工作比例"格式
2. **真实洞察**: 基于实际浏览数据，发现用户真实的兴趣点和行为模式
3. **主题流转**: 重点分析用户是如何在不同主题间切换的，找出内在逻辑
4. **个性化**: 每个用户的报告应该看起来不一样，反映其独特的行为特征

### 其他要求
1. **时间估算**: 基于访问频率和停留时间进行合理估算，格式统一为"X小时X分钟"
2. **表格排序**: 任务统计表格必须按时间从多到少降序排列
3. **使用Emoji**: 适当使用 emoji 让报告更生动
4. **积极正面**: 评价部分要鼓励为主

## 数据格式
我会提供当天的浏览记录，格式为：
- 访问时间: 网页标题 (URL)

请基于这些数据生成详细、有洞察力的报告。'''

ANALYSIS_PROMPT = os.getenv('ANALYSIS_PROMPT', config.get('prompt', DEFAULT_PROMPT))


# 从配置文件或环境变量加载浏览器路径
def get_browser_paths(browser_name):
    """从配置文件获取浏览器路径，如果不存在则尝试自动发现"""
    browsers = config.get('browsers', {})
    if browser_name in browsers:
        paths = browsers[browser_name]
        return [p for p in paths if os.path.exists(p)]

    # 尝试自动发现
    try:
        from detect_browser_paths import find_browser_paths
        detected = find_browser_paths(browser_name)
        return detected.get(browser_name, [])
    except ImportError:
        return []


def get_chrome_profile_paths():
    return get_browser_paths('Chrome')


def get_arc_history_path():
    paths = get_browser_paths('Arc')
    return paths[0] if paths else None


def get_safari_history_path():
    paths = get_browser_paths('Safari')
    return paths[0] if paths else None


def get_edge_profile_paths():
    return get_browser_paths('Edge')


def get_dia_profile_paths():
    return get_browser_paths('Dia')


def get_atlas_profile_paths():
    return get_browser_paths('Atlas')


def get_comet_profile_paths():
    return get_browser_paths('Comet')


def get_tabbit_profile_paths():
    return get_browser_paths('Tabbit')


def get_tabbit_browser_profile_paths():
    return get_browser_paths('Tabbit Browser')


def get_firefox_profile_paths():
    return get_browser_paths('Firefox')


def get_brave_profile_paths():
    return get_browser_paths('Brave')


def get_vivaldi_profile_paths():
    return get_browser_paths('Vivaldi')


def get_opera_profile_paths():
    return get_browser_paths('Opera')


def get_zen_profile_paths():
    return get_browser_paths('Zen')


def get_sigmaos_profile_paths():
    return get_browser_paths('SigmaOS')


def get_history_from_db(history_path, browser_name):
    if not history_path or not os.path.exists(history_path):
        raise Exception(f"{browser_name} history file not found: {history_path}")

    temp_path = f'/tmp/{browser_name}_history_{os.getpid()}'
    # 使用 cp -c 参数跳过克隆错误（MacOS 系统专用参数）
    os.system(f'cp -c "{history_path}" "{temp_path}" 2>/dev/null')

    # 添加数据库连接超时参数
    conn = sqlite3.connect(temp_path, timeout=15)
    cursor = conn.cursor()

    # 根据相对日期计算目标日期
    target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=RELATIVE_DAY)
    next_date = target_date + timedelta(days=1)

    # WebKit 时间戳转换 (microseconds since 1601-01-01)
    target_timestamp = int((target_date - datetime(1601, 1, 1)).total_seconds() * 1000000)
    next_timestamp = int((next_date - datetime(1601, 1, 1)).total_seconds() * 1000000)

    # Firefox 使用不同的数据库结构
    if browser_name == 'Firefox' or history_path.endswith('places.sqlite'):
        # Firefox places.sqlite 使用 Unix 时间戳（微秒）
        cursor.execute("""
            SELECT url, title, visit_date
            FROM moz_places p
            JOIN moz_historyvisits v ON p.id = v.place_id
            WHERE visit_date >= ? AND visit_date < ?
            ORDER BY visit_date DESC
        """, (target_timestamp, next_timestamp))
    else:
        cursor.execute("""
            SELECT url, title, last_visit_time
            FROM urls
            WHERE last_visit_time >= ? AND last_visit_time < ?
            ORDER BY last_visit_time DESC
        """, (target_timestamp, next_timestamp))

    history_data = cursor.fetchall()

    if not history_data:
        date_str = target_date.strftime('%Y-%m-%d')
        print(f"没有找到{browser_name}在{date_str}的历史记录。配置文件: {history_path}")

    conn.close()
    os.remove(temp_path)

    processed_data = []
    for url, title, timestamp in history_data:
        # 将 UTC 时间转换为指定时区
        visit_time = datetime(1601, 1, 1) + timedelta(microseconds=timestamp) + timedelta(hours=TIMEZONE_OFFSET)
        processed_data.append([url, title, visit_time.strftime('%Y-%m-%d %H:%M:%S'), browser_name])

    return processed_data


def export_to_csv(data, filename='browser_history.csv'):
    # 创建历史记录存储目录
    history_dir = os.path.join(_PROJECT_ROOT, 'history_records')
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)

    # 获取目标日期作为文件名
    target_date = (datetime.now() + timedelta(days=RELATIVE_DAY)).strftime('%Y-%m-%d')
    filename = os.path.join(history_dir, f'browser_history_{target_date}.csv')

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Title', 'Visit Time', 'Browser'])
        writer.writerows(data)

    return filename


def save_summary_as_markdown(summary_text, date=None):
    """保存分析摘要到 Markdown 文件"""
    history_dir = os.path.join(_PROJECT_ROOT, 'history_records')
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)

    # 获取日期
    if date is None:
        date = (datetime.now() + timedelta(days=RELATIVE_DAY)).strftime('%Y-%m-%d')

    # 创建 Markdown 内容
    markdown_content = f"# {date} 浏览记录分析\n\n"
    markdown_content += summary_text

    # 保存 Markdown 文件
    markdown_file = os.path.join(history_dir, f'summary_{date}.md')
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return markdown_file


def summarize_history(history_data: List[list]) -> str:
    if not API_KEY:
        print("警告: 未设置 API Key。请在 config.json 中填写 api_key 或设置环境变量 API_KEY")
        return ""

    if not BASE_URL or not MODEL_NAME:
        print("警告: 未设置 base_url 或 model_name。请在 config.json 中配置")
        return ""

    try:
        from openai import OpenAI
    except ImportError:
        print("错误: 未安装 openai 包。请运行: pip install openai")
        return ""

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 获取目标日期的字符串表示
    target_date = (datetime.now() + timedelta(days=RELATIVE_DAY)).strftime('%Y-%m-%d')

    # 压缩历史记录: 相邻相同 URL 合并，减少冗余
    compressed_data = []
    last_url = None
    for item in history_data:
        url, title, visit_time, browser = item
        if url != last_url:
            compressed_data.append(item)
            last_url = url

    # 如果仍然过长，截断到前 MAX_RECORDS 条
    if len(compressed_data) > MAX_RECORDS:
        print(f"警告: 压缩后仍有 {len(compressed_data)} 条记录，截断到前 {MAX_RECORDS} 条进行分析")
        compressed_data = compressed_data[:MAX_RECORDS]

    # 将历史记录格式化为易读的文本
    history_text = f"{target_date}的浏览记录:\n"
    for url, title, visit_time, browser in compressed_data:
        history_text += f"- {visit_time}: {title} ({url})\n"

    # 完整提示内容
    custom_prompt = ANALYSIS_PROMPT.replace("今天", target_date)
    full_prompt = custom_prompt + "\n\n" + history_text

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            n=1,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )

        summary_text = response.choices[0].message.content
        return summary_text
    except Exception as e:
        print(f"生成总结时发生错误: {str(e)}")
        return ""


def extract_and_export(target_relative_day=None):
    """主函数: 提取历史记录并导出"""
    global RELATIVE_DAY
    if target_relative_day is not None:
        RELATIVE_DAY = target_relative_day

    all_history_data = []

    # 浏览器列表和对应的获取函数
    browsers = [
        ('Chrome', get_chrome_profile_paths),
        ('Edge', get_edge_profile_paths),
        ('Safari', get_safari_history_path),
        ('Arc', get_arc_history_path),
        ('Firefox', get_firefox_profile_paths),
        ('Brave', get_brave_profile_paths),
        ('Vivaldi', get_vivaldi_profile_paths),
        ('Opera', get_opera_profile_paths),
        ('Dia', get_dia_profile_paths),
        ('Atlas', get_atlas_profile_paths),
        ('Comet', get_comet_profile_paths),
        ('Tabbit', get_tabbit_profile_paths),
        ('Tabbit Browser', get_tabbit_browser_profile_paths),
        ('Zen', get_zen_profile_paths),
        ('SigmaOS', get_sigmaos_profile_paths),
    ]

    for browser_name, path_func in browsers:
        try:
            paths = path_func()
            if not paths:
                continue
            # 统一处理单路径和多路径
            if isinstance(paths, str):
                paths = [paths]
            for p in paths:
                try:
                    data = get_history_from_db(p, browser_name)
                    all_history_data.extend(data)
                    print(f"{browser_name}: 获取 {len(data)} 条记录 [{p}]")
                except Exception as e:
                    print(f"{browser_name} 配置文件跳过 {p}: {e}")
        except Exception as e:
            print(f"{browser_name} 跳过: {e}")

    # 导出所有历史记录
    if all_history_data:
        all_history_data.sort(key=lambda x: x[2], reverse=True)
        saved_file = export_to_csv(all_history_data)
        print(f"成功导出总计 {len(all_history_data)} 条历史记录到 {saved_file}")

        # 使用 AI 生成总结
        summary = summarize_history(all_history_data)
        if summary:
            markdown_file = save_summary_as_markdown(summary)
            print(f"成功保存分析摘要到 Markdown 文件: {markdown_file}")
            print("\n=== 今日浏览记录总结 ===")
            print(summary)
            return saved_file, markdown_file
        else:
            print("AI 总结生成失败或未配置 API Key")
            return saved_file, None
    else:
        target_date = (datetime.now() + timedelta(days=RELATIVE_DAY)).strftime('%Y-%m-%d')
        print(f"未找到 {target_date} 的任何历史记录")
        return None, None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='浏览器历史记录导出与 AI 日报生成')
    parser.add_argument('--today', action='store_true', help='分析今天的记录')
    parser.add_argument('--date', type=str, help='指定日期，格式: YYYY-MM-DD')
    parser.add_argument('--relative-day', type=int, help='相对天数偏移 (0=今天, -1=昨天)')
    args = parser.parse_args()

    if args.today:
        RELATIVE_DAY = 0
    elif args.date:
        target = datetime.strptime(args.date, '%Y-%m-%d')
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        RELATIVE_DAY = (target - today).days
    elif args.relative_day is not None:
        RELATIVE_DAY = args.relative_day

    extract_and_export()
