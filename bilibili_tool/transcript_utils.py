#!/usr/bin/env python3
"""Shared utilities for transcript processing.

Extracted from gen_transcript_tex.py and gen_transcript_md.py to avoid
code duplication. Both generators import from this module.

Functions:
    build_slide_timestamps  — Map slide filenames to video timestamps
    read_transcript         — Parse whisper transcript into (timestamp, text) pairs
"""

import os
import re


def build_slide_timestamps(base_dir, duration):
    """Build mapping: slide filename -> timestamp in seconds.

    Args:
        base_dir: Project base directory containing key_slides/
        duration: Video duration in seconds (required, passed from Makefile)

    Returns:
        tuple: (slides_list, timestamps_dict)
            slides_list: sorted list of slide filenames
            timestamps_dict: {filename: timestamp_seconds}
    """
    slides_dir = os.path.join(base_dir, "key_slides")

    slides = sorted(os.listdir(slides_dir))
    slides = [s for s in slides if s.startswith("slide_") and s.endswith(".jpg")]

    timestamps = {}

    if not slides:
        print("No slides found!")
        return slides, timestamps

    n = len(slides)
    for i, s in enumerate(slides):
        ts = int(i * duration / n)
        timestamps[s] = ts

    print(f"Slides: {n}, Video duration: {duration}s")
    return slides, timestamps


def read_transcript(base_dir, segment_sec=600):
    """Read the full whisper transcript and split into paragraphs with timestamps.

    Args:
        base_dir: Project base directory containing full_whisper_transcript.txt
        segment_sec: Duration of each audio segment in seconds (must match Makefile SEGMENT_SEC)

    Returns:
        list of (start_seconds, text) tuples
    """
    transcript_path = os.path.join(base_dir, "full_whisper_transcript.txt")
    with open(transcript_path, "r") as f:
        text = f.read()

    # Split by part markers: --- [MM:SS - MM:SS] Part N of M ---
    parts = re.split(r'\n--- \[(\d+:\d+) - (\d+:\d+)\] Part (\d+) of (\d+) ---\n', text)

    paragraphs = []  # list of (start_seconds, text)
    segment_duration = segment_sec

    i = 1
    while i < len(parts):
        if i + 4 >= len(parts) + 1:
            break
        start_str = parts[i]
        end_str = parts[i + 1]
        part_num = int(parts[i + 2])
        total_parts = int(parts[i + 3])
        content = parts[i + 4] if i + 4 < len(parts) else ""
        i += 5

        # Parse start time
        m, s = start_str.split(":")
        part_start_sec = int(m) * 60 + int(s)

        # Split content into paragraphs (groups of ~5 lines)
        lines = content.strip().split("\n")
        group_size = 5
        for j in range(0, len(lines), group_size):
            group = lines[j:j + group_size]
            frac = j / max(len(lines), 1)
            ts = part_start_sec + int(frac * segment_duration)
            para_text = " ".join(line.strip() for line in group if line.strip())
            if para_text:
                paragraphs.append((ts, para_text))

    return paragraphs
