# B站/YouTube 视频 → PDF 完整逐字稿 工具集

一键将B站（或YouTube）视频转换为精美的 PDF 文档，包含**完整逐字稿**（whisper 语音转文字原始输出）并穿插关键幻灯片截图。

支持两种发布模式：
- **LaTeX 模式**（`publish_tex/`）：使用 xelatex 编译，排版质量最佳
- **Markdown 模式**（`publish_md/`）：使用 Python 工具转换，无需安装 LaTeX

此外，还支持由大模型完成的后续步骤：**英文逐字稿 → 中文翻译** 和 **中文翻译 → Beamer/PPTX 演示文稿**。

---

## 工具清单

```
bilibili_tool/
├── Makefile                      # 顶层流水线编排（支持 tex/md 双模式）
├── Makefile.publish_tex.template # publish_tex/ 子目录 Makefile 模板（xelatex 编译）
├── Makefile.publish_md.template  # publish_md/ 子目录 Makefile 模板（Python 转换）
├── transcript_utils.py           # 共享解析模块（时间戳对齐、转录解析）
├── dedup_slides.py               # 帧去重工具（dhash 算法，仅依赖 Pillow）
├── gen_transcript_tex.py         # LaTeX 逐字稿生成器（调用 transcript_utils）
├── gen_transcript_md.py          # Markdown 逐字稿生成器（调用 transcript_utils）
├── gen_presentation.py           # 演示稿生成器（translate + beamer，过渡性脚本/scaffold）
├── md2pdf.py                     # Markdown → PDF 转换器（weasyprint）
├── md2pptx.py                    # Markdown slides → PPTX 转换器（python-pptx）
├── config.env                    # 项目配置（URL、标题、语言、发布模式等）
├── merge_transcript.py           # Whisper 转录合并工具
├── .gitignore                    # Git 忽略规则
└── WORKFLOW.md                   # 本文档
```

---

## 快速开始

```bash
# 完整流水线：一行命令，URL → PDF（自动检测 tex/md 模式）
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" all

# 强制使用 LaTeX 模式
make URL="..." PUBLISH_MODE=tex all
# 或使用快捷方式
make URL="..." all-tex

# 强制使用 Markdown 模式（无需 LaTeX）
make URL="..." PUBLISH_MODE=md all
# 或使用快捷方式
make URL="..." all-md

# 自定义标题和语言
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" \
     TITLE="FHE十年发展" WHISPER_LANG=en all

# 单独运行某些步骤
make URL="..." transcript     # 仅下载 + 转录
make URL="..." slides         # 仅下载 + 提取帧 + 去重
make pdf                      # 仅重新编译 PDF

# 查看帮助和当前配置
make help
make info
```

---

## 前置依赖

### 通用依赖（两种模式都需要）

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| `yt-dlp` | `brew install yt-dlp` | 从B站/YouTube下载视频 |
| `ffmpeg` / `ffprobe` | `brew install ffmpeg` | 提取音频、分段、提取帧 |
| `whisper-cli` | `brew install whisper-cpp` | 语音转文字（本地离线） |
| `python3` + `Pillow` | `brew install python3` + `pip install Pillow` | 帧去重 |

### LaTeX 模式额外依赖（`PUBLISH_MODE=tex`）

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| `xelatex` | `brew install --cask mactex` | 编译 LaTeX → PDF |

### Markdown 模式额外依赖（`PUBLISH_MODE=md`）

| 工具 | 安装方式 | 用途 |
|------|----------|------|
| `markdown` | `pip3 install markdown` | Markdown 解析 |
| `weasyprint` | `pip3 install weasyprint` | HTML → PDF 转换 |
| `python-pptx` | `pip3 install python-pptx` | 生成 PPTX 演示文稿 |
| `Pillow` | `pip3 install Pillow` | PPTX 图片处理 |

### Whisper 模型

```bash
# 下载 large-v3-turbo 模型（1.6GB，推荐）
mkdir -p ~/.summarize/cache/whisper-cpp/models
curl -L -o ~/.summarize/cache/whisper-cpp/models/ggml-large-v3-turbo.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin"
```

---

## 发布模式

