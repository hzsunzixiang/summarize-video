#!/usr/bin/env bash
# ============================================================================
# bilibili_video_to_pdf.sh
# One-click pipeline: Bilibili video → Full verbatim transcript PDF
#
# Usage:
#   ./bilibili_video_to_pdf.sh <BILIBILI_URL> [OUTPUT_DIR]
#
# Examples:
#   ./bilibili_video_to_pdf.sh "https://www.bilibili.com/video/BV1rY411V7Ko/"
#   ./bilibili_video_to_pdf.sh "https://www.bilibili.com/video/BV1rY411V7Ko/" ./my_output
#
# Prerequisites:
#   - yt-dlp        (brew install yt-dlp)
#   - ffmpeg        (brew install ffmpeg)
#   - whisper-cli   (brew install whisper-cpp)
#   - python3 + PIL (pip install Pillow)
#   - xelatex       (brew install --cask mactex  OR  install BasicTeX)
#
# Whisper model:
#   The script uses ggml-large-v3-turbo by default for best quality.
#   If not found, it falls back to ggml-base.
#   To download large-v3-turbo, run:
#     summarize some_short_audio.mp3  (it auto-downloads on first use)
#   Or manually download from:
#     https://huggingface.co/ggerganov/whisper.cpp/tree/main
# ============================================================================

set -euo pipefail

# ── Color output helpers ─────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ── Parse arguments ──────────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <BILIBILI_URL> [OUTPUT_DIR]"
    echo ""
    echo "  BILIBILI_URL   Full Bilibili video URL (e.g. https://www.bilibili.com/video/BVxxxxxxxx/)"
    echo "  OUTPUT_DIR     Output directory (default: current directory)"
    exit 1
fi

BILIBILI_URL="$1"
OUTPUT_DIR="${2:-.}"

# Extract BV ID from URL
BV_ID=$(echo "$BILIBILI_URL" | grep -oE 'BV[a-zA-Z0-9]+' | head -1)
if [[ -z "$BV_ID" ]]; then
    err "Cannot extract BV ID from URL: $BILIBILI_URL"
    exit 1
fi

info "BV ID: $BV_ID"
info "Output directory: $OUTPUT_DIR"

# ── Configuration ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SEGMENT_DURATION=600        # 10 minutes per audio segment
FRAME_INTERVAL=30           # Extract one frame every 30 seconds
DEDUP_THRESHOLD=20          # dhash hamming distance threshold for dedup
WHISPER_LANG="en"           # Language for whisper (use "auto" for auto-detect)
WHISPER_MODEL=""            # Will be auto-detected below

# Locate whisper model
WHISPER_MODELS_DIR="$HOME/.summarize/cache/whisper-cpp/models"
if [[ -f "$WHISPER_MODELS_DIR/ggml-large-v3-turbo.bin" ]]; then
    WHISPER_MODEL="$WHISPER_MODELS_DIR/ggml-large-v3-turbo.bin"
    info "Using whisper model: large-v3-turbo"
elif [[ -f "$WHISPER_MODELS_DIR/ggml-base.bin" ]]; then
    WHISPER_MODEL="$WHISPER_MODELS_DIR/ggml-base.bin"
    warn "large-v3-turbo not found, falling back to base model"
else
    err "No whisper model found in $WHISPER_MODELS_DIR"
    err "Install via: brew install whisper-cpp, then run 'summarize' once to download models"
    exit 1
fi

# ── Check prerequisites ─────────────────────────────────────────────────────
check_cmd() {
    if ! command -v "$1" &>/dev/null; then
        err "Required command not found: $1"
        err "Install with: $2"
        exit 1
    fi
}

check_cmd yt-dlp    "brew install yt-dlp"
check_cmd ffmpeg    "brew install ffmpeg"
check_cmd whisper-cli "brew install whisper-cpp"
check_cmd python3   "brew install python3"
check_cmd xelatex   "brew install --cask mactex"

# ── Create directory structure ───────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"/{slides,key_slides,audio_parts,pdf/images}

# ── Step 1: Download video ───────────────────────────────────────────────────
VIDEO_FILE="$OUTPUT_DIR/$BV_ID.mp4"
if [[ -f "$VIDEO_FILE" ]]; then
    ok "Video already downloaded: $VIDEO_FILE"
