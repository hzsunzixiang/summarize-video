# Summarize Skill 配置说明

## 1. 概述

`summarize` 是一个 CLI 工具，用于对 URL、本地文件（PDF、音频、图片）和 YouTube 链接进行摘要。
在本项目中，它主要用于 **音频语音转录**（whisper-cpp）+ **大模型摘要**（LLM）。

- 官网：https://summarize.sh
- Skill 定义文件：`~/.codebuddy/skills/summarize/SKILL.md`

---

## 2. 安装

```bash
brew install steipete/tap/summarize
```

---

## 3. 大模型配置文件

### 配置文件路径

```
~/.summarize/config.json
```

### 当前配置内容

```json
{
  "model": "openai/DeepSeek-V3-0324",
  "models": {
    "ds":     { "id": "openai/DeepSeek-V3-0324" },
    "ds31":   { "id": "openai/DeepSeek-V3.1" },
    "qwen":   { "id": "openai/Qwen3-235B-A22B" },
    "qwen32": { "id": "openai/Qwen3-32B-FP8" },
    "kimi":   { "id": "openai/Kimi-K2" }
  },
  "env": {
    "OPENAI_API_KEY": "sk-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "OPENAI_BASE_URL": "http://api.haihub.cn/v1"
  },
  "openai": {
    "useChatCompletions": true
  }
}
```

### 配置项说明

| 配置项 | 说明 |
|--------|------|
| `model` | 默认使用的大模型，当前为 **DeepSeek-V3-0324** |
| `models` | 模型别名映射，可通过 `--model ds31` 等别名快速切换 |
| `env.OPENAI_API_KEY` | API 密钥，通过 OpenAI 兼容接口调用 |
| `env.OPENAI_BASE_URL` | API 代理地址，指向 haihub.cn 的 OpenAI 兼容端点 |
| `openai.useChatCompletions` | 使用 Chat Completions API 格式 |

### 支持的 API Key 环境变量

| 提供商 | 环境变量 |
|--------|----------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| xAI | `XAI_API_KEY` |
| Google | `GEMINI_API_KEY`（别名：`GOOGLE_GENERATIVE_AI_API_KEY`、`GOOGLE_API_KEY`） |

> 如果不设置 `config.json`，默认模型为 `google/gemini-3-flash-preview`。

---

## 4. Whisper 语音识别模型

### 模型存储路径

```
~/.summarize/cache/whisper-cpp/models/
```

### 当前已下载的模型

| 模型文件 | 大小 | 说明 |
|----------|------|------|
| `ggml-base.bin` | 142 MB | 基础模型（回退用） |
| `ggml-large-v3-turbo.bin` | 1.6 GB | 高质量模型（默认优先使用） |

### 模型下载方式

```bash
# 方式1：运行 summarize 自动下载
summarize some_audio.mp3

# 方式2：手动下载
curl -L -o ~/.summarize/cache/whisper-cpp/models/ggml-large-v3-turbo.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
```

---

## 5. 工作流程

```
┌──────────────────────────────────────────────────────────┐
│                   summarize CLI 内部流程                    │
│                                                          │
│  音频文件 (.mp3)                                          │
│      │                                                   │
│      ▼                                                   │
│  whisper-cpp（本地离线）                                    │
│  模型：~/.summarize/cache/whisper-cpp/models/             │
│      │                                                   │
│      ▼                                                   │
│  原始转录文本                                              │
│      │                                                   │
│      ▼                                                   │
│  大模型 LLM（通过 API 调用）                                │
│  配置：~/.summarize/config.json                           │
│      │                                                   │
│      ▼                                                   │
│  摘要文本输出                                              │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 6. 常用命令

### 基本用法

```bash
# 摘要音频文件（使用默认模型 DeepSeek-V3）
summarize audio.mp3

# 指定摘要长度
summarize audio.mp3 --length xxl --max-output-tokens 8000

# 仅提取原始内容，不做摘要
summarize audio.mp3 --extract-only
```

### 切换模型

```bash
# 使用别名切换（需在 config.json 中配置 models）
summarize audio.mp3 --model ds31     # DeepSeek-V3.1
summarize audio.mp3 --model qwen     # Qwen3-235B
summarize audio.mp3 --model kimi     # Kimi-K2

# 直接指定完整模型名
summarize audio.mp3 --model google/gemini-3-flash-preview
```

### 指定转录后端

```bash
summarize audio.mp3 --transcriber whisper    # 使用 whisper-cpp
summarize audio.mp3 --transcriber parakeet   # 使用 parakeet
summarize audio.mp3 --transcriber canary     # 使用 canary
```

### 摘要长度选项

| 选项 | 说明 |
|------|------|
| `--length short` (或 `s`) | 简短摘要 |
| `--length medium` (或 `m`) | 中等长度 |
| `--length long` (或 `l`) | 较长摘要 |
| `--length xl` | 超长摘要（默认） |
| `--length xxl` | 最长摘要 |
| `--length 20000` 或 `20k` | 指定字符数上限 |

### 其他常用选项

```bash
# 摘要网页
summarize "https://example.com"

# 摘要 YouTube 视频
summarize "https://youtu.be/dQw4w9WgXcQ" --youtube auto

# 摘要 PDF 文件
summarize "/path/to/file.pdf"

# 输出 JSON 格式（机器可读）
summarize audio.mp3 --json

# 包含时间戳
summarize audio.mp3 --timestamps
```

---

## 7. 在本项目中的使用方式

在 bilibili_fhe 项目中，`summarize` 被用于对分段音频进行转录和摘要：

```bash
# 对每段音频调用 summarize（并行执行）
for f in audio_parts/part_*.mp3; do
  summarize "$f" --length xxl --max-output-tokens 8000 > "${f%.mp3}_transcript.txt" &
done
wait
```

### 注意事项

1. **音频分段是必须的** — summarize CLI 处理超过 10 分钟的音频会超时，必须先用 ffmpeg 分段
2. **模型选择影响质量** — large-v3-turbo 模型（1.6GB）转录质量远优于 base 模型（142MB）
3. **摘要 vs 逐字稿** — summarize 生成的是摘要而非逐字稿；如需逐字稿，应直接使用 whisper-cli 的原始输出
4. **离线转录** — whisper-cpp 语音识别完全在本地运行，不需要网络；只有 LLM 摘要步骤需要 API 调用

---

## 8. 目录结构总览

```
~/.summarize/
├── config.json                              # 大模型配置文件（模型、API Key、代理地址）
└── cache/
    └── whisper-cpp/
        └── models/
            ├── ggml-base.bin                # Whisper 基础模型（142 MB）
            └── ggml-large-v3-turbo.bin      # Whisper 高质量模型（1.6 GB）
```