### 模式选择逻辑

```
PUBLISH_MODE 配置值:
  auto (默认) → 检测 xelatex 是否安装
                  ├─ 已安装 → tex 模式 → publish_tex/
                  └─ 未安装 → md 模式  → publish_md/
  tex          → 强制 LaTeX 模式      → publish_tex/
  md           → 强制 Markdown 模式   → publish_md/
```

### LaTeX 模式（`publish_tex/`）

- 使用 `gen_transcript_tex.py` 生成 `.tex` 文件
- 使用 `xelatex` 编译为 PDF
- 排版质量最佳，支持精美的中文排版
- 大模型辅助步骤生成 `.tex` 格式文件
- Beamer 演示稿编译为 `.pdf`

### Markdown 模式（`publish_md/`）

- 使用 `gen_transcript_md.py` 生成 `.md` 文件
- 使用 `md2pdf.py`（基于 weasyprint）转换为 PDF
- 无需安装 LaTeX，仅需 Python 包
- 大模型辅助步骤生成 `.md` 格式文件
- 演示稿使用 `python-pptx` 生成 `.pptx`

---

## 流水线步骤

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Makefile + 大模型（双模式）                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─ 自动化流水线（Makefile 驱动）──────────────────────────────────┐ │
│  │  第1步：下载视频         yt-dlp → BVxxxxxxxx.mp4 (720p)         │ │
│  │  第2步：提取音频         ffmpeg → audio.mp3                      │ │
│  │  第3步：音频分段         ffmpeg -f segment → part_00~06.mp3      │ │
│  │  第4步：语音转录（并行）  whisper-cli → whisper_partXX.txt        │ │
│  │                          合并 → full_whisper_transcript.txt      │ │
│  │  第5步：提取+去重帧      ffmpeg + dedup_slides.py → key_slides/  │ │
│  │  第6步：生成文档                                                 │ │
│  │    tex模式: gen_transcript_tex.py → publish_tex/transcript.tex   │ │
│  │    md模式:  gen_transcript_md.py  → publish_md/transcript.md     │ │
│  │  第7步：编译 PDF                                                 │ │
│  │    tex模式: xelatex ×2 → transcript.pdf                          │ │
│  │    md模式:  md2pdf.py  → transcript.pdf                          │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌─ 大模型辅助步骤（由 AI Agent / Skill 执行）────────────────────┐ │
│  │  第8步：中文翻译                                                 │ │
│  │    tex模式: transcript.tex    → transcript_zh.tex                │ │
│  │    md模式:  transcript.md     → transcript_zh.md                 │ │
│  │  第9步：演示文稿                                                 │ │
│  │    tex模式: transcript_zh.tex → slides.tex  → slides.pdf         │ │
│  │    md模式:  transcript_zh.md  → slides.md   → slides.pptx        │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Make 依赖关系图

```
all → pdf → doc ──────────→ transcript → transcribe → segment → audio → download
              └→ copy-images → dedup → extract-frames ─────────────────→ download

# 大模型辅助步骤（不在 make all 中，由 AI Agent 单独执行）
# tex模式:
transcript.tex ──(大模型翻译)──→ transcript_zh.tex ──(大模型生成)──→ slides.tex
# md模式:
transcript.md  ──(大模型翻译)──→ transcript_zh.md  ──(大模型生成)──→ slides.md
```

---

## 配置参数

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `URL` | （必填） | 视频 URL |
| `TITLE` | "Video Transcript" | PDF 封面标题 |
| `PUBLISH_MODE` | `auto` | 发布模式：`tex` / `md` / `auto`（自动检测 xelatex） |
| `TRANSLATE_ZH` | `auto` | 是否翻译中文：`yes` / `no` / `auto`（大模型根据语言决定） |
| `WHISPER_LANG` | `en` | Whisper 语言（`en`/`zh`/`auto`） |
| `SEGMENT_SEC` | 600 | 音频分段时长（秒） |
| `FRAME_INTERVAL` | 30 | 每隔 N 秒提取一帧 |
| `DEDUP_THRESH` | 20 | dhash 去重阈值 |
| `VIDEO_FORMAT` | 720p | yt-dlp 格式字符串 |

