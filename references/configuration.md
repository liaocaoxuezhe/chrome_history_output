# Configuration Reference

## config.json Structure

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

## Fields

### browsers
Object mapping browser names to arrays of history database paths. Paths listed here take priority over auto-detection.

### custom_paths
Array of additional directories to scan for history databases.

### api.api_key
Your API key. Supports any OpenAI-compatible API service (Gemini, Qwen, DeepSeek, etc.).

### api.base_url
OpenAI-compatible API base URL. Default is Gemini's free endpoint. Change to any provider:
- Gemini: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Qwen: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- DeepSeek: `https://api.deepseek.com`
- Or any self-hosted endpoint

### api.model_name
Model name for the configured API endpoint. Default is `gemini-2.0-flash`. Examples:
- Gemini: `gemini-2.5-flash`, `gemini-2.5-pro`
- Qwen: `qwen-max-latest`, `qwen-plus-latest`
- DeepSeek: `deepseek-chat`

### output.relative_day
Default day offset (0=today, -1=yesterday).

### output.timezone_offset
Timezone offset in hours from UTC. Default is 8 (UTC+8 / Beijing time).

### output.max_records
Maximum number of history records to send to AI analysis. Records beyond this limit are truncated.

## Environment Variables

All API keys and output settings can be overridden via environment variables:

- `API_KEY`
- `BASE_URL`
- `MODEL_NAME`
- `ANALYSIS_PROMPT`
- `RELATIVE_DAY`
- `TIMEZONE_OFFSET`
- `MAX_RECORDS`
