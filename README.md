# Browser History Daily Report

一个支持多浏览器的历史记录导出与 AI 日报生成工具。支持从 Chrome、Edge、Safari、Arc、Firefox、Brave、Vivaldi、Opera、Dia、Atlas、Comet、Tabbit、Zen、SigmaOS 等浏览器提取历史记录，并调用任意 OpenAI 兼容 API（Gemini、Qwen、DeepSeek 等）生成结构化的 Markdown 分析报告。

## 特性

- **多浏览器支持**: 自动检测 macOS / Windows / Linux 上常见浏览器的历史记录数据库路径
- **AI 智能分析**: 支持任意 OpenAI 兼容 API（Gemini、Qwen、DeepSeek 等）
- **灵活的日期选择**: 昨天、今天、指定日期或任意相对天数
- **安全的数据读取**: 自动创建临时副本避免锁定正在运行的浏览器数据库
- **UTF-8 完全兼容**: 完美支持中文内容

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/liaocaoxuezhe/chrome_history_output.git
cd chrome_history_output
```

### 2. 安装依赖

```bash
pip install openai
```

### 3. 检测浏览器路径

```bash
python scripts/detect_browser_paths.py --init
```

这会自动检测你的浏览器并生成 `config.json`。

### 4. 配置 API Key

编辑生成的 `config.json`，填写你的 API 配置：

```json
{
  "api": {
    "api_key": "your-api-key",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "model_name": "gemini-2.0-flash"
  }
}
```

默认使用 Gemini 的免费 API，你也可以换成任意 OpenAI 兼容接口：

```json
{
  "api": {
    "api_key": "your-qwen-api-key",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen-max-latest"
  }
}
```

或者使用环境变量：

```bash
export API_KEY="your-api-key"
export BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
export MODEL_NAME="gemini-2.0-flash"
```

### 5. 运行

```bash
# 分析昨天
python scripts/browser_history.py

# 分析今天
python scripts/browser_history.py --today

# 分析指定日期
python scripts/browser_history.py --date 2025-03-15
```

报告将生成在 `history_records/` 目录下：
- `browser_history_YYYY-MM-DD.csv` - 原始浏览记录
- `summary_YYYY-MM-DD.md` - AI 生成的分析日报

## 在 AI 编程助手中使用

### Skills.sh 安装

```bash
npx skills add liaocaoxuezhe/chrome_history_output
```

### Claude Code

```bash
# 或者直接使用
claude 帮我分析昨天的浏览记录
```

### Codex CLI

```bash
codex 分析我近7天的浏览记录
```

### Cursor

在 Cursor 的 Composer 或 Chat 中说：

```
帮我导出昨天的浏览记录并生成日报
```

## 支持的浏览器

| 浏览器 | macOS | Windows | Linux |
|---------|-------|---------|-------|
| Chrome | ✅ | ✅ | ✅ |
| Edge | ✅ | ✅ | ✅ |
| Safari | ✅ | - | - |
| Arc | ✅ | ✅ | - |
| Firefox | ✅ | ✅ | ✅ |
| Brave | ✅ | ✅ | ✅ |
| Vivaldi | ✅ | ✅ | ✅ |
| Opera | ✅ | ✅ | - |
| Dia | ✅ | - | - |
| Atlas | ✅ | - | - |
| Comet | ✅ | - | - |
| Tabbit | ✅ | - | - |
| Zen | ✅ | - | - |
| SigmaOS | ✅ | - | - |

## 配置文件说明

`config.json` 支持以下配置项：

```json
{
  "browsers": {
    "Chrome": ["/path/to/History"]
  },
  "custom_paths": [],
  "api": {
    "api_key": "",
    "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "model_name": "gemini-2.0-flash"
  },
  "output": {
    "relative_day": -1,
    "timezone_offset": 8,
    "max_records": 800
  }
}
```

- `browsers`: 手动指定浏览器路径（优先级高于自动检测）
- `custom_paths`: 自定义扫描路径
- `api.api_key`: API Key（支持任意 OpenAI 兼容接口）
- `api.base_url`: API 地址（默认 Gemini，可换 Qwen/DeepSeek 等）
- `api.model_name`: 模型名称（默认 gemini-2.0-flash）
- `output.timezone_offset`: 时区偏移（默认 UTC+8）
- `output.max_records`: AI 分析时最多处理的记录数

## 自动化日报

你可以设置定时任务每天自动生成日报：

### macOS (LaunchAgent)

```bash
# 复制 plist 文件并加载
cp com.user.browserhistory.smart.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.browserhistory.smart.plist
```

### Linux (Cron)

```bash
# 每天上午9点运行
crontab -e
# 添加：0 9 * * * /usr/bin/python3 /path/to/browser_history.py
```

### Windows (任务计划程序)

```powershell
# 使用 Task Scheduler 创建每日任务
schtasks /create /tn "BrowserHistoryReport" /tr "python C:\path\to\browser_history.py" /sc daily /st 09:00
```

## 安装脚本

项目提供了一键安装脚本：

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/liaocaoxuezhe/chrome_history_output/main/install.sh | bash

# Windows
irm https://raw.githubusercontent.com/liaocaoxuezhe/chrome_history_output/main/install.ps1 | iex
```

## 贡献

欢迎提交 Issue 和 PR！如果你发现了新的浏览器路径模式，请在 `scripts/detect_browser_paths.py` 中添加。

## License

MIT License

## 作者

作者: **liaocaoxuezhe**

如果这个工具帮助到了你，欢迎 Star 和分享！
