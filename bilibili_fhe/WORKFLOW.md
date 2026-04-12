# B站视频 → PDF 逐字稿 流水线

一键将B站视频转换为精美的 PDF 文档，包含**完整逐字稿**（语音转文字）并穿插关键幻灯片截图。

## 快速开始

### 方式一：Makefile（推荐）

```bash
# 完整流水线：URL → PDF
make URL="https://www.bilibili.com/video/BVxxxxxxxx/" all

# 自定义标题和语言
make URL="https://www.bilibili.com/video/BVxxxxxxxx/" TITLE="我的演讲" WHISPER_LANG=zh all

# 单独运行某些步骤
make URL="..." transcript     # 仅下载 + 转录
make URL="..." slides         # 仅下载 + 提取帧
make pdf                      # 仅重新编译 PDF（修改 .tex 后）

# 查看所有目标和选项
make help
```

### 方式二：Shell 脚本

```bash
# 一键：URL → PDF
./bilibili_video_to_pdf.sh "https://www.bilibili.com/video/BVxxxxxxxx/"

# 指定输出目录
./bilibili_video_to_pdf.sh "https://www.bilibili.com/video/BVxxxxxxxx/" ./my_output
```

## 前置依赖

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| `yt-dlp` | `brew install yt-dlp` | 从B站下载视频 |
| `ffmpeg` / `ffprobe` | `brew install ffmpeg` | 提取音频、分段、提取帧 |
| `whisper-cli` | `brew install whisper-cpp` | 语音转文字（本地离线运行） |
| `python3` + `Pillow` | `brew install python3` + `pip install Pillow` | 帧去重 |
| `xelatex` | `brew install --cask mactex` | 编译 LaTeX → PDF（支持中文） |

### Whisper 模型

脚本默认使用 `ggml-large-v3-turbo`（1.6 GB）以获得最佳转录质量。
如果未找到，会回退到 `ggml-base`（148 MB）。