### TRANSLATE_ZH 配置说明

| 值 | 行为 |
|------|------|
| `yes` | 始终翻译为中文（scaffold 脚本执行占位翻译，将来由大模型替代） |
| `no` | 跳过中文翻译 |
| `auto` | 根据 `WHISPER_LANG` 自动决定：源语言非中文时翻译，源语言为中文时跳过 |

> **注意**：`TRANSLATE_ZH` 现已在 Makefile 中真正生效。`auto` 模式下，
> 当 `WHISPER_LANG=zh` 时自动跳过翻译，其他语言自动执行翻译。

---

## 大模型辅助步骤详解

### 第 8 步：英文逐字稿 → 中文翻译

**执行者**：
- **当前**：`gen_presentation.py translate`（scaffold 占位，仅复制文件）
- **将来**：大模型（AI Agent / Skill）直接执行高质量翻译

**是否执行**：由 `TRANSLATE_ZH` 配置控制（`yes` / `no` / `auto`），在 Makefile 中已实现条件分支

**运行方式**：
```bash
# scaffold 模式（当前）
make translate

# 将来由大模型直接读取 publish_*/transcript.* 并输出 transcript_zh.*
```

**tex 模式**：
- 输入：`publish_tex/transcript.tex`
- 输出：`publish_tex/transcript_zh.tex`

**md 模式**：
- 输入：`publish_md/transcript.md`
- 输出：`publish_md/transcript_zh.md`

**翻译要求**：
- 保留所有文档结构（标题、图片引用、时间戳等）
- 技术术语保留英文并附中文，如：全同态加密（FHE）
- 人名、会议名保留英文
- 封面标题改为中英双语
- section 标题翻译为中文
- 翻译风格：自然流畅的中文技术写作，非逐字翻译

**编译**：
```bash
# tex 模式
cd publish_tex/ && make

# md 模式
cd publish_md/ && make
```

### 第 9 步：中文翻译 → 演示文稿

**执行者**：
- **当前**：`gen_presentation.py beamer`（scaffold 启发式提取，质量有限）
- **将来**：大模型（AI Agent / Skill）直接执行智能内容提炼

**运行方式**：
```bash
# scaffold 模式（当前）
make beamer

# 将来由大模型直接读取 transcript_zh.* 并输出 slides.*
```

**tex 模式**：
- 输入：`publish_tex/transcript_zh.tex`
- 输出：`publish_tex/slides.tex`（Beamer 演示文稿）
- 编译：`cd publish_tex/ && make beamer`

**md 模式**：
- 输入：`publish_md/transcript_zh.md`
- 输出：`publish_md/slides.md`（Markdown 格式演示稿）
- 转换：`cd publish_md/ && make pptx`

**为什么当前用 scaffold 脚本而非直接调 LLM？**
- 让流水线可以端到端跑通，不依赖外部 LLM API
- scaffold 输出质量有限，但足以验证下游渲染链路
- 将来制作成 Skill 时，由大模型直接替代 scaffold
- 大模型可以理解上下文，翻译质量远优于机器翻译
- 演示稿需要对内容进行高度提炼和重组
- 不同视频的内容结构差异大，难以用模板化脚本处理

---

## 各脚本说明

### `transcript_utils.py`

共享解析模块，被 `gen_transcript_tex.py` 和 `gen_transcript_md.py` 共同引用。

- `build_slide_timestamps(base_dir, duration)` — 将幻灯片文件名映射到视频时间戳
- `read_transcript(base_dir, segment_sec)` — 解析 whisper 转录文件为 `(timestamp, text)` 列表

### `dedup_slides.py`

使用差分哈希（dhash）去除近似重复帧。仅依赖 Pillow。

```bash
python3 dedup_slides.py --input slides/ --output key_slides/ --threshold 20 --frame-interval 30
```

### `gen_transcript_tex.py`

从 whisper 逐字稿 + 关键幻灯片生成 LaTeX 文档。

```bash
python3 gen_transcript_tex.py --base . --title "标题" --url "URL" --output publish_tex/transcript.tex
```

### `gen_transcript_md.py`

