#!/usr/bin/env python3
"""Merge whisper transcript parts into a single full transcript file.

Reads whisper_part_XX.txt files and combines them with time markers.
Replaces the complex shell logic that was previously in the Makefile.

Usage:
    python3 merge_transcript.py --parts-dir audio_parts --segment-sec 600 --output full_whisper_transcript.txt
"""

import argparse
import os
import re
from pathlib import Path


def merge_transcripts(parts_dir, segment_sec, output_path):
    """Merge individual whisper transcript files into one full transcript.

    Args:
        parts_dir: Directory containing part_XX.mp3 files (used to enumerate parts)
        segment_sec: Duration of each audio segment in seconds
        output_path: Path to write the merged transcript
    """
    parts = sorted(Path(parts_dir).glob("part_*.mp3"))
    if not parts:
        print(f"WARNING: No part_*.mp3 files found in {parts_dir}")
        return

    total = len(parts)
    print(f"Merging {total} transcript parts (segment={segment_sec}s)...")

    lines = []
    for idx, part_path in enumerate(parts):
        name = part_path.stem  # e.g. "part_00"
        transcript_file = f"whisper_{name}.txt"

        offset_min = idx * segment_sec // 60
        end_min = (idx + 1) * segment_sec // 60

        lines.append("")
        lines.append(f"--- [{offset_min:02d}:00 - {end_min:02d}:00] Part {idx + 1} of {total} ---")
        lines.append("")

        if os.path.isfile(transcript_file):
            with open(transcript_file, "r", encoding="utf-8") as f:
                content = f.read().rstrip("\n")
            lines.append(content)
        else:
            lines.append(f"[WARNING] Missing transcript for {name}")
            print(f"  WARNING: {transcript_file} not found")

    text = "\n".join(lines) + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"  ✓ Transcript: {output_path} ({len(text)} bytes)")


def main():
    parser = argparse.ArgumentParser(
        description="Merge whisper transcript parts into a single file."
    )
    parser.add_argument(
        "--parts-dir", "-p", required=True,
        help="Directory containing part_XX.mp3 files"
    )
    parser.add_argument(
        "--segment-sec", "-s", type=int, default=600,
        help="Duration of each audio segment in seconds (default: 600)"
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="Output file path for the merged transcript"
    )
    args = parser.parse_args()

    merge_transcripts(args.parts_dir, args.segment_sec, args.output)


if __name__ == "__main__":
    main()