else
    info "Step 1/7: Downloading video from Bilibili..."
    yt-dlp \
        -f "bestvideo[height<=720]+bestaudio/best[height<=720]" \
        -o "$VIDEO_FILE" \
        --merge-output-format mp4 \
        "$BILIBILI_URL" 2>&1 | tail -5
    ok "Video downloaded: $VIDEO_FILE"
fi

# Get video duration
DURATION=$(ffprobe -v error -show_entries format=duration \
    -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null | cut -d. -f1)
info "Video duration: $((DURATION / 60))m $((DURATION % 60))s"

# ── Step 2: Extract audio ───────────────────────────────────────────────────
AUDIO_FILE="$OUTPUT_DIR/audio.mp3"
if [[ -f "$AUDIO_FILE" ]]; then
    ok "Audio already extracted: $AUDIO_FILE"
else
    info "Step 2/7: Extracting audio..."
    ffmpeg -i "$VIDEO_FILE" -vn -acodec libmp3lame -q:a 4 "$AUDIO_FILE" -y 2>/dev/null
    ok "Audio extracted: $AUDIO_FILE"
fi

# ── Step 3: Segment audio ───────────────────────────────────────────────────
PARTS_DIR="$OUTPUT_DIR/audio_parts"
PART_COUNT=$(ls "$PARTS_DIR"/part_*.mp3 2>/dev/null | wc -l | tr -d ' ')
if [[ "$PART_COUNT" -gt 0 ]]; then
    ok "Audio already segmented: $PART_COUNT parts"
else
    info "Step 3/7: Segmenting audio into ${SEGMENT_DURATION}s chunks..."
    ffmpeg -i "$AUDIO_FILE" \
        -f segment -segment_time "$SEGMENT_DURATION" \
        -c copy "$PARTS_DIR/part_%02d.mp3" -y 2>/dev/null
    PART_COUNT=$(ls "$PARTS_DIR"/part_*.mp3 | wc -l | tr -d ' ')
    ok "Audio segmented into $PART_COUNT parts"
fi

# ── Step 4: Transcribe with whisper ─────────────────────────────────────────
TRANSCRIPT_FILE="$OUTPUT_DIR/full_whisper_transcript.txt"
if [[ -f "$TRANSCRIPT_FILE" && -s "$TRANSCRIPT_FILE" ]]; then
    ok "Transcript already exists: $TRANSCRIPT_FILE"