从 whisper 逐字稿 + 关键幻灯片生成 Markdown 文档（LaTeX 不可用时的退化方案）。

```bash
python3 gen_transcript_md.py --base . --title "标题" --url "URL" --output publish_md/transcript.md
```

### `md2pdf.py`

将 Markdown 转换为 PDF，使用 weasyprint 引擎。支持 CJK 中文。

```bash
python3 md2pdf.py --input transcript.md --output transcript.pdf --images images/
```

### `md2pptx.py`

将结构化 Markdown 幻灯片转换为 PPTX 演示文稿。这是"渲染层"脚本——负责排版和视觉呈现。

"内容层"（决定每页放什么内容）由大模型生成 `slides.md`，本脚本只负责将其转为美观的 `.pptx`。

支持的 Markdown 格式：
- `# 标题` → 标题页
- `## 标题` → 内容页标题
- `- 要点` → 要点列表
- `![说明](images/xxx.jpg)` → 嵌入图片
- `---` → 幻灯片分隔符
- `> 备注` → 演讲者备注

```bash
python3 md2pptx.py --input slides.md --output slides.pptx --images images/
```

### `gen_presentation.py`

过渡性 scaffold 脚本，提供 `translate` 和 `beamer` 两个子命令。将来由大模型 Skill 替代。

- `translate`：占位翻译（当前仅复制文件，将来由 LLM 执行高质量翻译）
- `beamer`：从逐字稿提取关键内容生成 `slides.md`（简单启发式，将来由 LLM 智能提炼）
- 支持 Markdown 和 LaTeX 两种输入格式

```bash
# 翻译（scaffold 占位）
python3 gen_presentation.py translate --input publish_md/transcript.md --output publish_md/transcript_zh.md

# 生成幻灯片
python3 gen_presentation.py beamer --input publish_md/transcript_zh.md --output publish_md/slides.md --title "标题" --url "URL"
```

---

## 实际运行示例：FHE 演讲（BV1rY411V7Ko）

以 Craig Gentry 在 EUROCRYPT 2021 上关于全同态加密的邀请报告为例。

### 执行命令

```bash
# LaTeX 模式（默认，如果已安装 xelatex）
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" \
     TITLE="A Decade (or So) of Fully Homomorphic Encryption" \
     WHISPER_LANG=en \
     all

# Markdown 模式（无需 LaTeX）
make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" \
     TITLE="A Decade (or So) of Fully Homomorphic Encryption" \
     WHISPER_LANG=en \
     PUBLISH_MODE=md \
     all
```

### 输出目录结构

```
bilibili_tool/
├── BV1rY411V7Ko.mp4              # 下载的视频 (160MB)
├── audio.mp3                     # 提取的音频 (34MB)
├── audio_parts/                  # 分段音频
├── whisper_part_00.txt ~ 06.txt  # 各段 whisper 转录
├── full_whisper_transcript.txt   # 合并后完整逐字稿 (52KB)
├── slides/                       # 原始帧 (131张)
├── key_slides/                   # 去重后关键幻灯片 (99张)
│
├── publish_tex/                  # LaTeX 模式输出
│   ├── Makefile                  # xelatex 编译系统
│   ├── transcript.tex            # 英文逐字稿 LaTeX
│   ├── transcript.pdf            # ✅ 英文 PDF
│   ├── transcript_zh.tex         # 中文翻译版 [大模型生成]
│   ├── transcript_zh.pdf         # ✅ 中文 PDF
│   ├── slides.tex                # Beamer 演示稿 [大模型生成]
│   ├── slides.pdf                # ✅ Beamer PDF
│   └── images/                   # 幻灯片图片
│
├── publish_md/                   # Markdown 模式输出
│   ├── Makefile                  # Python 转换系统
│   ├── md2pdf.py                 # Markdown → PDF 转换器
│   ├── transcript.md             # 英文逐字稿 Markdown
│   ├── transcript.pdf            # ✅ 英文 PDF
│   ├── transcript_zh.md          # 中文翻译版 [大模型生成]
│   ├── transcript_zh.pdf         # ✅ 中文 PDF
│   ├── slides.md                 # 演示稿 Markdown [大模型生成]
│   ├── slides.pptx               # ✅ PPTX 演示文稿
│   └── images/                   # 幻灯片图片
│
├── transcript_utils.py           # 共享解析模块
├── Makefile                      # 流水线编排（双模式）
├── Makefile.publish_tex.template # LaTeX 模式 Makefile 模板
├── Makefile.publish_md.template  # Markdown 模式 Makefile 模板
├── config.env                    # 配置文件
├── dedup_slides.py               # 帧去重工具
├── gen_transcript_tex.py         # LaTeX 生成器
├── gen_transcript_md.py          # Markdown 生成器
├── gen_presentation.py           # 演示稿生成器（过渡性脚本）
├── md2pdf.py                     # Markdown → PDF 转换器
├── md2pptx.py                    # Markdown slides → PPTX 转换器
├── merge_transcript.py           # 转录合并工具
├── .gitignore
└── WORKFLOW.md                   # 本文档
```

