#!/usr/bin/env python3
"""Generate a LaTeX document from full whisper transcript + key slides.

Aligns slide images with transcript text based on timestamps.
Each slide was extracted at 30-second intervals; timestamps are
distributed proportionally across the video duration.

Usage:
    python3 gen_full_transcript_tex.py --base <project_dir> [--title "Title"] [--url "URL"]
"""

import argparse
import re
import os

SLIDE_TIMESTAMPS = {}


def build_slide_timestamps(base_dir, duration=None):
    """Build mapping: slide filename -> timestamp in seconds."""
    slides_dir = os.path.join(base_dir, "key_slides")

    slides = sorted(os.listdir(slides_dir))
    slides = [s for s in slides if s.startswith("slide_") and s.endswith(".jpg")]

    if not slides:
        print("No slides found!")
        return slides

    # Auto-detect duration from video if not provided
    if duration is None:
        video_files = [f for f in os.listdir(base_dir) if f.endswith(".mp4")]
        if video_files:
            import subprocess
            try:
                result = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1",
                     os.path.join(base_dir, video_files[0])],
                    capture_output=True, text=True
                )
                duration = int(float(result.stdout.strip()))
            except Exception:
                pass
        if duration is None:
            # Estimate from transcript parts (10 min each)
            parts = [f for f in os.listdir(os.path.join(base_dir, "audio_parts"))
                     if f.startswith("part_") and f.endswith(".mp3")]
            duration = len(parts) * 600

    n = len(slides)
    for i, s in enumerate(slides):
        ts = int(i * duration / n)
        SLIDE_TIMESTAMPS[s] = ts

    print(f"Slides: {n}, Video duration: {duration}s")
    return slides


def escape_tex(s):
    """Escape special LaTeX characters."""
    s = s.replace("\\", "\\textbackslash{}")
    s = s.replace("%", "\\%")
    s = s.replace("&", "\\&")
    s = s.replace("#", "\\#")
    s = s.replace("_", "\\_")
    s = s.replace("$", "\\$")
    s = s.replace("{", "\\{")
    s = s.replace("}", "\\}")
    s = s.replace("~", "\\textasciitilde{}")
    s = s.replace("^", "\\textasciicircum{}")
    return s


def read_transcript(base_dir):
    """Read the full whisper transcript and split into paragraphs with timestamps."""
    transcript_path = os.path.join(base_dir, "full_whisper_transcript.txt")
    with open(transcript_path, "r") as f:
        text = f.read()

    # Split by part markers: --- [MM:SS - MM:SS] Part N of M ---
    parts = re.split(r'\n--- \[(\d+:\d+) - (\d+:\d+)\] Part (\d+) of (\d+) ---\n', text)

    paragraphs = []  # list of (start_seconds, text)
    segment_duration = 600  # default 10 min per segment

    i = 1
    while i < len(parts):
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


