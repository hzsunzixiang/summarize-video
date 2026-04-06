#!/usr/bin/env python3
"""
add_punctuation.py
------------------
Process audio-transcribed .tex files and add proper Chinese punctuation marks.

This script:
1. Reads .tex files containing audio transcripts
2. Identifies plain text paragraphs (skips LaTeX commands, environments, etc.)
3. Sends text to Claude API for punctuation correction
4. Writes the corrected text back to the .tex files

Usage:
    python add_punctuation.py [--dry-run] [--file FILE] [--all]

Requirements:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key_here
"""

import os
import re
import sys
import argparse
import time
import copy
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: Please install anthropic package: pip install anthropic")
    sys.exit(1)


# Target .tex files
TEX_FILES = [
    "p1_pdf/p1_full_transcript_with_slides.tex",
    "p2_pdf/p2_full_transcript_with_slides.tex",
    "p3_pdf/p3_full_transcript_with_slides.tex",
    "p4_pdf/p4_full_transcript_with_slides.tex",
]

# Lines that are LaTeX commands or environments (should not be modified)
LATEX_PATTERNS = [
    r'^\s*$',                          # empty lines
    r'^\s*%',                          # comments
    r'^\s*\\',                         # LaTeX commands
    r'^\s*\{',                         # opening braces
    r'^\s*\}',                         # closing braces
    r'^\s*\[',                         # opening brackets
    r'^\s*\]',                         # closing brackets
    r'^\s*\\begin\{',                  # environment start
    r'^\s*\\end\{',                    # environment end
    r'^\s*\\item',                     # list items
    r'^\s*\\keyslide',                 # slide commands
    r'^\s*\\textbf',                   # bold text commands
    r'^\s*\\section',                  # section commands
    r'^\s*\\subsection',               # subsection commands
]


def is_latex_line(line: str) -> bool:
    """Check if a line is a LaTeX command/environment that should not be modified."""
    stripped = line.strip()
    if not stripped:
        return True
    for pattern in LATEX_PATTERNS:
        if re.match(pattern, stripped):
            return True
    return False


def is_transcript_text(line: str) -> bool:
    """Check if a line is transcript text that needs punctuation."""
    stripped = line.strip()
    if not stripped:
        return False
    if is_latex_line(line):
        return False
    # Must contain Chinese characters to be considered transcript text
    if re.search(r'[\u4e00-\u9fff]', stripped):
        return True
    return False


def extract_text_blocks(lines: list[str]) -> list[dict]:
    """
    Extract contiguous blocks of transcript text from the file lines.
    Returns a list of dicts with 'start_line', 'end_line', 'text' keys.
    """
    blocks = []
    i = 0
    while i < len(lines):
        if is_transcript_text(lines[i]):
            start = i
            text_lines = []
            while i < len(lines) and is_transcript_text(lines[i]):
                text_lines.append(lines[i])
                i += 1
            blocks.append({
                'start_line': start,
                'end_line': i - 1,
                'text': '\n'.join(text_lines),
                'original_lines': text_lines,
            })
        else:
            i += 1
    return blocks


def merge_blocks_for_batch(blocks: list[dict], max_chars: int = 3000) -> list[list[dict]]:
    """
    Merge small blocks into batches for efficient API calls.
    Each batch should not exceed max_chars total characters.
    """
    batches = []
    current_batch = []
    current_chars = 0

    for block in blocks:
        block_chars = len(block['text'])
        if current_chars + block_chars > max_chars and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_chars = 0
        current_batch.append(block)
        current_chars += block_chars

    if current_batch:
        batches.append(current_batch)

    return batches


def add_punctuation_with_ai(client: anthropic.Anthropic, text: str) -> str:
    """
    Use Claude to add proper punctuation to the transcript text.
    """
    prompt = f"""你是一个中文标点符号修正专家。以下是从音频转录的中文逐字稿，标点符号不完整，主要缺少句号（。）、问号（？）、感叹号（！）、冒号（：）、分号（；）等断句标点。

请为以下文本添加适当的标点符号，遵循以下规则：
1. 保留原有的逗号（,），但在需要断句的地方将逗号改为句号（。）、问号（？）等
2. 不要修改任何文字内容，只添加或修改标点符号
3. 不要添加或删除换行符，保持原有的行结构
4. 每行的文本独立处理，不要合并行
5. 疑问句末尾用问号（？）
6. 陈述句末尾用句号（。）
7. 感叹句末尾用感叹号（！）
8. 列举或解释前用冒号（：）
9. 不要修改英文单词、专有名词的大小写
10. 不要添加任何额外的解释，只返回修正后的文本

原文：
{text}

修正后的文本："""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        result = response.content[0].text.strip()
        return result
    except Exception as e:
        print(f"  [ERROR] API call failed: {e}")
        return text  # Return original text on failure


