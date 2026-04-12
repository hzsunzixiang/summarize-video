#!/usr/bin/env python3
"""Generate a Markdown document from full whisper transcript + key slides.

Fallback alternative to gen_transcript_tex.py when LaTeX is not installed.
Aligns slide images with transcript text based on timestamps.

Usage:
    python3 gen_transcript_md.py --base <project_dir> [--title "Title"] [--url "URL"] [--output transcript.md]
"""

import argparse
import re
import os

from transcript_utils import build_slide_timestamps as _build_slide_timestamps
from transcript_utils import read_transcript as _read_transcript

SLIDE_TIMESTAMPS = {}

def build_slide_timestamps(base_dir, duration):
    """Build mapping: slide filename -> timestamp in seconds (delegates to shared module)."""
    slides, timestamps = _build_slide_timestamps(base_dir, duration)
    SLIDE_TIMESTAMPS.update(timestamps)
    return slides


def read_transcript(base_dir, segment_sec=600):
    """Read the full whisper transcript (delegates to shared module)."""
    return _read_transcript(base_dir, segment_sec)


def generate_md(paragraphs, slides, title="Video Transcript", url="", segment_sec=600):
    """Generate Markdown document with transcript and slides interleaved."""
    slide_idx = 0
    md = []

    # Determine section boundaries from paragraphs
    max_section = max(ts // segment_sec for ts, _ in paragraphs) if paragraphs else 0

    # Auto-generate section titles
    section_min = segment_sec // 60
    section_titles = []
    for sec_idx in range(max_section + 1):
        start_min = sec_idx * section_min
        end_min = (sec_idx + 1) * section_min
        section_titles.append(f"Part {sec_idx + 1} ({start_min:02d}:00 – {end_min:02d}:00)")

    # Title page
    md.append(f"# {title}\n")
    md.append(f"**Full Verbatim Transcript**\n")
    md.append(f"Transcribed by Whisper large-v3-turbo\n")
    if url:
        md.append(f"Original video: [{url}]({url})\n")
    md.append("---\n")

    # Table of contents
    md.append("## Table of Contents\n")
    for i, st in enumerate(section_titles):
        anchor = st.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(":", "").replace("–", "")
        md.append(f"- [{st}](#{anchor})")
    md.append("\n---\n")

    current_section = -1

    for ts, para_text in paragraphs:
        new_section = min(ts // segment_sec, len(section_titles) - 1)

        if new_section != current_section:
            current_section = new_section
            md.append(f"\n## {section_titles[current_section]}\n")

        # Insert slides whose timestamp is close to this paragraph
        while slide_idx < len(slides):
            slide_ts = SLIDE_TIMESTAMPS[slides[slide_idx]]
            if slide_ts <= ts + 15:
                slide_name = slides[slide_idx]
                slide_min = slide_ts // 60
                slide_sec = slide_ts % 60
                md.append(f"\n![Slide at {slide_min:02d}:{slide_sec:02d}](images/{slide_name})\n")
                md.append(f"*Slide at {slide_min:02d}:{slide_sec:02d}*\n")
                slide_idx += 1
            else:
                break

        t_min = ts // 60
        t_sec = ts % 60
        md.append(f"{para_text} <sub>[{t_min:02d}:{t_sec:02d}]</sub>\n")

    # Insert remaining slides
    while slide_idx < len(slides):
        slide_name = slides[slide_idx]
        slide_ts = SLIDE_TIMESTAMPS[slides[slide_idx]]
        slide_min = slide_ts // 60
        slide_sec = slide_ts % 60
        md.append(f"\n![Slide at {slide_min:02d}:{slide_sec:02d}](images/{slide_name})\n")
        md.append(f"*Slide at {slide_min:02d}:{slide_sec:02d}*\n")
        slide_idx += 1

    md.append("\n---\n")
    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Markdown from whisper transcript + key slides."
    )
    parser.add_argument(
        "--base", "-b", required=True,
        help="Base project directory containing key_slides/ and full_whisper_transcript.txt"
    )
    parser.add_argument(
        "--title", "-T", default="Video Transcript",
        help="Document title"
    )
    parser.add_argument(
        "--url", "-u", default="",
        help="Original video URL"
    )
    parser.add_argument(
        "--duration", "-d", type=int, required=True,
        help="Video duration in seconds (passed from Makefile via ffprobe)"
    )
    parser.add_argument(
        "--segment-sec", "-s", type=int, default=600,
        help="Audio segment duration in seconds (default: 600)"
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output .md file path (default: <base>/publish_md/transcript.md)"
    )
    args = parser.parse_args()

    slides = build_slide_timestamps(args.base, args.duration)
    paragraphs = read_transcript(args.base, args.segment_sec)

    print(f"Paragraphs: {len(paragraphs)}")

    md_content = generate_md(paragraphs, slides, args.title, args.url, args.segment_sec)

    out_path = args.output or os.path.join(args.base, "publish_md", "transcript.md")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        f.write(md_content)

    print(f"Markdown written to {out_path}")
    print(f"Size: {len(md_content)} bytes")


if __name__ == "__main__":
    main()
