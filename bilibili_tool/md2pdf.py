#!/usr/bin/env python3
"""Convert Markdown to PDF using markdown + weasyprint.

Fallback PDF generator when LaTeX/xelatex is not available.
Supports embedded images and CJK (Chinese) text.

Usage:
    python3 md2pdf.py --input transcript.md --output transcript.pdf [--images images/]

Requirements:
    pip3 install markdown weasyprint
"""

import argparse
import os
import sys

def check_dependencies():
    """Check if required Python packages are available."""
    missing = []
    try:
        import markdown
    except ImportError:
        missing.append("markdown")
    try:
        import weasyprint
    except ImportError:
        missing.append("weasyprint")
    if missing:
        print(f"ERROR: Missing Python packages: {', '.join(missing)}")
        print(f"Install: pip3 install {' '.join(missing)}")
        sys.exit(1)


def md_to_pdf(input_path, output_path, images_dir=None):
    """Convert Markdown file to PDF."""
    import markdown
    from weasyprint import HTML

    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Convert Markdown to HTML
    extensions = ["tables", "fenced_code", "toc", "attr_list"]
    html_body = markdown.markdown(md_text, extensions=extensions)

    # Resolve image paths
    base_url = os.path.dirname(os.path.abspath(input_path))
    if images_dir:
        base_url = os.path.dirname(os.path.abspath(input_path))

    # Wrap in full HTML with CSS for nice styling
    html_full = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: A4;
    margin: 2.5cm;
}}
body {{
    font-family: "PingFang SC", "Helvetica Neue", "Noto Sans CJK SC", sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
    max-width: 100%;
}}
h1 {{
    font-size: 24pt;
    text-align: center;
    margin-top: 3cm;
    margin-bottom: 1cm;
    color: #1a1a1a;
    page-break-before: avoid;
}}
h2 {{
    font-size: 16pt;
    border-bottom: 2px solid #4a90d9;
    padding-bottom: 4pt;
    margin-top: 1.5em;
    color: #2c3e50;
    page-break-after: avoid;
}}
h3 {{
    font-size: 13pt;
    color: #34495e;
}}
p {{
    margin: 6pt 0;
    text-align: justify;
}}
img {{
    max-width: 88%;
    display: block;
    margin: 12pt auto;
    border: 1px solid #ddd;
    border-radius: 4px;
}}
em {{
    display: block;
    text-align: center;
    color: #888;
    font-size: 9pt;
    margin-bottom: 8pt;
}}
sub {{
    color: #999;
    font-size: 8pt;
}}
hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 1.5em 0;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}}
th {{
    background-color: #f5f5f5;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    # Generate PDF
    HTML(string=html_full, base_url=base_url).write_pdf(output_path)
    print(f"PDF written to {output_path}")
    print(f"Size: {os.path.getsize(output_path)} bytes")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to PDF (fallback when LaTeX is unavailable)."
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Input Markdown file"
    )
    parser.add_argument(
        "--output", "-o", required=True,
        help="Output PDF file"
    )
    parser.add_argument(
        "--images", default=None,
        help="Images directory (for resolving relative image paths)"
    )
    args = parser.parse_args()

    check_dependencies()
    md_to_pdf(args.input, args.output, args.images)


if __name__ == "__main__":
    main()
