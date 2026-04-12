#!/usr/bin/env python3
"""Generate presentation slides from transcript.

This is a transitional script — in the future, the LLM Skill will
directly generate slides.md (content layer) and this script will
only handle the rendering.

Currently provides two subcommands:
  translate  — Placeholder for LLM translation (copies with note)
  beamer     — Extract key content from transcript to slides.md

The "beamer" subcommand generates a structured Markdown file that
md2pptx.py can convert to PPTX. It extracts section headings,
key bullet points, and image references from the transcript.

Usage:
    python3 gen_presentation.py translate --input publish_md/transcript.md --output publish_md/transcript_zh.md
    python3 gen_presentation.py beamer --input publish_md/transcript_zh.md --output publish_md/slides.md \
        --title "Title" --url "URL"

Note:
    In production, both translate and beamer steps will be performed
    by the LLM directly, producing much higher quality output.
    This script serves as a fallback / testing scaffold.
"""

import argparse
import os
import re
import sys


def cmd_translate(args):
    """Placeholder translation: copy input to output with a note.

    In production, the LLM will perform high-quality translation.
    This placeholder simply copies the file so the pipeline can proceed.

    Supports both Markdown (.md) and LaTeX (.tex) input files.
    """
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    # Detect file type and add appropriate placeholder header
    is_tex = args.input.endswith(".tex") or args.output.endswith(".tex")
    if is_tex:
        header = (
            "% NOTE: This is a placeholder copy.\n"
            "% In production, the LLM Skill will translate this to Chinese.\n\n"
        )
    else:
        header = (
            "<!-- NOTE: This is a placeholder copy. "
            "In production, the LLM Skill will translate this to Chinese. -->\n\n"
        )

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(header + content)

    print(f"Placeholder translation: {args.input} → {args.output}")
    print(f"Size: {os.path.getsize(args.output)} bytes")
    print("NOTE: Replace with LLM translation for production quality.")


def cmd_beamer(args):
    """Generate slides.md from transcript for md2pptx.py to render.

    Extracts structure from the transcript Markdown:
    - Section headings become slide titles
    - First paragraph of each section becomes bullet points
    - Image references are preserved
    - Aims for ~15-30 slides (one per section)
    """
    if not os.path.exists(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()

    title = getattr(args, "title", "Presentation")
    url = getattr(args, "url", "")

    slides_md = generate_slides_from_transcript(content, title, url)

    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(slides_md)

    print(f"Slides written to {args.output}")
    print(f"Size: {os.path.getsize(args.output)} bytes")


def generate_slides_from_transcript(content, title, url):
    """Extract key content from transcript to create slides.

    Supports both Markdown and LaTeX input formats.

    Strategy:
    1. Parse sections (## headings or \\section{} commands) from the transcript
    2. For each section, extract:
       - The heading as slide title
       - First 3-5 sentences as bullet points
       - First image reference
    3. Create a title slide and section slides
    """
    lines = content.splitlines()
    sections = []
    current_section = None

    for line in lines:
        # Match Markdown ## headings or LaTeX \section{...}
        md_match = re.match(r'^## (.+)', line)
        tex_match = re.match(r'\\section\{(.+?)\}', line)

        if md_match or tex_match:
            if current_section:
                sections.append(current_section)
            heading = md_match.group(1).strip() if md_match else tex_match.group(1).strip()
            current_section = {
                "title": heading,
                "text_lines": [],
                "images": [],
            }
            continue

        if current_section is not None:
            # Collect images (Markdown format)
            img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
            # Also match LaTeX \keyslide{image}{caption} or \includegraphics{image}
            tex_img_match = re.match(r'\\keyslide\{([^}]+)\}\{([^}]*)\}', line.strip())
            tex_incl_match = re.match(r'.*\\includegraphics.*\{([^}]+)\}', line.strip())

            if img_match:
                current_section["images"].append({
                    "caption": img_match.group(1),
                    "path": img_match.group(2),
                })
                continue
            elif tex_img_match:
                current_section["images"].append({
                    "caption": tex_img_match.group(2),
                    "path": "images/" + tex_img_match.group(1),
                })
                continue
            elif tex_incl_match:
                current_section["images"].append({
                    "caption": "",
                    "path": "images/" + tex_incl_match.group(1),
                })
                continue

            # Collect text (skip empty lines, metadata, sub-headings)
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("*Slide"):
                # Remove timestamp markers like [00:05:30]
                cleaned = re.sub(r'\[[\d:]+\]\s*', '', stripped)
                if cleaned and len(cleaned) > 10:
                    current_section["text_lines"].append(cleaned)

    if current_section:
        sections.append(current_section)

    # Build slides Markdown
    out = []

    # Title slide
    out.append(f"# {title}")
    if url:
        out.append(f"- Source: {url}")
    out.append("")

    # Section slides
    for sec in sections:
        out.append(f"## {sec['title']}")
        out.append("")

        # Extract key sentences as bullet points (max 5)
        bullets = extract_key_bullets(sec["text_lines"], max_bullets=5)
        for bullet in bullets:
            out.append(f"- {bullet}")

        # Add first image if available
        if sec["images"]:
            img = sec["images"][0]
            out.append("")
            out.append(f"![{img['caption']}]({img['path']})")

        out.append("")
        out.append("---")
        out.append("")

    return "\n".join(out)


def extract_key_bullets(text_lines, max_bullets=5):
    """Extract key bullet points from text lines.

    Simple heuristic: take the first N non-trivial sentences.
    In production, the LLM will do intelligent summarization.
    """
    bullets = []
    for line in text_lines:
        # Clean up the line
        line = line.strip()
        if not line:
            continue

        # Skip very short lines
        if len(line) < 15:
            continue

        # Truncate very long lines
        if len(line) > 120:
            # Find a good break point
            break_at = line[:120].rfind(". ")
            if break_at > 60:
                line = line[:break_at + 1]
            else:
                line = line[:117] + "..."

        bullets.append(line)
        if len(bullets) >= max_bullets:
            break

    return bullets


def main():
    parser = argparse.ArgumentParser(
        description="Generate presentation slides from transcript."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-command")

    # translate subcommand
    p_translate = subparsers.add_parser(
        "translate",
        help="Translate transcript (placeholder — LLM will replace this)"
    )
    p_translate.add_argument("--input", "-i", required=True, help="Input file")
    p_translate.add_argument("--output", "-o", required=True, help="Output file")

    # beamer subcommand
    p_beamer = subparsers.add_parser(
        "beamer",
        help="Generate slides Markdown from transcript"
    )
    p_beamer.add_argument("--input", "-i", required=True, help="Input transcript file")
    p_beamer.add_argument("--output", "-o", required=True, help="Output slides file")
    p_beamer.add_argument("--title", default="Presentation", help="Presentation title")
    p_beamer.add_argument("--url", default="", help="Source video URL")

    args = parser.parse_args()

    if args.command == "translate":
        cmd_translate(args)
    elif args.command == "beamer":
        cmd_beamer(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
