#!/usr/bin/env python3
"""
add_punctuation_rules.py
------------------------
Add Chinese punctuation to audio-transcribed .tex files using rule-based approach.

In these transcripts, spaces between Chinese text typically represent sentence boundaries.
This script adds appropriate punctuation (。？！) at these boundaries.

Usage:
    python add_punctuation_rules.py [--file FILE] [--all] [--dry-run]
"""

import re
import sys
import argparse
from pathlib import Path

# Target .tex files
TEX_FILES = [
    "p1_pdf/p1_full_transcript_with_slides.tex",
    "p2_pdf/p2_full_transcript_with_slides.tex",
    "p3_pdf/p3_full_transcript_with_slides.tex",
    "p4_pdf/p4_full_transcript_with_slides.tex",
]

# Question indicators - if a segment ends with these patterns, use ？
QUESTION_ENDINGS = [
    r'吗$', r'呢$', r'吧$', r'么$', r'嘛$',
    r'什么$', r'怎么$', r'如何$', r'多少$', r'哪里$', r'哪个$',
    r'为什么$', r'怎么样$', r'怎样$', r'几个$', r'几种$',
    r'好不好$', r'对不对$', r'是不是$', r'能不能$', r'可不可以$',
    r'有没有$', r'会不会$',
]

# Exclamation indicators
EXCLAMATION_ENDINGS = [
    r'啊$', r'哇$', r'了$(?<=太.*了$)', r'吧$(?<=好.*吧$)',
]

# Patterns that indicate a line is LaTeX command (should not be modified)
LATEX_LINE_PATTERNS = [
    r'^\s*$',
    r'^\s*%',
    r'^\s*\\',
    r'^\s*\{',
    r'^\s*\}',
    r'^\s*\[',
    r'^\s*\]',
]


def is_latex_line(line: str) -> bool:
    """Check if a line is a LaTeX command."""
    stripped = line.strip()
    if not stripped:
        return True
    for pattern in LATEX_LINE_PATTERNS:
        if re.match(pattern, stripped):
            return True
    return False


def has_chinese(text: str) -> bool:
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def is_question(segment: str) -> bool:
    """Check if a text segment is likely a question."""
    segment = segment.strip()
    for pattern in QUESTION_ENDINGS:
        if re.search(pattern, segment):
            return True
    # Check for question words in the segment
    question_words = ['什么', '怎么', '如何', '多少', '哪', '为何', '几', '谁',
                      '能不能', '可不可', '有没有', '会不会', '是不是', '好不好',
                      '对不对', '到底']
    for word in question_words:
        if word in segment and segment.strip().endswith(('呢', '吗', '吧', '么', '嘛')):
            return True
    return False


def ends_with_punctuation(text: str) -> bool:
    """Check if text already ends with Chinese punctuation."""
    text = text.rstrip()
    if not text:
        return True
    return text[-1] in '。？！，、；：""''（）【】《》…—'


def add_punctuation_to_segment(segment: str, is_line_end: bool = False) -> str:
    """Add punctuation to a text segment (between spaces)."""
    segment = segment.strip()
    if not segment:
        return segment
    if ends_with_punctuation(segment):
        return segment

    # Don't add punctuation to very short segments (likely incomplete)
    if len(segment) < 2:
        return segment

    # Check if it's a question
    if is_question(segment):
        return segment + '？'

    # For line endings, add period
    if is_line_end:
        return segment + '。'

    # For mid-line segments, add comma or period based on context
    # If the segment is relatively complete (has subject + predicate pattern), use period
    # Otherwise use comma
    if len(segment) >= 8:  # Longer segments are more likely complete sentences
        return segment + '。'
    else:
        return segment + '，'