---

## 幂等执行

Makefile 是**幂等**的——每步用 `.done` 哨兵文件标记完成状态，Make 自动跳过已完成的步骤。

- 中断后直接 `make all` 恢复
- 要重做某步，删除其输出：
  - 重新转录：`rm whisper_part*.txt full_whisper_transcript.txt audio_parts/.transcribed`
  - 重新去重：`rm -rf key_slides/ slides/.done`
  - 重新编译 PDF：`rm publish_tex/transcript.pdf` 或 `rm publish_md/transcript.pdf`

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| whisper-cli 未安装 | `brew install whisper-cpp` |
| 没有 whisper 模型 | 见上方"Whisper 模型"下载命令 |
| xelatex 未安装 | `brew install --cask mactex` 或使用 `PUBLISH_MODE=md` |
| weasyprint 不可用 | `pip3 install weasyprint`（md 模式需要） |
| Pillow 不可用 | `pip3 install --user --break-system-packages Pillow` |
| 视频下载失败 | `brew upgrade yt-dlp` 或 `yt-dlp --cookies-from-browser chrome "URL"` |
| 转录质量差 | 确认用 large-v3-turbo 模型；指定正确的 `-l` 语言参数 |
| 想同时生成两种格式 | 先 `make all-tex`，再 `make all-md` |

---

## 后续规划

本工具集将形成一个通用 **skill**，专门针对 B站和 YouTube 视频提取完整版文字 PDF：

- [x] 支持 YouTube URL 自动识别（yt-dlp 已原生支持，Makefile 已兼容 BV/YouTube ID）
- [ ] 支持自动检测视频语言
- [ ] 支持 SRT/VTT 字幕输出格式
- [x] 大模型辅助：英文逐字稿 → 中文翻译（第 8 步，当前 scaffold 占位）
- [x] 大模型辅助：中文翻译 → Beamer/PPTX 演示文稿（第 9 步，当前 scaffold 占位）
- [x] 双发布模式：LaTeX（publish_tex/）和 Markdown（publish_md/）
- [x] 自动检测 xelatex 可用性，智能选择发布模式
- [x] TRANSLATE_ZH 配置项，控制中文翻译行为（已在 Makefile 中实现条件分支）
- [ ] 封装为独立 skill（SKILL.md + assets/）

### Skill 设计备忘

将来封装为 Skill 时的关键设计点：

1. **翻译步骤**（第 8 步）由 Skill 中的大模型直接执行，不依赖外部翻译 API 或脚本
2. **演示稿生成**（第 9 步）同样由大模型直接生成，不使用模板化脚本
3. 大模型需要读取逐字稿的完整内容作为输入（`.tex` 或 `.md`）
4. 输出必须是可直接编译/转换的文件
5. `TRANSLATE_ZH` 配置让大模型决定是否翻译：
   - `auto` 模式下，大模型根据 `WHISPER_LANG` 判断
   - 源语言为中文时跳过翻译，直接生成演示稿
6. 两种发布模式的 Makefile 模板已支持条件编译：
   - 自动检测翻译版文件是否存在
   - 自动检测演示稿文件是否存在
   - `make` 只编译/转换存在的文件
