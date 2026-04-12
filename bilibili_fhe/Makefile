# ============================================================================
# Makefile — Bilibili Video → PDF Transcript Pipeline
#
# Usage:
#   make URL="https://www.bilibili.com/video/BV1rY411V7Ko/" all
#   make pdf                  # only recompile PDF (after editing .tex)
#   make transcript           # only run steps 1-4 (download + transcribe)
#   make slides               # only run steps 1,5 (download + extract frames)
#   make clean                # remove LaTeX auxiliary files
#   make distclean            # remove everything (video, audio, slides, PDF)
#
# The pipeline is idempotent — each target checks if output exists and skips.
# To force re-run a step, delete its output first (e.g. rm full_whisper_transcript.txt)
# ============================================================================

# ── User-configurable variables ──────────────────────────────────────────────
# Override on command line:  make URL="..." TITLE="..." WHISPER_LANG=zh all

URL            ?=
TITLE          ?= Video Transcript
WHISPER_LANG   ?= en
SEGMENT_SEC    ?= 600
FRAME_INTERVAL ?= 30
DEDUP_THRESH   ?= 20
VIDEO_FORMAT   ?= bestvideo[height<=720]+bestaudio/best[height<=720]

# ── Derived variables ────────────────────────────────────────────────────────
BV_ID          := $(shell echo "$(URL)" | grep -oE 'BV[a-zA-Z0-9]+' | head -1)
VIDEO          := $(BV_ID).mp4
AUDIO          := audio.mp3
PARTS_DIR      := audio_parts
SLIDES_DIR     := slides
KEY_SLIDES_DIR := key_slides
PDF_DIR        := pdf
TRANSCRIPT     := full_whisper_transcript.txt
TEX_FILE       := $(PDF_DIR)/fhe_full_transcript.tex
PDF_FILE       := $(PDF_DIR)/fhe_full_transcript.pdf

# Whisper model (auto-detect: prefer large-v3-turbo, fallback to base)
WHISPER_MODELS := $(HOME)/.summarize/cache/whisper-cpp/models
WHISPER_MODEL  := $(shell \
	if [ -f "$(WHISPER_MODELS)/ggml-large-v3-turbo.bin" ]; then \
		echo "$(WHISPER_MODELS)/ggml-large-v3-turbo.bin"; \
	elif [ -f "$(WHISPER_MODELS)/ggml-base.bin" ]; then \
		echo "$(WHISPER_MODELS)/ggml-base.bin"; \
	fi)

# ── Phony targets ───────────────────────────────────────────────────────────
.PHONY: all pdf transcript slides dedup tex download audio segment \
        transcribe merge-transcript extract-frames copy-images \
        check-url check-deps info clean distclean help

# ── Default target ───────────────────────────────────────────────────────────
all: check-url check-deps pdf
	@echo ""
	@echo "============================================"
	@echo "  ✅ Pipeline complete!"
	@echo "============================================"
	@echo "  Video:       $(VIDEO)"
	@echo "  Transcript:  $(TRANSCRIPT)"
	@echo "  Key slides:  $(KEY_SLIDES_DIR)/"
	@echo "  PDF:         $(PDF_FILE)"
	@echo ""

# ── Convenience aliases ──────────────────────────────────────────────────────
transcript: check-url check-deps merge-transcript
slides:     check-url check-deps dedup

# ── Validation ───────────────────────────────────────────────────────────────
check-url:
ifeq ($(BV_ID),)
	$(error URL is required. Usage: make URL="https://www.bilibili.com/video/BVxxxxxxxx/" all)
endif

