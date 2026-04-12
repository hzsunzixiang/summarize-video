# ============================================================================
# Makefile — Bilibili / YouTube Video → PDF Transcript Pipeline
#
# Usage:
#   1. Edit config.env (fill in URL and TITLE)
#   2. make all               # run full pipeline (auto-detect tex/md mode)
#
#   make all-tex              # force LaTeX mode
#   make all-md               # force Markdown mode
#   make pdf                  # recompile PDF only (current mode)
#   make transcript           # download + transcribe only
#   make slides               # download + extract frames only
#   make clean                # remove auxiliary files
#   make distclean            # remove ALL generated files
#   make help                 # show all targets
#
# Parameters can also be overridden on command line:
#   make URL="..." TITLE="..." all
#   make PUBLISH_MODE=md all  # force Markdown mode
#
# Idempotent: each step checks if output exists and skips.
# To force re-run, delete the output first.
# ============================================================================

# ── Load configuration from config.env ───────────────────────────────────────
-include config.env

# ── Default values (used if not set in config.env or command line) ───────────
URL            ?=
TITLE          ?= Video Transcript
WHISPER_LANG   ?= en
SEGMENT_SEC    ?= 600
FRAME_INTERVAL ?= 30
DEDUP_THRESH   ?= 20
VIDEO_FORMAT   ?= bestvideo[height<=720]+bestaudio/best[height<=720]
COOKIES_BROWSER ?=
PUBLISH_MODE   ?= auto
TRANSLATE_ZH   ?= auto

# ── Resolve PUBLISH_MODE ─────────────────────────────────────────────────────
# auto → detect xelatex availability
ifeq ($(PUBLISH_MODE),auto)
  HAS_XELATEX := $(shell command -v xelatex >/dev/null 2>&1 && echo yes || echo no)
  ifeq ($(HAS_XELATEX),yes)
    RESOLVED_MODE := tex
  else
    RESOLVED_MODE := md
  endif
else
  RESOLVED_MODE := $(PUBLISH_MODE)
endif

# ── Resolve TRANSLATE_ZH ──────────────────────────────────────────────────────
# auto → decide based on WHISPER_LANG (translate if source is not Chinese)
ifeq ($(TRANSLATE_ZH),auto)
  ifeq ($(WHISPER_LANG),zh)
    RESOLVED_TRANSLATE := no
  else
    RESOLVED_TRANSLATE := yes
  endif
else
  RESOLVED_TRANSLATE := $(TRANSLATE_ZH)
endif

# ── Derived variables ────────────────────────────────────────────────────────
# Support both Bilibili (BV...) and YouTube (watch?v=... or youtu.be/...) URLs
BV_ID          := $(shell echo "$(URL)" | grep -oE 'BV[a-zA-Z0-9]+' | head -1)
YT_ID          := $(shell echo "$(URL)" | grep -oP '(?:v=|youtu\.be/)[a-zA-Z0-9_-]+' | head -1 | sed 's/^v=//')
VIDEO_ID       := $(if $(BV_ID),$(BV_ID),$(YT_ID))
VIDEO          := $(VIDEO_ID).mp4
AUDIO          := audio.mp3
PARTS_DIR      := audio_parts
SLIDES_DIR     := slides
KEY_SLIDES_DIR := key_slides
TRANSCRIPT     := full_whisper_transcript.txt

# Mode-specific directories and files
ifeq ($(RESOLVED_MODE),tex)
  PUBLISH_DIR    := publish_tex
  PUB_TEMPLATE   := Makefile.publish_tex.template
  DOC_FILE       := $(PUBLISH_DIR)/transcript.tex
  DOC_PDF        := $(PUBLISH_DIR)/transcript.pdf
  DOC_ZH_FILE    := $(PUBLISH_DIR)/transcript_zh.tex
  BEAMER_FILE    := $(PUBLISH_DIR)/slides.tex
  BEAMER_OUT     := $(PUBLISH_DIR)/slides.pdf
else
  PUBLISH_DIR    := publish_md
  PUB_TEMPLATE   := Makefile.publish_md.template
  DOC_FILE       := $(PUBLISH_DIR)/transcript.md
  DOC_PDF        := $(PUBLISH_DIR)/transcript.pdf
  DOC_ZH_FILE    := $(PUBLISH_DIR)/transcript_zh.md
  BEAMER_FILE    := $(PUBLISH_DIR)/slides.md
  BEAMER_OUT     := $(PUBLISH_DIR)/slides.pptx
endif

PUB_MAKEFILE   := $(PUBLISH_DIR)/Makefile

