# B站/YouTube 视频 → PDF 完整逐字稿 工具集

一键将B站（或YouTube）视频转换为精美的 PDF 文档，包含**完整逐字稿**（whisper 语音转文字原始输出）并穿插关键幻灯片截图。

---

## 工具清单

```
bilibili_tool/
├── Makefile                 # 顶层流水线编排（Make 依赖图驱动 7 步流程）
├── dedup_slides.py          # 帧去重工具（dhash 算法，仅依赖 Pillow）
├── gen_transcript_tex.py    # LaTeX 逐字稿生成器（转录文本 + 幻灯片对齐）
├── .gitignore               # Git 忽略规则
└── WORKFLOW.md              # 本文档
```

---

## 快速开始

```bash
# 完整流水线：一行命令，URL → PDF
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" all

# 自定义标题和语言
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" \
     TITLE="FHE十年发展" WHISPER_LANG=en all

# 单独运行某些步骤
make URL="..." transcript     # 仅下载 + 转录
make URL="..." slides         # 仅下载 + 提取帧 + 去重
make pdf                      # 仅重新编译 PDF

# 查看帮助
make help
```

---

## 前置依赖

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| `yt-dlp` | `brew install yt-dlp` | 从B站/YouTube下载视频 |
| `ffmpeg` / `ffprobe` | `brew install ffmpeg` | 提取音频、分段、提取帧 |
| `whisper-cli` | `brew install whisper-cpp` | 语音转文字（本地离线） |
| `python3` + `Pillow` | `brew install python3` + `pip install Pillow` | 帧去重 |
| `xelatex` | `brew install --cask mactex` | 编译 LaTeX → PDF |

### Whisper 模型

```bash
# 下载 large-v3-turbo 模型（1.6GB，推荐）
mkdir -p ~/.summarize/cache/whisper-cpp/models
curl -L -o ~/.summarize/cache/whisper-cpp/models/ggml-large-v3-turbo.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
```

---

## 流水线 7 步

```
┌─────────────────────────────────────────────────────────────────┐
│                         Makefile                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  第1步：下载视频         yt-dlp → BVxxxxxxxx.mp4 (720p)         │
│  第2步：提取音频         ffmpeg → audio.mp3                      │
│  第3步：音频分段         ffmpeg -f segment → part_00~06.mp3      │
│  第4步：语音转录（并行）  whisper-cli → whisper_partXX.txt        │
│                          合并 → full_whisper_transcript.txt      │
│  第5步：提取+去重帧      ffmpeg + dedup_slides.py → key_slides/  │
│  第6步：生成 LaTeX       gen_transcript_tex.py → transcript.tex  │
│  第7步：编译 PDF         xelatex ×2 → transcript.pdf             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Make 依赖关系图

```
all → pdf → tex ──────────→ transcript → transcribe → segment → audio → download
              └→ copy-images → dedup → extract-frames ─────────────────→ download
```

---

## 配置参数

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `URL` | （必填） | 视频 URL |
| `TITLE` | "Video Transcript" | PDF 封面标题 |
| `WHISPER_LANG` | `en` | Whisper 语言（`en`/`zh`/`auto`） |
| `SEGMENT_SEC` | 600 | 音频分段时长（秒） |
| `FRAME_INTERVAL` | 30 | 每隔 N 秒提取一帧 |
| `DEDUP_THRESH` | 20 | dhash 去重阈值 |
| `VIDEO_FORMAT` | 720p | yt-dlp 格式字符串 |

---

## 各脚本说明

### `dedup_slides.py`

使用差分哈希（dhash）去除近似重复帧。仅依赖 Pillow。

```bash
python3 dedup_slides.py --input slides/ --output key_slides/ --threshold 20 --frame-interval 30
```

### `gen_transcript_tex.py`

从 whisper 逐字稿 + 关键幻灯片生成 LaTeX 文档。

```bash
python3 gen_transcript_tex.py --base . --title "标题" --url "URL" --output pdf/transcript.tex
```

---

## 实际运行示例：FHE 演讲（BV1rY411V7Ko）

以 Craig Gentry 在 EUROCRYPT 2021 上关于全同态加密的邀请报告为例，
使用本工具集的 Makefile 驱动完整流水线。

### 执行命令

```bash
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" \
     TITLE="A Decade (or So) of Fully Homomorphic Encryption" \
     WHISPER_LANG=en \
     all