def generate_tex(paragraphs, slides, title="Video Transcript", url=""):
    """Generate LaTeX document with transcript and slides interleaved."""
    slide_idx = 0
    tex = []

    # Determine section boundaries from paragraphs
    max_section = max(ts // 600 for ts, _ in paragraphs) if paragraphs else 0

    # Auto-generate section titles
    section_titles = []
    for sec_idx in range(max_section + 1):
        start_min = sec_idx * 10
        end_min = (sec_idx + 1) * 10
        section_titles.append(f"Part {sec_idx + 1} ({start_min:02d}:00 -- {end_min:02d}:00)")

    # Preamble
    escaped_title = title.replace("&", "\\&").replace("_", "\\_")
    url_line = ""
    if url:
        url_line = f"  {{\\small 原始视频：\\href{{{url}}}{{{url}}}\\par}}"

    tex.append(r"""% fhe_full_transcript.tex
% Full verbatim transcript - auto-generated
% Compile: xelatex fhe_full_transcript.tex

\documentclass[11pt,a4paper]{article}

\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont[BoldFont=PingFang SC Semibold]{PingFang SC}
\setCJKsansfont[BoldFont=PingFang SC Semibold]{PingFang SC}
\setCJKmonofont{PingFang SC}
\setmainfont{Palatino}
\setsansfont{Helvetica Neue}
\setmonofont{Menlo}

\usepackage[top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\graphicspath{{images/}}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{caption}
\hypersetup{
  colorlinks=true,
  linkcolor=blue!70!black,
  urlcolor=blue!70!black,
  pdfauthor={Whisper Transcription},
  pdftitle={""" + escaped_title + r"""},
}

\usepackage{parskip}
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt plus 2pt minus 1pt}

\usepackage{mdframed}
\newmdenv[
  topline=false, bottomline=false, rightline=false,
  linewidth=3pt, linecolor=blue!40,
  innerleftmargin=12pt, innerrightmargin=12pt,
  innertopmargin=8pt, innerbottommargin=8pt,
  backgroundcolor=blue!3, skipabove=10pt, skipbelow=10pt,
]{myquote}

\usepackage{titlesec}
\titleformat{\section}{\Large\bfseries\sffamily}{}{0em}{}[\vspace{-0.5em}\rule{\textwidth}{0.5pt}]
\titleformat{\subsection}{\large\bfseries\sffamily}{}{0em}{}
\setcounter{secnumdepth}{0}

\setlength{\emergencystretch}{3em}
\tolerance=1000

\newcommand{\keyslide}[2]{%
  \begin{center}
    \includegraphics[width=0.88\textwidth]{#1}
    \captionof{figure}{#2}
  \end{center}
  \vspace{6pt}
}

\newcommand{\timestamp}[1]{%
  \hfill{\scriptsize\color{gray}[#1]}%
}

\begin{document}

\begin{titlepage}
  \centering
  \vspace*{3cm}
  {\Huge\bfseries\sffamily """ + escaped_title + r"""\par}
  \vspace{1.5cm}
  {\large\bfseries Full Verbatim Transcript\par}
  \vspace{0.3cm}
  {\small Transcribed by Whisper large-v3-turbo\par}
  \vspace{0.5cm}
""" + url_line + r"""
  \vfill
  {\large \today\par}
\end{titlepage}

\newpage
\tableofcontents
\newpage
""")

    current_section = -1

    for ts, para_text in paragraphs:
        new_section = min(ts // 600, len(section_titles) - 1)

        if new_section != current_section:
            current_section = new_section
            tex.append(f"\n\\section{{{section_titles[current_section]}}}\n")

        # Insert slides whose timestamp is close to this paragraph
        while slide_idx < len(slides):
            slide_ts = SLIDE_TIMESTAMPS[slides[slide_idx]]
            if slide_ts <= ts + 15:
                slide_name = slides[slide_idx]
                slide_min = slide_ts // 60
                slide_sec = slide_ts % 60
                tex.append(f"\\keyslide{{{slide_name}}}{{Slide at {slide_min:02d}:{slide_sec:02d}}}\n")
                slide_idx += 1
            else:
                break

        t_min = ts // 60
        t_sec = ts % 60
        escaped = escape_tex(para_text)
        tex.append(f"{escaped} \\timestamp{{{t_min:02d}:{t_sec:02d}}}\n")

    # Insert remaining slides
    while slide_idx < len(slides):
        slide_name = slides[slide_idx]
        slide_ts = SLIDE_TIMESTAMPS[slides[slide_idx]]
        slide_min = slide_ts // 60
        slide_sec = slide_ts % 60
        tex.append(f"\\keyslide{{{slide_name}}}{{Slide at {slide_min:02d}:{slide_sec:02d}}}\n")
        slide_idx += 1

    tex.append("\n\\end{document}\n")
    return "\n".join(tex)


def main():
    parser = argparse.ArgumentParser(
        description="Generate LaTeX from whisper transcript + key slides."
    )
    parser.add_argument(
        "--base", "-b", required=True,
        help="Base project directory containing key_slides/ and full_whisper_transcript.txt"
    )
    parser.add_argument(
        "--title", "-T", default="Video Transcript",
        help="Document title for the PDF title page"
    )
    parser.add_argument(
        "--url", "-u", default="",
        help="Original video URL (shown on title page)"
    )
    parser.add_argument(
        "--duration", "-d", type=int, default=None,
        help="Video duration in seconds (auto-detected if omitted)"
    )
    args = parser.parse_args()

    slides = build_slide_timestamps(args.base, args.duration)
    paragraphs = read_transcript(args.base)

    print(f"Paragraphs: {len(paragraphs)}")

    tex_content = generate_tex(paragraphs, slides, args.title, args.url)

    out_path = os.path.join(args.base, "pdf", "fhe_full_transcript.tex")
    with open(out_path, "w") as f:
        f.write(tex_content)

    print(f"LaTeX written to {out_path}")
    print(f"Size: {len(tex_content)} bytes")


if __name__ == "__main__":
    main()
