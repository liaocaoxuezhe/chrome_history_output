# Browser History Daily Report - 一键安装脚本 (Windows)
# 支持 Claude Code / Codex CLI / Cursor 等 AI 编程助手
# 作者: liaocaoxuezhe

$REPO_URL = "https://github.com/liaocaoxuezhe/chrome_history_output.git"
$INSTALL_DIR = "$env:USERPROFILE\.browser-history-daily-report"
$SKILL_NAME = "browser-history"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Browser History Daily Report 安装器" -ForegroundColor Cyan
Write-Host "  作者: liaocaoxuezhe" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检测 Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $pythonCmd) {
    Write-Host "❌ 错误: 未找到 Python，请先安装 Python 3.9+" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 检测到 Python" -ForegroundColor Green

# 检测 Git
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "❌ 错误: 未找到 git，请先安装 Git" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 检测到 git" -ForegroundColor Green
Write-Host ""

# 克隆或更新
if (Test-Path $INSTALL_DIR) {
    Write-Host "🔄 检测到已存在的安装，正在更新..." -ForegroundColor Yellow
    Set-Location $INSTALL_DIR
    git pull origin main
} else {
    Write-Host "📥 正在从 GitHub 克隆项目..." -ForegroundColor Cyan
    git clone $REPO_URL $INSTALL_DIR
    Set-Location $INSTALL_DIR
}

Write-Host ""

# 安装依赖
Write-Host "📦 正在安装依赖..." -ForegroundColor Cyan
& $pythonCmd.Source -m pip install openai --quiet

Write-Host "✅ 依赖安装完成" -ForegroundColor Green
Write-Host ""

# 检测浏览器路径
Write-Host "🔍 正在检测浏览器路径..." -ForegroundColor Cyan
& $pythonCmd.Source scripts/detect_browser_paths.py --init

Write-Host ""

# 配置 AI API Key
Write-Host "🔐 配置 AI API（支持任意 OpenAI 兼容接口）" -ForegroundColor Cyan
Write-Host ""
Write-Host "  预设选项:"
Write-Host "  1) Gemini (Google) - 免费，推荐"
Write-Host "  2) Qwen (通义千问)"
Write-Host "  3) DeepSeek"
Write-Host "  4) 自定义"
Write-Host "  5) 稍后配置"
Write-Host ""

$choice = Read-Host "请输入选项 (1-5)"

$apiKeyConfigured = $false
switch ($choice) {
    "1" {
        $apiKey = Read-Host "请输入 Gemini API Key (https://aistudio.google.com/app/apikey)" -AsSecureString
        $plainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey))
        $config = Get-Content config.json -Raw | ConvertFrom-Json
        $config.api.api_key = $plainKey
        $config.api.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
        $config.api.model_name = "gemini-2.0-flash"
        $config | ConvertTo-Json -Depth 10 | Set-Content config.json -Encoding UTF8
        Write-Host "✅ Gemini API 配置已保存" -ForegroundColor Green
    }
    "2" {
        $apiKey = Read-Host "请输入 Qwen API Key" -AsSecureString
        $plainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey))
        $config = Get-Content config.json -Raw | ConvertFrom-Json
        $config.api.api_key = $plainKey
        $config.api.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        $config.api.model_name = "qwen-max-latest"
        $config | ConvertTo-Json -Depth 10 | Set-Content config.json -Encoding UTF8
        Write-Host "✅ Qwen API 配置已保存" -ForegroundColor Green
    }
    "3" {
        $apiKey = Read-Host "请输入 DeepSeek API Key" -AsSecureString
        $plainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey))
        $config = Get-Content config.json -Raw | ConvertFrom-Json
        $config.api.api_key = $plainKey
        $config.api.base_url = "https://api.deepseek.com"
        $config.api.model_name = "deepseek-chat"
        $config | ConvertTo-Json -Depth 10 | Set-Content config.json -Encoding UTF8
        Write-Host "✅ DeepSeek API 配置已保存" -ForegroundColor Green
    }
    "4" {
        $baseUrl = Read-Host "请输入 API Base URL"
        $modelName = Read-Host "请输入 Model 名称"
        $apiKey = Read-Host "请输入 API Key" -AsSecureString
        $plainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey))
        $config = Get-Content config.json -Raw | ConvertFrom-Json
        $config.api.api_key = $plainKey
        $config.api.base_url = $baseUrl
        $config.api.model_name = $modelName
        $config | ConvertTo-Json -Depth 10 | Set-Content config.json -Encoding UTF8
        Write-Host "✅ 自定义 API 配置已保存" -ForegroundColor Green
    }
    default {
        Write-Host "⏭️ 跳过 API 配置，之后可通过编辑 config.json 或设置环境变量" -ForegroundColor Yellow
    }
}

Write-Host ""

# 安装 Claude Code Skill
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if ($claudeCmd) {
    Write-Host "🤖 检测到 Claude Code，正在安装 skill..." -ForegroundColor Cyan
    $skillDir = "$env:USERPROFILE\.claude\skills\$SKILL_NAME"
    New-Item -ItemType Directory -Force -Path "$skillDir\scripts" | Out-Null
    Copy-Item SKILL.md $skillDir\ -Force
    Copy-Item scripts\*.py "$skillDir\scripts\" -Force
    Write-Host "✅ Claude Code skill 已安装到: $skillDir" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✅ 安装完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "安装路径: $INSTALL_DIR" -ForegroundColor Cyan
Write-Host ""
Write-Host "快速使用:" -ForegroundColor Cyan
Write-Host "  cd $INSTALL_DIR"
Write-Host "  python scripts\browser_history.py           # 分析昨天"
Write-Host "  python scripts\browser_history.py --today   # 分析今天"
Write-Host ""
Write-Host "在 AI 编程助手中使用:" -ForegroundColor Cyan
Write-Host "  Claude Code: '帮我分析昨天的浏览记录'"
Write-Host "  Codex CLI:   '分析我近7天的浏览记录'"
Write-Host "  Cursor:      '导出昨天的浏览记录并生成日报'"
Write-Host ""
Write-Host "配置文件: $INSTALL_DIR\config.json" -ForegroundColor Cyan
Write-Host "日报输出: $INSTALL_DIR\history_records\" -ForegroundColor Cyan
Write-Host ""