else
    info "Step 4/7: Transcribing audio with whisper (model: $(basename "$WHISPER_MODEL"))..."
    
    # Transcribe each part in parallel
    PIDS=()
    for part_file in "$PARTS_DIR"/part_*.mp3; do
        part_name=$(basename "$part_file" .mp3)
        out_prefix="$OUTPUT_DIR/whisper_${part_name}"
        if [[ -f "${out_prefix}.txt" && -s "${out_prefix}.txt" ]]; then
            ok "  $part_name already transcribed"
        else
            info "  Transcribing $part_name..."
            whisper-cli \
                -m "$WHISPER_MODEL" \
                -l "$WHISPER_LANG" \
                --no-prints \
                -otxt \
                -of "$out_prefix" \
                "$part_file" 2>/dev/null &
            PIDS+=($!)
        fi
    done
    
    # Wait for all whisper processes
    if [[ ${#PIDS[@]} -gt 0 ]]; then
        info "  Waiting for ${#PIDS[@]} transcription jobs..."
        for pid in "${PIDS[@]}"; do
            wait "$pid" || warn "  A whisper process exited with error"
        done
    fi
    
    # Merge all parts into one transcript
    info "  Merging transcripts..."
    > "$TRANSCRIPT_FILE"
    part_idx=0
    for part_file in "$PARTS_DIR"/part_*.mp3; do
        part_name=$(basename "$part_file" .mp3)
        whisper_txt="$OUTPUT_DIR/whisper_${part_name}.txt"
        
        offset_min=$((part_idx * SEGMENT_DURATION / 60))
        end_min=$(( (part_idx + 1) * SEGMENT_DURATION / 60 ))
        total_parts=$(ls "$PARTS_DIR"/part_*.mp3 | wc -l | tr -d ' ')
        
        echo "" >> "$TRANSCRIPT_FILE"
        echo "--- [$(printf '%02d' $offset_min):00 - $(printf '%02d' $end_min):00] Part $((part_idx + 1)) of $total_parts ---" >> "$TRANSCRIPT_FILE"
        echo "" >> "$TRANSCRIPT_FILE"
        
        if [[ -f "$whisper_txt" ]]; then
            cat "$whisper_txt" >> "$TRANSCRIPT_FILE"
        else
            warn "  Missing transcript for $part_name"
        fi
        
        part_idx=$((part_idx + 1))
    done
    
    ok "Full transcript: $TRANSCRIPT_FILE ($(wc -c < "$TRANSCRIPT_FILE") bytes)"
fi

# ── Step 5: Extract & deduplicate key frames ────────────────────────────────
SLIDES_DIR="$OUTPUT_DIR/slides"
KEY_SLIDES_DIR="$OUTPUT_DIR/key_slides"
FRAME_COUNT=$(ls "$SLIDES_DIR"/frame_*.jpg 2>/dev/null | wc -l | tr -d ' ')

if [[ "$FRAME_COUNT" -gt 0 ]]; then
    ok "Frames already extracted: $FRAME_COUNT frames"
else
    info "Step 5/7: Extracting key frames (1 every ${FRAME_INTERVAL}s)..."
    ffmpeg -i "$VIDEO_FILE" \
        -vf "fps=1/$FRAME_INTERVAL,scale=1280:-1" \
        -q:v 2 \
        "$SLIDES_DIR/frame_%04d.jpg" -y 2>/dev/null
    FRAME_COUNT=$(ls "$SLIDES_DIR"/frame_*.jpg | wc -l | tr -d ' ')
    ok "Extracted $FRAME_COUNT frames"
fi

KEY_SLIDE_COUNT=$(ls "$KEY_SLIDES_DIR"/slide_*.jpg 2>/dev/null | wc -l | tr -d ' ')
if [[ "$KEY_SLIDE_COUNT" -gt 0 ]]; then
    ok "Key slides already deduplicated: $KEY_SLIDE_COUNT slides"
else
    info "  Deduplicating frames (threshold=$DEDUP_THRESHOLD)..."
    python3 "$SCRIPT_DIR/dedup_slides.py" \
        --input "$SLIDES_DIR" \
        --output "$KEY_SLIDES_DIR" \
        --threshold "$DEDUP_THRESHOLD"
    KEY_SLIDE_COUNT=$(ls "$KEY_SLIDES_DIR"/slide_*.jpg | wc -l | tr -d ' ')
    ok "Deduplicated to $KEY_SLIDE_COUNT key slides"
fi

# Copy key slides to pdf/images
info "  Copying key slides to pdf/images/..."
cp "$KEY_SLIDES_DIR"/slide_*.jpg "$OUTPUT_DIR/pdf/images/" 2>/dev/null || true

# ── Step 6: Generate LaTeX ──────────────────────────────────────────────────
TEX_FILE="$OUTPUT_DIR/pdf/fhe_full_transcript.tex"
if [[ -f "$TEX_FILE" ]]; then
    ok "LaTeX file already exists: $TEX_FILE"
else
    info "Step 6/7: Generating LaTeX document..."
    python3 "$SCRIPT_DIR/gen_full_transcript_tex.py" \
        --base "$OUTPUT_DIR" \
        --title "Video Transcript" \
        --url "$BILIBILI_URL"
    ok "LaTeX generated: $TEX_FILE"
fi

# ── Step 7: Compile PDF ─────────────────────────────────────────────────────
PDF_FILE="$OUTPUT_DIR/pdf/fhe_full_transcript.pdf"
info "Step 7/7: Compiling PDF with xelatex..."
(
    cd "$OUTPUT_DIR/pdf"
    xelatex -interaction=nonstopmode -halt-on-error "$(basename "$TEX_FILE")" >/dev/null 2>&1
    xelatex -interaction=nonstopmode -halt-on-error "$(basename "$TEX_FILE")" >/dev/null 2>&1
    # Clean auxiliary files
    rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz *.nav *.snm *.vrb
)
ok "PDF compiled: $PDF_FILE ($(du -h "$PDF_FILE" | cut -f1))"

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "============================================"
echo -e "${GREEN}✅ Pipeline complete!${NC}"
echo "============================================"
echo ""
echo "  Video:       $VIDEO_FILE"
echo "  Transcript:  $TRANSCRIPT_FILE"
echo "  Key slides:  $KEY_SLIDES_DIR/ ($KEY_SLIDE_COUNT slides)"
echo "  PDF:         $PDF_FILE"
echo ""
echo "  To recompile PDF:  make -C $OUTPUT_DIR/pdf full"
echo "  To clean:          make -C $OUTPUT_DIR/pdf distclean"
echo ""