模型存储路径：`~/.summarize/cache/whisper-cpp/models/`。
下载大模型的方式：
- 运行一次 `summarize some_audio.mp3`（自动下载），或
- 从 [HuggingFace](https://huggingface.co/ggerganov/whisper.cpp/tree/main) 手动下载

## 流水线概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    bilibili_video_to_pdf.sh                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  第1步：下载视频                                                  │
│  yt-dlp → BVxxxxxxxx.mp4 (720p)                                │
│                                                                 │
│  第2步：提取音频                                                  │
│  ffmpeg → audio.mp3                                             │
│                                                                 │
│  第3步：音频分段                                                  │
│  ffmpeg -f segment → audio_parts/part_00~06.mp3（每段10分钟）     │
│                                                                 │
│  第4步：语音转录（并行）                                           │
│  whisper-cli (large-v3-turbo) → whisper_partXX.txt              │
│  合并 → full_whisper_transcript.txt                              │
│                                                                 │
│  第5步：提取并去重关键帧                                           │
│  ffmpeg（每30秒1帧）→ slides/frame_XXXX.jpg                      │
│  dedup_slides.py (dhash) → key_slides/slide_XXXX.jpg            │
│                                                                 │
│  第6步：生成 LaTeX                                                │
│  gen_full_transcript_tex.py → pdf/fhe_full_transcript.tex       │
│                                                                 │
│  第7步：编译 PDF                                                  │
│  xelatex (×2) → pdf/fhe_full_transcript.pdf                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 输出目录结构

```
<output_dir>/
├── BVxxxxxxxx.mp4              # 下载的视频（720p）
├── audio.mp3                   # 提取的音频
├── audio_parts/                # 分段音频（每段10分钟）
│   ├── part_00.mp3
│   ├── part_01.mp3
│   └── ...
├── whisper_part00.txt          # 各段 whisper 转录结果
├── whisper_part01.txt
├── ...
├── full_whisper_transcript.txt # 合并后的完整逐字稿
├── slides/                     # 原始提取帧
│   ├── frame_0001.jpg
│   └── ...
├── key_slides/                 # 去重后的关键幻灯片
│   ├── slide_0001.jpg
│   └── ...
└── pdf/
    ├── Makefile                # PDF 编译系统
    ├── fhe_full_transcript.tex # LaTeX 源文件
    ├── fhe_full_transcript.pdf # ✅ 最终 PDF 输出
    └── images/                 # LaTeX 引用的幻灯片图片
        ├── slide_0001.jpg
        └── ...
```

## 各脚本说明

### `dedup_slides.py` — 帧去重

使用差分哈希（dhash）去除近似重复帧。仅依赖 `Pillow`（无需 `imagehash`）。

```bash
python3 dedup_slides.py --input slides/ --output key_slides/ --threshold 20
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--input` | （必填） | 包含 `frame_XXXX.jpg` 的目录 |
| `--output` | （必填） | 输出 `slide_XXXX.jpg` 的目录 |
| `--threshold` | 20 | 汉明距离阈值，越大保留的幻灯片越少 |

**算法**：对每帧计算 16×16 差分哈希（256 位），与上一张保留帧的哈希比较。
仅当汉明距离超过阈值时才保留该帧。

### `gen_full_transcript_tex.py` — LaTeX 生成器

从 whisper 逐字稿生成 LaTeX 文档，并穿插幻灯片图片。

```bash
python3 gen_full_transcript_tex.py \
    --base . \
    --title "我的视频标题" \
    --url "https://www.bilibili.com/video/BVxxxxxxxx/"
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--base` | （必填） | 项目目录，需包含 `key_slides/` 和 `full_whisper_transcript.txt` |
| `--title` | "Video Transcript" | PDF 封面标题 |
| `--url` | "" | 原始视频 URL（显示在封面） |
| `--duration` | 自动检测 | 视频时长（秒） |

### `pdf/Makefile` — PDF 编译

```bash
make -C pdf all        # 编译摘要版和完整逐字稿版 PDF
make -C pdf full       # 仅编译完整逐字稿版
make -C pdf summary    # 仅编译摘要版
make -C pdf clean      # 清理辅助文件
make -C pdf distclean  # 清理辅助文件 + PDF
```

### `Makefile`（顶层）— 完整流水线编排

顶层 Makefile 利用 Make 的依赖图编排全部 7 个步骤。
每步都是带有文件依赖的 target，Make 会自动跳过已完成的步骤，只重建需要更新的部分。

```bash
make URL="..." all           # 完整流水线
make URL="..." transcript    # 第1-4步：下载 + 转录
make URL="..." slides        # 第1、5步：下载 + 提取帧 + 去重
make pdf                     # 仅第7步：重新编译 PDF
make clean                   # 清理 LaTeX 辅助文件
make distclean               # 清理所有生成文件
make help                    # 显示所有目标和选项
make URL="..." info          # 显示当前配置
```

**依赖关系图：**

```
all → pdf → tex ──────────→ transcript → transcribe → segment → audio → download
              └→ copy-images → dedup → extract-frames ─────────────────→ download
```

## 配置参数

核心参数（Makefile 变量 / Shell 脚本变量）：

| Makefile 变量 | Shell 变量 | 默认值 | 说明 |
|---------------|-----------|--------|------|
| `SEGMENT_SEC` | `SEGMENT_DURATION` | 600 | 音频分段时长（秒），默认10分钟 |
| `FRAME_INTERVAL` | `FRAME_INTERVAL` | 30 | 每隔 N 秒提取一帧 |
| `DEDUP_THRESH` | `DEDUP_THRESHOLD` | 20 | dhash 去重阈值 |
| `WHISPER_LANG` | `WHISPER_LANG` | "en" | Whisper 语言（`"auto"` 自动检测） |
| `TITLE` | — | "Video Transcript" | PDF 封面标题 |
| `VIDEO_FORMAT` | — | 720p | yt-dlp 格式字符串 |

### 语言配置

**英文**视频（默认）：
```bash
WHISPER_LANG="en"
```

**中文**视频：
```bash
WHISPER_LANG="zh"
```

**自动检测**：
```bash
WHISPER_LANG="auto"
```

## 幂等执行

脚本是**幂等**的——每步都会检查输出是否已存在，存在则跳过。这意味着：

- 如果脚本中断，直接重新运行即可恢复
- 如果想重做某一步，先删除该步的输出文件
- 例如：要重新转录，删除 `whisper_part*.txt` 和 `full_whisper_transcript.txt`

## 常见问题

### "No whisper model found"
```bash
# 方式1：用 summarize 自动下载
summarize some_short_audio.mp3

# 方式2：手动下载
curl -L -o ~/.summarize/cache/whisper-cpp/models/ggml-large-v3-turbo.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
```

### 找不到 xelatex
```bash
brew install --cask mactex
# 或安装更小的版本：
brew install --cask basictex
sudo tlmgr install xecjk ctex mdframed titlesec caption
```

### Python Pillow 不可用
```bash
# macOS externally-managed-environment 环境下：
pip3 install --user --break-system-packages Pillow
# 或使用 venv：
python3 -m venv .venv && source .venv/bin/activate && pip install Pillow
```

### 视频下载失败
```bash
# 更新 yt-dlp（B站经常更改接口）
brew upgrade yt-dlp
# 或使用浏览器 cookies
yt-dlp --cookies-from-browser chrome "URL"
```

## 示例：FHE 演讲（BV1rY411V7Ko）

本目录包含了对 Craig Gentry 在 EUROCRYPT 2021 上关于全同态加密（FHE）的邀请报告的处理结果：

- **视频**：[BV1rY411V7Ko](https://www.bilibili.com/video/BV1rY411V7Ko/)
- **时长**：65 分 22 秒
- **语言**：英文
- **逐字稿**：52 KB，683 行原始转录文本
- **关键幻灯片**：99 张去重帧
- **PDF 输出**：55 页，14.1 MB
