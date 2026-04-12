# B站视频 → PDF 完整逐字稿 流水线

一键将B站视频转换为精美的 PDF 文档，包含**完整逐字稿**（语音转文字原始输出，非摘要）并穿插关键幻灯片截图。

## 核心思路

直接使用 `whisper-cli`（whisper.cpp 的命令行工具）进行语音转文字，获取演讲者说的**每一句话**的完整逐字稿，而非经过 LLM 摘要处理的精简版本。

**为什么不用 `summarize` CLI？**

| 方式 | 问题 |
|------|------|
| `summarize audio.mp3` | 输出经过 LLM 摘要处理，丢失大量细节，不是逐字稿 |
| `summarize audio.mp3 --extract-only` | 可获取原始转录，但对超过 10 分钟的音频容易超时 |
| **直接调用 `whisper-cli`** | ✅ 完整逐字稿，支持并行处理长音频，质量可控 |

---

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

---

## 前置依赖

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| `yt-dlp` | `brew install yt-dlp` | 从B站下载视频 |
| `ffmpeg` / `ffprobe` | `brew install ffmpeg` | 提取音频、分段、提取帧 |
| `whisper-cli` | `brew install whisper-cpp` | 语音转文字（本地离线运行） |
| `python3` + `Pillow` | `brew install python3` + `pip install Pillow` | 帧去重（dhash 算法） |
| `xelatex` | `brew install --cask mactex` | 编译 LaTeX → PDF（支持中文） |

### Whisper 模型

脚本默认使用 `ggml-large-v3-turbo`（1.6 GB）以获得最佳转录质量。
如果未找到，会回退到 `ggml-base`（148 MB）。

模型存储路径：`~/.summarize/cache/whisper-cpp/models/`

下载方式：
```bash
# 手动下载 large-v3-turbo 模型（推荐）
mkdir -p ~/.summarize/cache/whisper-cpp/models
curl -L -o ~/.summarize/cache/whisper-cpp/models/ggml-large-v3-turbo.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
```

---

## 流水线 7 步详解

### 整体流程图

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

### Makefile 依赖关系图

```
all → pdf → tex ──────────→ transcript → transcribe → segment → audio → download
              └→ copy-images → dedup → extract-frames ─────────────────→ download
```

---

### 第 1 步：下载视频

```bash
yt-dlp \
    -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
    -o "BVxxxxxxxx.mp4" \
    --merge-output-format mp4 \
    "https://www.bilibili.com/video/BVxxxxxxxx/"
```

| 参数 | 说明 |
|------|------|
| `-f "bestvideo[height<=720]+bestaudio/best[height<=720]"` | 下载 720p 画质（平衡质量与文件大小） |
| `--merge-output-format mp4` | 合并为 MP4 格式 |

### 第 2 步：提取音频

```bash
ffmpeg -i BVxxxxxxxx.mp4 -vn -acodec libmp3lame -q:a 4 audio.mp3 -y
```

| 参数 | 说明 |
|------|------|
| `-vn` | 不包含视频流 |
| `-acodec libmp3lame` | 使用 LAME 编码器输出 MP3 |
| `-q:a 4` | 音频质量等级 4（VBR，约 165 kbps，足够语音识别） |

### 第 3 步：音频分段

```bash
ffmpeg -i audio.mp3 \
    -f segment -segment_time 600 \
    -c copy audio_parts/part_%02d.mp3 -y
```

| 参数 | 说明 |
|------|------|
| `-f segment` | 分段模式 |
| `-segment_time 600` | 每段 600 秒（10 分钟） |
| `-c copy` | 直接复制音频流，不重新编码（速度极快） |
| `part_%02d.mp3` | 输出文件名模板（part_00.mp3, part_01.mp3, ...） |

**为什么要分段？** whisper-cli 处理超长音频时可能内存不足或速度极慢，分段后可以并行处理。

### 第 4 步：语音转录（核心步骤）

**单段转录命令：**

```bash
whisper-cli \
    -m ~/.summarize/cache/whisper-cpp/models/ggml-large-v3-turbo.bin \
    -l en \
    --no-prints \
    -otxt \
    -of whisper_part00 \
    audio_parts/part_00.mp3
```

| 参数 | 说明 |
|------|------|
| `-m ggml-large-v3-turbo.bin` | 使用最高质量的 whisper 模型（1.6GB） |
| `-l en` | 指定语言为英文（避免自动检测误判；中文用 `-l zh`） |
| `--no-prints` | 不输出进度信息到 stderr |
| `-otxt` | 输出纯文本格式（还支持 `-osrt` 字幕、`-ovtt` WebVTT 等） |
| `-of whisper_part00` | 输出文件前缀（生成 `whisper_part00.txt`） |

**并行处理所有段（充分利用多核 CPU）：**

```bash
for part in audio_parts/part_*.mp3; do
    name=$(basename "$part" .mp3)
    whisper-cli \
        -m "$WHISPER_MODEL" \
        -l en \
        --no-prints \
        -otxt \
        -of "whisper_${name}" \
        "$part" &
done
wait
```

**合并为完整逐字稿：**

各段转录结果按顺序合并，每段之间加上时间标记：

```
--- [00:00 - 10:00] Part 1 of 7 ---
（第1段转录文本）

--- [10:00 - 20:00] Part 2 of 7 ---
（第2段转录文本）
...
```

最终产出：`full_whisper_transcript.txt`

### 第 5 步：提取并去重关键帧

**5a. 按固定间隔提取帧：**

```bash
ffmpeg -i BVxxxxxxxx.mp4 \
    -vf "fps=1/30,scale=1280:-1" \
    -q:v 2 \
    slides/frame_%04d.jpg -y
```