def process_file(filepath: str, client: anthropic.Anthropic, dry_run: bool = False) -> None:
    """Process a single .tex file to add punctuation."""
    print(f"\n{'='*60}")
    print(f"Processing: {filepath}")
    print(f"{'='*60}")

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Preserve original line endings
    original_lines = [line.rstrip('\n') for line in lines]

    # Extract text blocks
    blocks = extract_text_blocks(original_lines)
    print(f"  Found {len(blocks)} text blocks to process")

    if not blocks:
        print("  No transcript text found, skipping.")
        return

    # Merge blocks into batches
    batches = merge_blocks_for_batch(blocks, max_chars=2500)
    print(f"  Merged into {len(batches)} batches for API calls")

    # Process each batch
    modified_lines = original_lines.copy()
    total_batches = len(batches)

    for batch_idx, batch in enumerate(batches):
        # Combine all blocks in this batch with separator
        separator = "\n---BLOCK_SEP---\n"
        combined_text = separator.join(block['text'] for block in batch)

        print(f"  Processing batch {batch_idx + 1}/{total_batches} "
              f"({sum(len(b['text']) for b in batch)} chars, "
              f"{len(batch)} blocks)...")

        if dry_run:
            print(f"    [DRY RUN] Would send {len(combined_text)} chars to API")
            continue

        # Call AI to add punctuation
        corrected_text = add_punctuation_with_ai(client, combined_text)

        # Split back into blocks
        corrected_blocks = corrected_text.split("---BLOCK_SEP---")

        if len(corrected_blocks) != len(batch):
            print(f"    [WARNING] Block count mismatch: expected {len(batch)}, "
                  f"got {len(corrected_blocks)}. Trying line-by-line fallback...")
            # Fallback: process each block individually
            for block in batch:
                print(f"    Fallback: processing block at lines {block['start_line']+1}-{block['end_line']+1}...")
                corrected = add_punctuation_with_ai(client, block['text'])
                corrected_lines = corrected.strip().split('\n')
                orig_count = block['end_line'] - block['start_line'] + 1

                if len(corrected_lines) == orig_count:
                    for i, corrected_line in enumerate(corrected_lines):
                        modified_lines[block['start_line'] + i] = corrected_line
                else:
                    # If line count doesn't match, join and redistribute
                    print(f"    [WARNING] Line count mismatch at block {block['start_line']+1}: "
                          f"expected {orig_count}, got {len(corrected_lines)}. Using joined text.")
                    joined = ' '.join(corrected_lines)
                    # Put all text on the first line, clear the rest
                    modified_lines[block['start_line']] = joined
                    for i in range(1, orig_count):
                        modified_lines[block['start_line'] + i] = ''

                time.sleep(0.5)  # Rate limiting
            continue

        # Apply corrections
        for block, corrected_block in zip(batch, corrected_blocks):
            corrected_lines_list = corrected_block.strip().split('\n')
            orig_count = block['end_line'] - block['start_line'] + 1

            if len(corrected_lines_list) == orig_count:
                for i, corrected_line in enumerate(corrected_lines_list):
                    modified_lines[block['start_line'] + i] = corrected_line
            else:
                print(f"    [WARNING] Line count mismatch at block {block['start_line']+1}: "
                      f"expected {orig_count}, got {len(corrected_lines_list)}. Using joined text.")
                joined = ' '.join(corrected_lines_list)
                modified_lines[block['start_line']] = joined
                for i in range(1, orig_count):
                    modified_lines[block['start_line'] + i] = ''

        # Rate limiting between batches
        if batch_idx < total_batches - 1:
            time.sleep(1)

    if dry_run:
        print("  [DRY RUN] No changes written.")
        return

    # Remove empty lines that were created by line count mismatches
    # (but preserve intentional empty lines from the original)
    final_lines = []
    for i, line in enumerate(modified_lines):
        if line == '' and original_lines[i] != '':
            continue  # Skip lines that were emptied due to mismatch
        final_lines.append(line)

    # Write back
    backup_path = filepath + '.bak'
    print(f"  Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(original_lines) + '\n')

    print(f"  Writing corrected file: {filepath}")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines) + '\n')

    print(f"  Done! Processed {len(blocks)} text blocks.")


def main():
    parser = argparse.ArgumentParser(
        description='Add punctuation to audio-transcribed .tex files'
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
        print("  python add_punctuation.py --file p1 --dry-run")
        print("  python add_punctuation.py --file p1")
        print("  python add_punctuation.py --all")
        sys.exit(1)

    # Determine base directory
    base_dir = Path(__file__).parent

    # Select files to process
    if args.all:
        files_to_process = TEX_FILES
    else:
        file_key = args.file.lower()
        matched = [f for f in TEX_FILES if file_key in f]
        if not matched:
            print(f"Error: No file matching '{args.file}' found.")
            print(f"Available: p1, p2, p3, p4")
            sys.exit(1)
        files_to_process = matched

    # Initialize Anthropic client
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key and not args.dry_run:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Export it: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    client = None
    if not args.dry_run:
        client = anthropic.Anthropic(api_key=api_key)

    # Process files
    for tex_file in files_to_process:
        filepath = base_dir / tex_file
        if not filepath.exists():
            print(f"Warning: File not found: {filepath}")
            continue
        process_file(str(filepath), client, dry_run=args.dry_run)

    print("\n" + "="*60)
    print("All done!")
    if not args.dry_run:
        print("Backup files (.bak) have been created for each processed file.")
        print("To recompile PDFs, run 'make' in each p*_pdf directory.")
    print("="*60)


if __name__ == '__main__':
    main()