# Whisper model auto-detect
WHISPER_MODELS ?= $(HOME)/.summarize/cache/whisper-cpp/models
WHISPER_MODEL  := $(shell \
	if [ -f "$(WHISPER_MODELS)/ggml-large-v3-turbo.bin" ]; then \
		echo "$(WHISPER_MODELS)/ggml-large-v3-turbo.bin"; \
	elif [ -f "$(WHISPER_MODELS)/ggml-base.bin" ]; then \
		echo "$(WHISPER_MODELS)/ggml-base.bin"; \
	fi)

# ── Phony targets ───────────────────────────────────────────────────────────
.PHONY: all all-tex all-md pdf transcript slides dedup tex markdown \
        download audio segment transcribe merge-transcript \
        extract-frames copy-images \
        translate beamer presentation \
        check-url check-deps check-deps-tex check-deps-md \
        info clean distclean help

# ── Default target ───────────────────────────────────────────────────────────
all: check-url check-deps pdf
	@echo ""
	@echo "============================================"
	@echo "  ✅ Pipeline complete! (mode: $(RESOLVED_MODE))"
	@echo "============================================"
	@echo "  Video:       $(VIDEO)"
	@echo "  Transcript:  $(TRANSCRIPT)"
	@echo "  Key slides:  $(KEY_SLIDES_DIR)/"
	@echo "  Output:      $(PUBLISH_DIR)/"
	@echo "  PDF:         $(DOC_PDF)"
	@echo ""

# ── Force-mode aliases ───────────────────────────────────────────────────────
all-tex:
	@$(MAKE) PUBLISH_MODE=tex all

all-md:
	@$(MAKE) PUBLISH_MODE=md all

# ── Convenience aliases ──────────────────────────────────────────────────────
transcript: check-url check-deps merge-transcript
slides:     check-url check-deps dedup
presentation: check-url check-deps beamer

# ── Validation ───────────────────────────────────────────────────────────────
check-url:
ifeq ($(VIDEO_ID),)
	$(error URL is required. Usage: make URL="https://www.bilibili.com/video/BVxxxxxxxx/" or YouTube URL)
endif

check-deps: check-deps-common check-deps-$(RESOLVED_MODE)

check-deps-common:
	@command -v yt-dlp      >/dev/null 2>&1 || { echo "ERROR: yt-dlp not found.      Install: brew install yt-dlp"; exit 1; }
	@command -v ffmpeg      >/dev/null 2>&1 || { echo "ERROR: ffmpeg not found.      Install: brew install ffmpeg"; exit 1; }
	@command -v ffprobe     >/dev/null 2>&1 || { echo "ERROR: ffprobe not found.     Install: brew install ffmpeg"; exit 1; }
	@command -v whisper-cli >/dev/null 2>&1 || { echo "ERROR: whisper-cli not found. Install: brew install whisper-cpp"; exit 1; }
	@command -v python3     >/dev/null 2>&1 || { echo "ERROR: python3 not found.     Install: brew install python3"; exit 1; }
	@test -n "$(WHISPER_MODEL)" || { echo "ERROR: No whisper model found in $(WHISPER_MODELS)"; exit 1; }

check-deps-tex:
	@command -v xelatex     >/dev/null 2>&1 || { echo "ERROR: xelatex not found.     Install: brew install --cask mactex"; exit 1; }

check-deps-md:
	@python3 -c "import markdown" 2>/dev/null || { echo "WARNING: markdown not found. Install: pip3 install markdown"; }
	@python3 -c "import weasyprint" 2>/dev/null || { echo "WARNING: weasyprint not found. Install: pip3 install weasyprint"; }
	@python3 -c "import pptx" 2>/dev/null || { echo "WARNING: python-pptx not found. Install: pip3 install python-pptx"; }
	@python3 -c "from PIL import Image" 2>/dev/null || { echo "WARNING: Pillow not found. Install: pip3 install Pillow"; }

# ── Step 1: Download video ──────────────────────────────────────────────────
download: $(VIDEO)

# Build yt-dlp cookie flag if COOKIES_BROWSER is set
YTDLP_COOKIE_FLAG := $(if $(COOKIES_BROWSER),--cookies-from-browser $(COOKIES_BROWSER),)

$(VIDEO):
	@echo "[1/7] Downloading video $(VIDEO_ID)..."
	yt-dlp $(YTDLP_COOKIE_FLAG) -f "$(VIDEO_FORMAT)" -o "$@" --merge-output-format mp4 "$(URL)"
	@echo "  ✓ Downloaded: $@ ($$(du -h "$@" | cut -f1))"