check-deps:
	@command -v yt-dlp      >/dev/null 2>&1 || { echo "ERROR: yt-dlp not found.      Install: brew install yt-dlp"; exit 1; }
	@command -v ffmpeg      >/dev/null 2>&1 || { echo "ERROR: ffmpeg not found.      Install: brew install ffmpeg"; exit 1; }
	@command -v ffprobe     >/dev/null 2>&1 || { echo "ERROR: ffprobe not found.     Install: brew install ffmpeg"; exit 1; }
	@command -v whisper-cli >/dev/null 2>&1 || { echo "ERROR: whisper-cli not found. Install: brew install whisper-cpp"; exit 1; }
	@command -v python3     >/dev/null 2>&1 || { echo "ERROR: python3 not found.     Install: brew install python3"; exit 1; }
	@command -v xelatex     >/dev/null 2>&1 || { echo "ERROR: xelatex not found.     Install: brew install --cask mactex"; exit 1; }
	@test -n "$(WHISPER_MODEL)" || { echo "ERROR: No whisper model found in $(WHISPER_MODELS)"; exit 1; }

# ── Step 1: Download video ──────────────────────────────────────────────────
download: $(VIDEO)

$(VIDEO):
	@echo "[1/7] Downloading video $(BV_ID)..."
	yt-dlp -f "$(VIDEO_FORMAT)" -o "$@" --merge-output-format mp4 "$(URL)"
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
# Transcribe each part individually, then merge
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
	@idx=0; \
	total=$$(ls $(PARTS_DIR)/part_*.mp3 | wc -l | tr -d ' '); \
	> $@; \
	for part in $(PARTS_DIR)/part_*.mp3; do \
		name=$$(basename "$$part" .mp3); \
		offset_min=$$((idx * $(SEGMENT_SEC) / 60)); \
		end_min=$$(( (idx + 1) * $(SEGMENT_SEC) / 60 )); \
		echo "" >> $@; \
		printf -- "--- [%02d:00 - %02d:00] Part %d of %d ---\n" $$offset_min $$end_min $$((idx + 1)) $$total >> $@; \
		echo "" >> $@; \
		if [ -f "whisper_$${name}.txt" ]; then \
			cat "whisper_$${name}.txt" >> $@; \
		else \
			echo "[WARNING] Missing transcript for $$name" >> $@; \
		fi; \
		idx=$$((idx + 1)); \
	done
	@echo "  ✓ Transcript: $@ ($$(wc -c < "$@") bytes)"

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
	python3 dedup_slides.py --input $(SLIDES_DIR) --output $(KEY_SLIDES_DIR) --threshold $(DEDUP_THRESH)
	@touch $@

copy-images: $(PDF_DIR)/images/.done

$(PDF_DIR)/images/.done: $(KEY_SLIDES_DIR)/.done
	@echo "  Copying key slides to pdf/images/..."
	@mkdir -p $(PDF_DIR)/images
	@cp $(KEY_SLIDES_DIR)/slide_*.jpg $(PDF_DIR)/images/ 2>/dev/null || true
	@touch $@

# ── Step 6: Generate LaTeX ──────────────────────────────────────────────────
tex: $(TEX_FILE)

$(TEX_FILE): $(TRANSCRIPT) $(KEY_SLIDES_DIR)/.done
	@echo "[6/7] Generating LaTeX document..."
	python3 gen_full_transcript_tex.py --base . --title "$(TITLE)" --url "$(URL)"
	@echo "  ✓ LaTeX: $@ ($$(wc -c < "$@") bytes)"

# ── Step 7: Compile PDF ─────────────────────────────────────────────────────
pdf: $(PDF_FILE)

$(PDF_FILE): $(TEX_FILE) $(PDF_DIR)/images/.done
	@echo "[7/7] Compiling PDF with xelatex..."
	@cd $(PDF_DIR) && \
		xelatex -interaction=nonstopmode -halt-on-error $$(basename $(TEX_FILE)) >/dev/null 2>&1 && \
		xelatex -interaction=nonstopmode -halt-on-error $$(basename $(TEX_FILE)) >/dev/null 2>&1 && \
		rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz *.nav *.snm *.vrb
	@echo "  ✓ PDF: $@ ($$(du -h "$@" | cut -f1))"