def process_transcript_line(line: str) -> str:
    """Process a single line of transcript text to add punctuation.

    Key insight: In these audio transcripts, sentence boundaries are represented
    by spaces BETWEEN Chinese text segments. Spaces adjacent to English words
    are NOT sentence boundaries - they're just natural Chinese-English spacing.

    We only split on spaces where BOTH sides end/start with Chinese characters.
    """
    if not has_chinese(line):
        return line

    stripped = line.strip()
    leading_space = line[:len(line) - len(line.lstrip())]

    # Strategy: Only split on spaces that are between two Chinese characters.
    # A "Chinese character boundary" means:
    #   - Left side: the last non-space char before the space is Chinese
    #   - Right side: the first non-space char after the space is Chinese
    # This avoids splitting "中文 English 中文" at the wrong places.

    # Split ONLY on spaces where both neighbors are Chinese characters
    # Pattern: Chinese char, then space(s), then Chinese char
    parts = re.split(r'(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])', stripped)

    # Filter empty parts
    parts = [p for p in parts if p.strip()]

    if len(parts) <= 1:
        # No Chinese-to-Chinese space boundaries found
        result = stripped
        if result and not ends_with_punctuation(result):
            if is_question(result):
                result += '？'
            else:
                result += '。'
        return leading_space + result

    # Process each segment - add punctuation at the end of each
    result_parts = []
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        is_last = (i == len(parts) - 1)

        if ends_with_punctuation(part):
            result_parts.append(part)
        elif is_last:
            if is_question(part):
                result_parts.append(part + '？')
            else:
                result_parts.append(part + '。')
        else:
            if is_question(part):
                result_parts.append(part + '？')
            elif len(part) >= 6:
                result_parts.append(part + '。')
            else:
                result_parts.append(part + '，')

    result = ''.join(result_parts)
    return leading_space + result


def process_file(filepath: str, dry_run: bool = False) -> None:
    """Process a single .tex file."""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath}")
    print(f"{'='*60}")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    original_lines = [line.rstrip('\n') for line in lines]
    modified_lines = []
    changes = 0

    in_document = False
    for i, line in enumerate(original_lines):
        if r'\begin{document}' in line:
            in_document = True
        if r'\end{document}' in line:
            in_document = False

        if not in_document or is_latex_line(line):
            modified_lines.append(line)
            continue

        # This is a transcript text line
        new_line = process_transcript_line(line)
        if new_line != line:
            changes += 1
            if dry_run and changes <= 10:
                print(f"  Line {i+1}:")
                print(f"    OLD: {line[:100]}...")
                print(f"    NEW: {new_line[:100]}...")
        modified_lines.append(new_line)

    print(f"  Total changes: {changes}")

    if dry_run:
        print("  [DRY RUN] No changes written.")
        return

    if changes == 0:
        print("  No changes needed.")
        return

    # Create backup
    backup_path = filepath + '.bak'
    if not Path(backup_path).exists():
        print(f"  Creating backup: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(original_lines) + '\n')

    # Write modified file
    print(f"  Writing corrected file: {filepath}")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(modified_lines) + '\n')

    print(f"  Done!")


def main():
    parser = argparse.ArgumentParser(
        description='Add punctuation to audio-transcribed .tex files (rule-based)'
    )
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('--file', type=str,
                        help='Process a specific file (e.g., p1, p2, p3, p4)')
    parser.add_argument('--all', action='store_true',
                        help='Process all 4 files')
    args = parser.parse_args()

    if not args.file and not args.all:
        parser.print_help()
        print("\nExample:")
        print("  python add_punctuation_rules.py --file p3 --dry-run")
        print("  python add_punctuation_rules.py --file p3")
        print("  python add_punctuation_rules.py --all")
        sys.exit(1)

    base_dir = Path(__file__).parent

    if args.all:
        files_to_process = TEX_FILES
    else:
        file_key = args.file.lower()
        matched = [f for f in TEX_FILES if file_key in f]
        if not matched:
            print(f"Error: No file matching '{args.file}' found.")
            sys.exit(1)
        files_to_process = matched

    for tex_file in files_to_process:
        filepath = base_dir / tex_file
        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            continue
        process_file(str(filepath), dry_run=args.dry_run)

    print("\n" + "="*60)
    print("All done!")
    print("="*60)


if __name__ == '__main__':
    main()