# ── Step 2: Extract audio ───────────────────────────────────────────────────
audio: $(AUDIO)

$(AUDIO): $(VIDEO)
	@echo "[2/7] Extracting audio..."
	ffmpeg -i $< -vn -acodec libmp3lame -q:a 4 $@ -y 2>/dev/null
	@echo "  ✓ Audio: $@ ($$(du -h "$@" | cut -f1))"

# ── Step 3: Segment audio ───────────────────────────────────────────────────
segment: $(PARTS_DIR)/.done

$(PARTS_DIR)/.done: $(AUDIO)
	@echo "[3/7] Segmenting audio into $(SEGMENT_SEC)s chunks..."
	@mkdir -p $(PARTS_DIR)
	ffmpeg -i $< -f segment -segment_time $(SEGMENT_SEC) -c copy $(PARTS_DIR)/part_%02d.mp3 -y 2>/dev/null
	@touch $@
	@echo "  ✓ Segments: $$(ls $(PARTS_DIR)/part_*.mp3 | wc -l | tr -d ' ') parts"

# ── Step 4: Transcribe with whisper ─────────────────────────────────────────
transcribe: $(PARTS_DIR)/.transcribed

$(PARTS_DIR)/.transcribed: $(PARTS_DIR)/.done
	@echo "[4/7] Transcribing with whisper (model: $$(basename $(WHISPER_MODEL)))..."
	@for part in $(PARTS_DIR)/part_*.mp3; do \
		name=$$(basename "$$part" .mp3); \
		out="whisper_$${name}"; \
		if [ -f "$${out}.txt" ] && [ -s "$${out}.txt" ]; then \
			echo "  ✓ $$name already transcribed"; \
		else \
			echo "  ⏳ Transcribing $$name..."; \
			whisper-cli -m "$(WHISPER_MODEL)" -l "$(WHISPER_LANG)" --no-prints -otxt -of "$$out" "$$part" 2>/dev/null & \
		fi; \
	done; \
	wait
	@touch $@
	@echo "  ✓ All parts transcribed"

merge-transcript: $(TRANSCRIPT)

$(TRANSCRIPT): $(PARTS_DIR)/.transcribed
	@echo "  Merging transcripts..."
	python3 merge_transcript.py --parts-dir $(PARTS_DIR) --segment-sec $(SEGMENT_SEC) --output $@

# ── Step 5: Extract & deduplicate frames ────────────────────────────────────
extract-frames: $(SLIDES_DIR)/.done

$(SLIDES_DIR)/.done: $(VIDEO)
	@echo "[5/7] Extracting frames (1 every $(FRAME_INTERVAL)s)..."
	@mkdir -p $(SLIDES_DIR)
	ffmpeg -i $< -vf "fps=1/$(FRAME_INTERVAL),scale=1280:-1" -q:v 2 $(SLIDES_DIR)/frame_%04d.jpg -y 2>/dev/null
	@touch $@
	@echo "  ✓ Frames: $$(ls $(SLIDES_DIR)/frame_*.jpg | wc -l | tr -d ' ')"

dedup: $(KEY_SLIDES_DIR)/.done

$(KEY_SLIDES_DIR)/.done: $(SLIDES_DIR)/.done
	@echo "  Deduplicating frames (threshold=$(DEDUP_THRESH))..."
	python3 dedup_slides.py --input $(SLIDES_DIR) --output $(KEY_SLIDES_DIR) --threshold $(DEDUP_THRESH) --frame-interval $(FRAME_INTERVAL)
	@touch $@

copy-images: $(PUBLISH_DIR)/images/.done

$(PUBLISH_DIR)/images/.done: $(KEY_SLIDES_DIR)/.done
	@echo "  Copying key slides to $(PUBLISH_DIR)/images/..."
	@mkdir -p $(PUBLISH_DIR)/images
	@cp $(KEY_SLIDES_DIR)/slide_*.jpg $(PUBLISH_DIR)/images/ 2>/dev/null || true
	@touch $@

# ── Step 6: Generate document (tex or md) ───────────────────────────────────
ifeq ($(RESOLVED_MODE),tex)

tex: $(DOC_FILE)

