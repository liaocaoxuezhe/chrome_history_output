---
name: browser-history
description: >
  Extract browser history from Chrome, Edge, Safari, Arc, Firefox, Brave, Vivaldi, Opera, Dia, Atlas, Comet, Tabbit, Zen, SigmaOS and generate AI-powered daily reports in Markdown format. This skill should be used when the user asks to export browsing history, generate a daily report, analyze browsing activity, or mentions phrases like "what did I browse today/yesterday/recently". Supports specifying dates or relative days (e.g., "last 3 days", "yesterday", "2025-03-15").
  Author: liaocaoxuezhe.
---

# Browser History Daily Report Skill

Extract browsing history from multiple browsers and generate structured AI analysis reports.

## When to Use

Use this skill when the user wants to:
- Export or extract browser history
- Generate a daily/weekly browsing report
- Analyze browsing activity for a specific date range
- Summarize what they browsed today, yesterday, or any past day

## Workflow

### Step 1: Determine Date Range

Parse the user's intent into a list of target dates:

| User Expression | Parsed Result |
|----------------|---------------|
| "yesterday" | relative_day = -1 |
| "today" | relative_day = 0 |
| "last 3 days" / "past 3 days" | relative_day = -1, -2, -3 |
| "the day before yesterday" | relative_day = -2 |
| "2025-03-15" | specific date |
| unspecified | default to yesterday (relative_day = -1) |

**Note**: Data for today (relative_day = 0) may be incomplete; warn the user.

### Step 2: Locate the Skill Directory

Find the skill installation directory in this priority order:
1. `~/.browser-history-daily-report/`
2. User workspace directory containing `browser-history-daily-report/`
3. Any path mentioned by the user in the current conversation
4. If not found, ask the user

### Step 3: Ensure Configuration Exists

Before running, verify `config.json` exists in the skill directory:

```bash
# Check if config.json exists
ls "$SKILL_DIR/config.json" 2>/dev/null || python3 "$SKILL_DIR/scripts/detect_browser_paths.py" --init
```

If `config.json` is missing, run the browser path detection script to auto-generate it.

### Step 4: Run Extraction Script

For each target date, execute the wrapper script:

```bash
python3 "$SKILL_DIR/scripts/run_history.py" \
  --history-dir "$SKILL_DIR" \
  --relative-day <N>
```

Key parameters:
- `--history-dir`: Absolute path to the skill root directory (contains `scripts/browser_history.py`)
- `--relative-day`: Day offset from today (0=today, -1=yesterday, -2=day before yesterday)
- `--date`: Alternatively specify a date string `YYYY-MM-DD`

### Step 5: Check Output Files

After successful execution, check `history_records/` for:
- `browser_history_YYYY-MM-DD.csv`: Raw browsing records
- `summary_YYYY-MM-DD.md`: AI-generated analysis report

If the summary file does not exist (API key not configured), read the CSV and generate a brief summary directly.

### Step 6: Present Results

For each successfully generated date:
1. Display `summary_YYYY-MM-DD.md` via `computer://` link
2. Briefly describe the date range and record count in Chinese
3. If multiple days, list all links in chronological order

Example response format:
```
已为你生成 3 天的浏览记录日报：

- [2026-02-25 日报](computer:///path/to/summary_2026-02-25.md)（共 142 条记录）
- [2026-02-26 日报](computer:///path/to/summary_2026-02-26.md)（共 89 条记录）
- [2026-02-27 日报](computer:///path/to/summary_2026-02-27.md)（共 56 条记录，今天数据可能不完整）
```

## Error Handling

- **Browser database not found**: Normal; the script skips that browser and continues with others.
- **API key not configured**: The script skips AI analysis and generates only CSV; Claude can read the CSV and produce a simplified report.
- **No records found**: The user may have no browsing activity that day, or the date is out of range; inform the user.
- **Permission error**: Browser databases may be locked; the script automatically creates temporary copies to avoid locking.

## Environment Checks

Before running, verify:

```bash
# Check Python
which python3

# Check dependencies
python3 -c "from openai import OpenAI; print('OK')" 2>/dev/null || pip3 install openai

# Check configuration file exists
ls "$SKILL_DIR/config.json" 2>/dev/null || python3 "$SKILL_DIR/scripts/detect_browser_paths.py" --init
```