# ── Clean targets ────────────────────────────────────────────────────────────
clean:
	@echo "Cleaning LaTeX auxiliary files..."
	rm -f $(PDF_DIR)/*.aux $(PDF_DIR)/*.log $(PDF_DIR)/*.out $(PDF_DIR)/*.toc
	rm -f $(PDF_DIR)/*.fls $(PDF_DIR)/*.fdb_latexmk $(PDF_DIR)/*.synctex.gz
	rm -f $(PDF_DIR)/*.nav $(PDF_DIR)/*.snm $(PDF_DIR)/*.vrb

distclean: clean
	@echo "Removing all generated files..."
	rm -f $(VIDEO) $(AUDIO)
	rm -rf $(PARTS_DIR) $(SLIDES_DIR) $(KEY_SLIDES_DIR)
	rm -f whisper_part*.txt $(TRANSCRIPT)
	rm -f $(PDF_FILE) $(TEX_FILE)
	rm -rf $(PDF_DIR)/images

# ── Help ─────────────────────────────────────────────────────────────────────
help:
	@echo "Bilibili Video → PDF Transcript Pipeline"
	@echo ""
	@echo "Usage:"
	@echo "  make URL=\"https://www.bilibili.com/video/BVxxxxxxxx/\" all"
	@echo ""
	@echo "Targets:"
	@echo "  all          Full pipeline: download → transcribe → slides → PDF"
	@echo "  download     Step 1: Download video from Bilibili"
	@echo "  audio        Step 2: Extract audio from video"
	@echo "  segment      Step 3: Segment audio into 10-min chunks"
	@echo "  transcribe   Step 4: Transcribe all segments with whisper"
	@echo "  transcript   Steps 1-4: Download + full transcript"
	@echo "  extract-frames  Step 5a: Extract video frames"
	@echo "  dedup        Step 5b: Deduplicate frames"
	@echo "  slides       Steps 1,5: Download + extract + dedup frames"
	@echo "  tex          Step 6: Generate LaTeX from transcript + slides"
	@echo "  pdf          Step 7: Compile PDF (runs all prerequisites)"
	@echo "  clean        Remove LaTeX auxiliary files"
	@echo "  distclean    Remove ALL generated files"
	@echo "  info         Show current configuration"
	@echo "  help         Show this help"
	@echo ""
	@echo "Variables (override on command line):"
	@echo "  URL            Bilibili video URL (required)"
	@echo "  TITLE          PDF title (default: Video Transcript)"
	@echo "  WHISPER_LANG   Whisper language: en|zh|auto (default: en)"
	@echo "  SEGMENT_SEC    Audio segment length in seconds (default: 600)"
	@echo "  FRAME_INTERVAL Frame extraction interval in seconds (default: 30)"
	@echo "  DEDUP_THRESH   dhash dedup threshold (default: 20)"
	@echo "  VIDEO_FORMAT   yt-dlp format string (default: 720p)"
	@echo ""
	@echo "Examples:"
	@echo "  make URL=\"https://www.bilibili.com/video/BV1rY411V7Ko/\" all"
	@echo "  make URL=\"...\" WHISPER_LANG=zh TITLE=\"我的视频\" all"
	@echo "  make pdf                    # recompile PDF only"
	@echo "  make transcript             # download + transcribe only"

info:
	@echo "Configuration:"
	@echo "  URL:            $(URL)"
	@echo "  BV_ID:          $(BV_ID)"
	@echo "  TITLE:          $(TITLE)"
	@echo "  WHISPER_LANG:   $(WHISPER_LANG)"
	@echo "  SEGMENT_SEC:    $(SEGMENT_SEC)"
	@echo "  FRAME_INTERVAL: $(FRAME_INTERVAL)"
	@echo "  DEDUP_THRESH:   $(DEDUP_THRESH)"
	@echo "  WHISPER_MODEL:  $(WHISPER_MODEL)"
	@echo "  VIDEO_FORMAT:   $(VIDEO_FORMAT)"