| 参数 | 说明 |
|------|------|
| `-vf "fps=1/30"` | 每 30 秒提取一帧（`fps=1/30` 表示每秒 1/30 帧） |
| `scale=1280:-1` | 缩放到宽度 1280px，高度按比例自动计算 |
| `-q:v 2` | JPEG 质量等级 2（高质量，范围 2-31，越小越好） |
| `frame_%04d.jpg` | 输出文件名模板（frame_0001.jpg, frame_0002.jpg, ...） |

**5b. 差分哈希去重：**

```bash
python3 dedup_slides.py \
    --input slides/ \
    --output key_slides/ \
    --threshold 20
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--input` | （必填） | 包含 `frame_XXXX.jpg` 的目录 |
| `--output` | （必填） | 输出 `slide_XXXX.jpg` 的目录 |
| `--threshold` | 20 | 汉明距离阈值，越大保留的幻灯片越少 |

**算法**：对每帧计算 16×16 差分哈希（dhash，256 位），与上一张保留帧的哈希比较汉明距离。仅当距离超过阈值时才保留该帧。

### 第 6 步：生成 LaTeX

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

脚本将逐字稿文本按时间戳与幻灯片图片对齐，穿插排版生成 LaTeX 文件。

### 第 7 步：编译 PDF

```bash
cd pdf/
xelatex -interaction=nonstopmode -halt-on-error fhe_full_transcript.tex
xelatex -interaction=nonstopmode -halt-on-error fhe_full_transcript.tex  # 第二遍生成目录
```

编译两遍是为了正确生成目录（Table of Contents）。使用 `xelatex` 而非 `pdflatex` 是因为需要支持中文字体（通过 `xeCJK` 宏包）。

---

## 配置参数

| Makefile 变量 | Shell 变量 | 默认值 | 说明 |
|---------------|-----------|--------|------|
| `URL` | 第1个参数 | （必填） | B站视频 URL |
| `TITLE` | — | "Video Transcript" | PDF 封面标题 |
| `WHISPER_LANG` | `WHISPER_LANG` | `"en"` | Whisper 语言（`en`/`zh`/`auto`） |
| `SEGMENT_SEC` | `SEGMENT_DURATION` | 600 | 音频分段时长（秒），默认10分钟 |
| `FRAME_INTERVAL` | `FRAME_INTERVAL` | 30 | 每隔 N 秒提取一帧 |
| `DEDUP_THRESH` | `DEDUP_THRESHOLD` | 20 | dhash 去重阈值 |
| `VIDEO_FORMAT` | — | 720p | yt-dlp 格式字符串 |

### 语言配置示例

```bash
# 英文视频（默认）
make URL="..." WHISPER_LANG=en all

# 中文视频
make URL="..." WHISPER_LANG=zh TITLE="我的中文演讲" all

# 自动检测语言
make URL="..." WHISPER_LANG=auto all
```

---

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
├── dedup_slides.py             # 帧去重脚本
├── gen_full_transcript_tex.py  # LaTeX 生成脚本
├── bilibili_video_to_pdf.sh   # 一键流水线脚本
├── Makefile                    # 顶层流水线编排
└── pdf/
    ├── Makefile                # PDF 编译系统
    ├── fhe_full_transcript.tex # LaTeX 源文件
    ├── fhe_full_transcript.pdf # ✅ 最终 PDF 输出
    └── images/                 # LaTeX 引用的幻灯片图片
        ├── slide_0001.jpg
        └── ...
```

---

## 幂等执行

脚本是**幂等**的——每步都会检查输出是否已存在，存在则跳过。这意味着：

- 如果脚本中断，直接重新运行即可恢复
- 如果想重做某一步，先删除该步的输出文件
- 例如：要重新转录，删除 `whisper_part*.txt` 和 `full_whisper_transcript.txt`

---

## 常见问题

### whisper-cli 找不到或未安装

```bash
brew install whisper-cpp
```

### 没有 whisper 模型文件

```bash
mkdir -p ~/.summarize/cache/whisper-cpp/models
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

### 转录质量不好

- 确认使用的是 `ggml-large-v3-turbo` 模型而非 `ggml-base`
- 确认 `-l` 参数指定了正确的语言（不要依赖 auto）
- 如果音频有背景噪音，可以先用 ffmpeg 降噪：
  ```bash
  ffmpeg -i audio.mp3 -af "highpass=f=200,lowpass=f=3000,afftdn=nf=-25" audio_clean.mp3
  ```

---

## 示例：FHE 演讲（BV1rY411V7Ko）

本目录包含了对 Craig Gentry 在 EUROCRYPT 2021 上关于全同态加密（FHE）的邀请报告的处理结果：

| 项目 | 数据 |
|------|------|
| **视频** | [BV1rY411V7Ko](https://www.bilibili.com/video/BV1rY411V7Ko/) |
| **时长** | 65 分 22 秒 |
| **语言** | 英文 |
| **Whisper 模型** | `ggml-large-v3-turbo`（1.6 GB） |
| **音频分段** | 7 段（每段 10 分钟） |
| **逐字稿** | 52 KB，683 行完整转录文本 |
| **原始帧** | 131 帧（每 30 秒 1 帧） |
| **关键幻灯片** | 99 张（dhash 去重，threshold=20） |
| **PDF 输出** | 55 页，14.1 MB |

### 复现命令

```bash
# 方式一：Makefile
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" \
     TITLE="A Decade (or So) of Fully Homomorphic Encryption" \
     WHISPER_LANG=en \
     all

# 方式二：Shell 脚本
./bilibili_video_to_pdf.sh "https://www.bilibili.com/video/BV1rY411V7Ko/"
```
