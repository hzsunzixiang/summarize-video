import os
import re

PARTS = {
    "p1": {
        "title": "第一集 Context Engineering 基本概念",
        "pdf_dir": "p1_pdf",
        "audio_txt": "bilibili_audio/p1_large.txt",
        "slides_dir": "bilibili_video/slides_p1",
        "ocr_marker": "P1 - "
    },
    "p2": {
        "title": "第二集 AI Agent 互动",
        "pdf_dir": "p2_pdf",
        "audio_txt": "bilibili_audio/p2_large.txt",
        "slides_dir": "bilibili_video/slides_p2",
        "ocr_marker": "P2 - "
    },
    "p3": {
        "title": "第三集 AI Agent 对工作的冲击",
        "pdf_dir": "p3_pdf",
        "audio_txt": "bilibili_audio/p3_large.txt",
        "slides_dir": "bilibili_video/slides_p3",
        "ocr_marker": "P3 - "
    }
}

def clean_text(text):
    return set(re.findall(r'[\u4e00-\u9fff]', text))

def extract_links(text):
    return re.findall(r'https?://[^\s\)]+', text)

def escape_tex(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("%", "\\%")
    s = s.replace("&", "\\&")
    s = s.replace("#", "\\#")
    s = s.replace("_", "\\_")
    s = s.replace("$", "\\$")
    return s

def process_part(part_id, config, ocr_data):
    print(f"--- Processing {part_id} ---")
    
    # 1. Parse OCR data for this part
    slides = []
    curr_slide = None
    curr_text = []
    
    for line in ocr_data:
        m = re.match(r'^---\s*Slide\s+(\d+)\s*---', line)
        if m:
            if curr_slide is not None:
                slides.append((curr_slide, "".join(curr_text)))
            curr_slide = int(m.group(1))
            curr_text = []
        else:
            curr_text.append(line)
    if curr_slide is not None:
        slides.append((curr_slide, "".join(curr_text)))
        
    print(f"[{part_id}] Total slides found: {len(slides)}")
    
    # 2. Read Transcript
    txt_path = config["audio_txt"]
    if not os.path.exists(txt_path):
        print(f"Skipping {part_id}: Transcript {txt_path} not found.")
        return
        
    with open(txt_path, "r", encoding="utf-8") as f:
        transcript_lines = [l.strip() for l in f if l.strip()]
        
    CHUNKS = []
    CHUNK_SIZE = 5
    for i in range(0, len(transcript_lines), CHUNK_SIZE):
        chunk_text = " ".join(transcript_lines[i:i+CHUNK_SIZE])
        CHUNKS.append(chunk_text)
        
    print(f"[{part_id}] Total transcript chunks: {len(CHUNKS)}")
    
    if len(slides) == 0 or len(CHUNKS) == 0:
        print(f"[{part_id}] Missing slides or chunks. Skipping.")
        return

    # 3. DP Alignment
    sim = []
    for i, (sid, stext) in enumerate(slides):
        s_chars = clean_text(stext)
        row = []
        for j, ctext in enumerate(CHUNKS):
            c_chars = clean_text(ctext)
            score = len(s_chars.intersection(c_chars))
            row.append(score)
        sim.append(row)

    dp = [[0]*len(CHUNKS) for _ in range(len(slides))]
    parent = [[0]*len(CHUNKS) for _ in range(len(slides))]

    for j in range(len(CHUNKS)):
        dp[0][j] = sim[0][j]
        if j > 0 and dp[0][j-1] > dp[0][j]:
            dp[0][j] = dp[0][j-1]

    for i in range(1, len(slides)):
        for j in range(len(CHUNKS)):
            best_prev = -1
            best_prev_idx = -1
            for k in range(j+1):
                if dp[i-1][k] > best_prev:
                    best_prev = dp[i-1][k]
                    best_prev_idx = k
            
            current_score = best_prev + sim[i][j]
            dp[i][j] = current_score
            parent[i][j] = best_prev_idx

    assignments = [0] * len(slides)
    best_j = 0
    max_final = -1
    for j in range(len(CHUNKS)):
        if dp[-1][j] > max_final:
            max_final = dp[-1][j]
            best_j = j

    for i in range(len(slides)-1, -1, -1):
        assignments[i] = best_j
        if i > 0:
            best_j = parent[i][best_j]

    print(f"[{part_id}] DP Alignment done.")

    # 4. Generate Markdown
    md_filename = f"{part_id}_full_transcript_with_slides.md"
    md_path = os.path.join(config["pdf_dir"], md_filename)
    os.makedirs(config["pdf_dir"], exist_ok=True)
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {config['title']} (全内容对比版)\n\n")
        f.write("> 自动生成的带全部图片的逐字稿对应文档。如果图片有外部链接，也会一并提取。\n\n")
        
        chunk_to_slides = {}
        for i, j in enumerate(assignments):
            chunk_to_slides.setdefault(j, []).append(i)
        
        for j, ctext in enumerate(CHUNKS):
            if j in chunk_to_slides:
                for s_idx in chunk_to_slides[j]:
                    sid = slides[s_idx][0]
                    stext = slides[s_idx][1]
                    links = extract_links(stext)
                    
                    slide_filename = f"slide_{sid:04d}.jpg"
                    f.write(f"\n![Slide {sid}](../../{config['slides_dir']}/{slide_filename})\n")
                    if links:
                        f.write("\n**幻灯片引用链接:**\n")
                        for link in links:
                            link = re.sub(r'[\)\]\},]+$', '', link)
                            f.write(f"- [{link}]({link})\n")
                    f.write("\n")
                    
            f.write(ctext + "\n\n")
            
    print(f"[{part_id}] Markdown generated at {md_path}")
    
    # 5. Generate LaTeX from Markdown
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    tex_out = []
    tex_out.append(r"""% """ + md_filename.replace('.md', '.tex') + r"""
% 编译方式: xelatex """ + md_filename.replace('.md', '.tex') + r"""

\documentclass[12pt,a4paper]{article}

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
\usepackage{longtable,booktabs,array}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{caption}
\hypersetup{
  colorlinks=true,
  linkcolor=blue!70!black,
  urlcolor=blue!70!black,
  pdfauthor={Auto Generator},
  pdftitle={""" + config['title'] + r""" - Full Transcript with All Slides},
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
\setcounter{secnumdepth}{0}

\setlength{\emergencystretch}{3em}
\tolerance=1000

\newcommand{\keyslide}[2]{%
  \begin{center}
    \includegraphics[width=0.92\textwidth]{#1}
    \captionof{figure}{#2}
  \end{center}
  \vspace{10pt}
}

\begin{document}

\begin{titlepage}
  \centering
  \vspace*{3cm}
  {\Huge\bfseries\sffamily """ + config['title'] + r"""\par}
  \vspace{1.5cm}
  {\Large 全内容对比版（全部幻灯片与完整逐字稿对照呈现）\par}
  \vspace{2cm}
  \vfill
  {\large \today\par}
\end{titlepage}

\newpage
\tableofcontents
\newpage
""")

    for line in lines:
        line = line.strip()
        if not line:
            tex_out.append("")
            continue
        
        if line.startswith("# "):
            tex_out.append(f"\\section{{{escape_tex(line[2:])}}}")
            continue
        if line.startswith("## "):
            tex_out.append(f"\\subsection{{{escape_tex(line[3:])}}}")
            continue
        if line.startswith("> "):
            tex_out.append(f"\\begin{{myquote}}\n{escape_tex(line[2:])}\n\\end{{myquote}}")
            continue
            
        if line.startswith("!["):
            m = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if m:
                alt = escape_tex(m.group(1))
                path = m.group(2)
                # handle relative path
                tex_path = path.replace("../../bilibili_video", "../bilibili_video")
                tex_out.append(f"\\keyslide{{{tex_path}}}{{{alt}}}")
                continue
                
        if line.startswith("- ["):
            m = re.match(r'- \[(.*?)\]\((.*?)\)', line)
            if m:
                text = escape_tex(m.group(1))
                url = m.group(2)
                tex_out.append(f"\\begin{{itemize}}\n  \\item \\href{{{url}}}{{{text}}}\n\\end{{itemize}}")
                continue
                
        if line.startswith("**幻灯片引用链接:**"):
            tex_out.append(r"\textbf{幻灯片引用链接:}")
            continue
            
        line = escape_tex(line)
        tex_out.append(line)

    tex_out.append("\n\\end{document}")

    tex_filename = f"{part_id}_full_transcript_with_slides.tex"
    tex_path = os.path.join(config["pdf_dir"], tex_filename)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex_out))

    print(f"[{part_id}] LaTeX file generated at {tex_path}\n")

if __name__ == "__main__":
    with open("all_slides_ocr.txt", "r", encoding="utf-8") as f:
        all_ocr_lines = f.readlines()
        
    part_ocr_data = {"p1": [], "p2": [], "p3": []}
    current_part = None
    
    for line in all_ocr_lines:
        if line.startswith("# P1 - "):
            current_part = "p1"
        elif line.startswith("# P2 - "):
            current_part = "p2"
        elif line.startswith("# P3 - "):
            current_part = "p3"
        elif line.startswith("# P4 - "):
            current_part = "p4"
            
        if current_part and current_part in part_ocr_data:
            part_ocr_data[current_part].append(line)
            
    for part_id in ["p1", "p2", "p3"]:
        process_part(part_id, PARTS[part_id], part_ocr_data[part_id])