import os
import re

with open("p4_pdf/p4_full_transcript_with_slides.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

tex_out = []
tex_out.append(r"""% p4_full_transcript_with_slides.tex
% 编译方式: xelatex p4_full_transcript_with_slides.tex

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
  pdftitle={P4 Context Engineering - Full Transcript with All Slides},
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
  {\Huge\bfseries\sffamily 第四集 Context Engineering\par}
  \vspace{1.5cm}
  {\Large 全内容对比版（209张幻灯片与完整逐字稿对照呈现）\par}
  \vspace{2cm}
  \vfill
  {\large \today\par}
\end{titlepage}

\newpage
\tableofcontents
\newpage
""")

def escape_tex(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("%", "\\%")
    s = s.replace("&", "\\&")
    s = s.replace("#", "\\#")
    s = s.replace("_", "\\_")
    s = s.replace("$", "\\$")
    return s

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

with open("p4_pdf/p4_full_transcript_with_slides.tex", "w", encoding="utf-8") as f:
    f.write("\n".join(tex_out))

print("LaTeX file generated.")
