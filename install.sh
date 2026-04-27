#!/usr/bin/env bash
# Browser History Daily Report - 一键安装脚本
# 支持 Claude Code / Codex CLI / Cursor 等 AI 编程助手
# 作者: liaocaoxuezhe

set -e

REPO_URL="https://github.com/liaocaoxuezhe/browser-history-daily-report.git"
INSTALL_DIR="${HOME}/.browser-history-daily-report"
SKILL_NAME="browser-history"

echo "=========================================="
echo "  Browser History Daily Report 安装器"
echo "  作者: liaocaoxuezhe"
echo "=========================================="
echo ""

# 检测 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.9+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ 检测到 Python $PYTHON_VERSION"

# 检测 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到 pip3"
    exit 1
fi

echo "✅ 检测到 pip3"

# 检测 Git
if ! command -v git &> /dev/null; then
    echo "❌ 错误: 未找到 git，请先安装 Git"
    exit 1
fi

echo "✅ 检测到 git"
echo ""

# 克隆或更新
if [ -d "$INSTALL_DIR" ]; then
    echo "🔄 检测到已存在的安装，正在更新..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo "📥 正在从 GitHub 克隆项目..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""

# 安装依赖
echo "📦 正在安装依赖..."
pip3 install openai --quiet

echo "✅ 依赖安装完成"
echo ""

# 检测浏览器路径
echo "🔍 正在检测浏览器路径..."
python3 scripts/detect_browser_paths.py --init

echo ""

# 配置 AI API Key
echo "🔐 配置 AI API（支持任意 OpenAI 兼容接口）"
echo ""
echo "  预设选项:"
echo "  1) Gemini (Google) - 免费，推荐"
echo "  2) Qwen (通义千问)"
echo "  3) DeepSeek"
echo "  4) 自定义"
echo "  5) 稍后配置"
echo ""
read -p "请输入选项 (1-5): " choice

case $choice in
    1)
        read -s -p "请输入 Gemini API Key (https://aistudio.google.com/app/apikey): " api_key
        echo ""
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        model_name="gemini-2.0-flash"
        ;;
    2)
        read -s -p "请输入 Qwen API Key: " api_key
        echo ""
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        model_name="qwen-max-latest"
        ;;
    3)
        read -s -p "请输入 DeepSeek API Key: " api_key
        echo ""
        base_url="https://api.deepseek.com"
        model_name="deepseek-chat"
        ;;
    4)
        read -p "请输入 API Base URL: " base_url
        read -p "请输入 Model 名称: " model_name
        read -s -p "请输入 API Key: " api_key
        echo ""
        ;;
    *)
        echo "⏭️ 跳过 API 配置，之后可通过编辑 config.json 或设置环境变量"
        api_key=""
        ;;
esac

if [ -n "$api_key" ]; then
    python3 -c "
import json
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
config['api']['api_key'] = '${api_key}'
config['api']['base_url'] = '${base_url}'
config['api']['model_name'] = '${model_name}'
with open('config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
"
    echo "✅ API 配置已保存"
fi

echo ""

# 安装 Claude Code Skill
if command -v claude &> /dev/null; then
    echo "🤖 检测到 Claude Code，正在安装 skill..."
    SKILL_DIR="${HOME}/.claude/skills/${SKILL_NAME}"
    mkdir -p "$SKILL_DIR/scripts"
    cp SKILL.md "$SKILL_DIR/"
    cp scripts/*.py "$SKILL_DIR/scripts/"
    echo "✅ Claude Code skill 已安装到: $SKILL_DIR"
    echo "   提示: 在 Claude Code 中说 '帮我分析昨天的浏览记录' 即可使用"
fi

# 安装 Codex CLI Skill
if command -v codex &> /dev/null; then
    echo "🤖 检测到 Codex CLI，正在配置..."
    # Codex CLI 使用同一个 skill 目录
    echo "✅ Codex CLI 已配置"
fi

echo ""
echo "=========================================="
echo "  ✅ 安装完成！"
echo "=========================================="
echo ""
echo "安装路径: $INSTALL_DIR"
echo ""
echo "快速使用:"
echo "  cd $INSTALL_DIR"
echo "  python3 scripts/browser_history.py           # 分析昨天"
echo "  python3 scripts/browser_history.py --today   # 分析今天"
echo ""
echo "在 AI 编程助手中使用:"
echo "  Claude Code: '帮我分析昨天的浏览记录'"
echo "  Codex CLI:   '分析我近7天的浏览记录'"
echo "  Cursor:      '导出昨天的浏览记录并生成日报'"
echo ""
echo "配置文件: $INSTALL_DIR/config.json"
echo "日报输出: $INSTALL_DIR/history_records/"
echo ""