$(DOC_FILE): $(TRANSCRIPT) $(KEY_SLIDES_DIR)/.done $(VIDEO)
	@echo "[6/7] Generating LaTeX document..."
	@mkdir -p $(PUBLISH_DIR)
	$(eval DURATION := $(shell ffprobe -v error -show_entries format=duration \
		-of default=noprint_wrappers=1:nokey=1 $(VIDEO) 2>/dev/null | cut -d. -f1))
	python3 gen_transcript_tex.py --base . --title "$(TITLE)" --url "$(URL)" \
		--duration $(DURATION) --segment-sec $(SEGMENT_SEC) --output "$(DOC_FILE)"
	@cp $(PUB_TEMPLATE) $(PUB_MAKEFILE)
	@echo "  ✓ LaTeX: $@ ($$(wc -c < "$@") bytes)"

else

markdown: $(DOC_FILE)

$(DOC_FILE): $(TRANSCRIPT) $(KEY_SLIDES_DIR)/.done $(VIDEO)
	@echo "[6/7] Generating Markdown document..."
	@mkdir -p $(PUBLISH_DIR)
	$(eval DURATION := $(shell ffprobe -v error -show_entries format=duration \
		-of default=noprint_wrappers=1:nokey=1 $(VIDEO) 2>/dev/null | cut -d. -f1))
	python3 gen_transcript_md.py --base . --title "$(TITLE)" --url "$(URL)" \
		--duration $(DURATION) --segment-sec $(SEGMENT_SEC) --output "$(DOC_FILE)"
	@cp $(PUB_TEMPLATE) $(PUB_MAKEFILE)
	@echo "  ✓ Markdown: $@ ($$(wc -c < "$@") bytes)"

endif

# ── Step 7a: Translate transcript → Chinese (scaffold, LLM replaces this) ───
# TRANSLATE_ZH controls whether this step runs:
#   yes  → always translate
#   no   → skip
#   auto → resolved based on WHISPER_LANG (see RESOLVED_TRANSLATE)
translate: $(DOC_ZH_FILE)

$(DOC_ZH_FILE): $(DOC_FILE)
ifeq ($(RESOLVED_TRANSLATE),yes)
	@echo "[7a] Translating transcript to Chinese (scaffold)..."
	python3 gen_presentation.py translate --input $(DOC_FILE) --output $(DOC_ZH_FILE)
	@echo "  ✓ Chinese translation: $@ ($$(wc -c < "$@") bytes)"
else
	@echo "[7a] Skipping translation (TRANSLATE_ZH=$(TRANSLATE_ZH), WHISPER_LANG=$(WHISPER_LANG))"
endif

# ── Step 7b: Generate Beamer/PPTX slides (scaffold, LLM replaces this) ──────
# Input: translated transcript (or original if no translation)
beamer: $(BEAMER_FILE)

$(BEAMER_FILE): $(DOC_FILE)
	@echo "[7b] Generating presentation (scaffold)..."
	@mkdir -p $(PUBLISH_DIR)
	$(eval BEAMER_INPUT := $(shell test -f $(DOC_ZH_FILE) && echo $(DOC_ZH_FILE) || echo $(DOC_FILE)))
	python3 gen_presentation.py beamer --input $(BEAMER_INPUT) --output $(BEAMER_FILE) \
		--title "$(TITLE)" --url "$(URL)"
	@cp $(PUB_TEMPLATE) $(PUB_MAKEFILE) 2>/dev/null || true
	@echo "  ✓ Presentation: $@ ($$(wc -c < "$@") bytes)"

# ── Step 8: Compile PDF ─────────────────────────────────────────────────────
pdf: $(DOC_PDF)

$(DOC_PDF): $(DOC_FILE) $(PUBLISH_DIR)/images/.done
	@echo "[8/8] Compiling PDF (mode: $(RESOLVED_MODE))..."
	@cd $(PUBLISH_DIR) && $(MAKE) --no-print-directory
	@echo "  ✓ PDF: $@ ($$(du -h "$@" | cut -f1))"

# ── Clean targets ────────────────────────────────────────────────────────────
clean:
	@echo "Cleaning auxiliary files..."
	@if [ -f publish_tex/Makefile ]; then cd publish_tex && $(MAKE) --no-print-directory clean; fi
	@if [ -f publish_md/Makefile ]; then cd publish_md && $(MAKE) --no-print-directory clean; fi

distclean: clean
	@echo "Removing all generated files..."
	rm -f *.mp4 $(AUDIO)
	rm -rf $(PARTS_DIR) $(SLIDES_DIR) $(KEY_SLIDES_DIR)
	rm -f whisper_part*.txt $(TRANSCRIPT)
	rm -rf publish_tex publish_md
	rm -rf __pycache__

# ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo "Bilibili / YouTube Video → PDF Transcript Pipeline"
	@echo ""
	@echo "Current mode: $(RESOLVED_MODE) (PUBLISH_MODE=$(PUBLISH_MODE))"
	@echo "Output dir:   $(PUBLISH_DIR)/"
	@echo ""
	@echo "Usage:"
	@echo "  1. Edit config.env (fill in URL, TITLE, PUBLISH_MODE, TRANSLATE_ZH)"
	@echo "  2. make all"
	@echo ""
	@echo "Or override on command line:"
	@echo "  make URL=\"...\" all                # auto-detect mode"
	@echo "  make URL=\"...\" PUBLISH_MODE=md all # force Markdown mode"
	@echo "  make URL=\"...\" PUBLISH_MODE=tex all # force LaTeX mode"
	@echo ""
	@echo "Targets:"
	@echo "  all            Full pipeline (auto-detect tex/md mode)"
	@echo "  all-tex        Full pipeline, force LaTeX mode → publish_tex/"
	@echo "  all-md         Full pipeline, force Markdown mode → publish_md/"
	@echo "  download       Step 1: Download video"
	@echo "  audio          Step 2: Extract audio from video"
	@echo "  segment        Step 3: Segment audio into chunks"
	@echo "  transcribe     Step 4: Transcribe all segments with whisper"
	@echo "  transcript     Steps 1-4: Download + full transcript"
	@echo "  extract-frames Step 5a: Extract video frames"
	@echo "  dedup          Step 5b: Deduplicate frames"
	@echo "  slides         Steps 1,5: Download + extract + dedup frames"
	@echo "  tex            Step 6: Generate LaTeX (tex mode only)"
	@echo "  markdown       Step 6: Generate Markdown (md mode only)"
	@echo "  translate      Step 7a: Translate English summary to Chinese"
	@echo "  beamer         Step 7b: Generate presentation (Beamer/PPTX)"
	@echo "  presentation   Steps 1-7b: Full pipeline + presentation"
	@echo "  pdf            Step 8: Compile PDF (runs all prerequisites)"
	@echo "  clean          Remove auxiliary files"
	@echo "  distclean      Remove ALL generated files"
	@echo "  info           Show current configuration"
	@echo "  help           Show this help"
	@echo ""
	@echo "Variables (override on command line):"
	@echo "  URL            Video URL (required)"
	@echo "  TITLE          PDF title (default: Video Transcript)"
	@echo "  PUBLISH_MODE   tex | md | auto (default: auto, detect xelatex)"
	@echo "  TRANSLATE_ZH   yes | no | auto (default: auto, LLM decides)"
	@echo "  WHISPER_LANG   Whisper language: en|zh|auto (default: en)"
	@echo "  SEGMENT_SEC    Audio segment length in seconds (default: 600)"
	@echo "  FRAME_INTERVAL Frame extraction interval in seconds (default: 30)"
	@echo "  DEDUP_THRESH   dhash dedup threshold (default: 20)"
	@echo "  VIDEO_FORMAT   yt-dlp format string (default: 720p)"
	@echo ""
	@echo "Publish modes:"
	@echo "  tex  → publish_tex/  (LaTeX/xelatex, best quality, requires mactex)"
	@echo "  md   → publish_md/   (Markdown + Python, no LaTeX needed)"
	@echo ""
	@echo "Config file:"
	@echo "  config.env                  # primary configuration (auto-loaded)"

info:
	@echo "Configuration (from config.env + command line):"
	@echo "  URL:            $(URL)"
	@echo "  VIDEO_ID:       $(VIDEO_ID) (BV_ID=$(BV_ID), YT_ID=$(YT_ID))"
	@echo "  TITLE:          $(TITLE)"
	@echo "  PUBLISH_MODE:   $(PUBLISH_MODE) → resolved: $(RESOLVED_MODE)"
	@echo "  TRANSLATE_ZH:   $(TRANSLATE_ZH) → resolved: $(RESOLVED_TRANSLATE)"
	@echo "  PUBLISH_DIR:    $(PUBLISH_DIR)"
	@echo "  WHISPER_LANG:   $(WHISPER_LANG)"
	@echo "  SEGMENT_SEC:    $(SEGMENT_SEC)"
	@echo "  FRAME_INTERVAL: $(FRAME_INTERVAL)"
	@echo "  DEDUP_THRESH:   $(DEDUP_THRESH)"
	@echo "  WHISPER_MODEL:  $(WHISPER_MODEL)"
	@echo "  VIDEO_FORMAT:   $(VIDEO_FORMAT)"