```

### 执行过程

```
[1/7] Downloading video BV1rY411V7Ko...
  ✓ Downloaded: BV1rY411V7Ko.mp4 (160MB, 720p, 65分22秒)

[2/7] Extracting audio...
  ✓ Audio: audio.mp3 (34MB)

[3/7] Segmenting audio into 600s chunks...
  ✓ Segments: 7 parts (part_00 ~ part_06, 每段约5MB)

[4/7] Transcribing with whisper (model: ggml-large-v3-turbo)...
  ⏳ 7 段并行转录...
  ✓ whisper_part_00.txt (7.9KB)
  ✓ whisper_part_01.txt (8.7KB)
  ✓ whisper_part_02.txt (7.9KB)
  ✓ whisper_part_03.txt (7.5KB)
  ✓ whisper_part_04.txt (7.2KB)
  ✓ whisper_part_05.txt (7.8KB)
  ✓ whisper_part_06.txt (4.4KB)
  ✓ Merged: full_whisper_transcript.txt (52KB, 704行)

[5/7] Extracting frames (1 every 30s)...
  ✓ 131 frames extracted
  Deduplicating (threshold=20)...
  ✓ 99 key slides after dedup

[6/7] Generating LaTeX document...
  ✓ transcript.tex (60KB, 99张幻灯片, 139个段落)

[7/7] Compiling PDF with xelatex...
  ✓ transcript.pdf (55页, 15MB)
```

### 输出目录结构

```
bilibili_tool/
├── BV1rY411V7Ko.mp4              # 下载的视频 (160MB)
├── audio.mp3                     # 提取的音频 (34MB)
├── audio_parts/                  # 分段音频
│   ├── part_00.mp3 ~ part_06.mp3
│   ├── .done
│   └── .transcribed
├── whisper_part_00.txt ~ 06.txt  # 各段 whisper 转录
├── full_whisper_transcript.txt   # 合并后完整逐字稿 (52KB, 704行)
├── slides/                       # 原始帧 (131张)
├── key_slides/                   # 去重后关键幻灯片 (99张)
├── pdf/
│   ├── transcript.tex            # LaTeX 源文件 (60KB)
│   ├── transcript.pdf            # ✅ 最终 PDF (55页, 15MB)
│   └── images/                   # 幻灯片图片 (99张)
├── Makefile                      # 流水线编排
├── dedup_slides.py               # 帧去重工具
├── gen_transcript_tex.py         # LaTeX 生成器
├── .gitignore
└── WORKFLOW.md                   # 本文档
```

### 产出统计

| 指标 | 数值 |
|------|------|
| 视频时长 | 65 分 22 秒 |
| 音频分段 | 7 段 × 10 分钟 |
| Whisper 模型 | ggml-large-v3-turbo (1.6GB) |
| 转录耗时 | ~3 分钟（7 段并行） |
| 逐字稿 | 52 KB / 704 行 |
| 原始帧 | 131 帧（每 30 秒 1 帧） |
| 去重后 | 99 张关键幻灯片 |
| PDF | 55 页 / 15 MB |

---

## 幂等执行

Makefile 是**幂等**的——每步用 `.done` 哨兵文件标记完成状态，Make 自动跳过已完成的步骤。

- 中断后直接 `make all` 恢复
- 要重做某步，删除其输出：
  - 重新转录：`rm whisper_part*.txt full_whisper_transcript.txt audio_parts/.transcribed`
  - 重新去重：`rm -rf key_slides/ slides/.done`
  - 重新编译 PDF：`rm pdf/transcript.pdf`

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| whisper-cli 未安装 | `brew install whisper-cpp` |
| 没有 whisper 模型 | 见上方"Whisper 模型"下载命令 |
| xelatex 未安装 | `brew install --cask mactex` |
| Pillow 不可用 | `pip3 install --user --break-system-packages Pillow` |
| 视频下载失败 | `brew upgrade yt-dlp` 或 `yt-dlp --cookies-from-browser chrome "URL"` |
| 转录质量差 | 确认用 large-v3-turbo 模型；指定正确的 `-l` 语言参数 |

---

## 后续规划

本工具集将形成一个通用 **skill**，专门针对 B站和 YouTube 视频提取完整版文字 PDF：

- [ ] 支持 YouTube URL 自动识别（yt-dlp 已原生支持）
- [ ] 支持自动检测视频语言
- [ ] 支持 SRT/VTT 字幕输出格式
- [ ] 封装为独立 skill（SKILL.md + assets/）
