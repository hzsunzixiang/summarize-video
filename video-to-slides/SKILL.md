---
name: video-to-slides
description: Convert raw video or course materials into structured, polished PDF handouts or LaTeX Beamer presentation slides, incorporating original extracted slide frames and summarized transcripts.
---

# Video to Slides

This skill orchestrates the conversion of processed video/audio materials (transcripts, slide OCR, audio summaries) into presentation-ready documents. It supports two main outputs:
1. **Handout PDF**: A detailed transcript and summary document containing matching slide images (using standard LaTeX `article`).
2. **Beamer Slides**: A formal slide presentation deck summarizing the content visually (using LaTeX `beamer`).

## Prerequisites

Before executing this workflow, ensure the target directory contains:
- Raw transcript files (e.g., `.txt` files of audio transcripts).
- Slide OCR text files.
- Extracted key slide images (e.g., `.jpg` or `.png` files).
- Related reference links (e.g., arXiv papers) if applicable.

## Workflow Instructions

To execute the `video-to-slides` workflow, follow these steps sequentially:

### 1. Structure the Content & Align
- **For Handout PDF**: Align the transcript chunks with the OCR text to figure out exactly when each slide appears. Produce a structured Markdown document (`.md`) containing full/summarized text, headers, and embedded image paths.
- **For Beamer Slides**: Synthesize and condense the transcript into concise bullet points. Map each extracted slide image to a specific Beamer frame. Produce a structured Markdown or JSON blueprint representing the presentation flow.

### 2. Generate LaTeX Source
Select the appropriate template from the `assets/` directory based on the desired output mode:

#### Option A: Handout PDF (`assets/handout_template.tex`)
- Read the generated Markdown document.
- Translate it into a standard LaTeX `.tex` file using `article` class.
- Map headings to `\section{}`, lists to `\begin{itemize}`, and images to `\keyslide{image_path}{caption}`.

#### Option B: Beamer Slides (`assets/beamer_template.tex`)
- Translate the condensed bullet points and image paths into a Beamer `.tex` file.
- Use `\begin{frame}{Frame Title}` and `\end{frame}` for each slide.
- Incorporate the original video's slide images using `\includegraphics` within a `columns` or centered layout, accompanied by the summarized bullet points.
- Ensure the LaTeX correctly specifies the `xeCJK` fonts to support Chinese text.

### 3. Compilation Setup
- Copy `assets/Makefile` into the same directory as the `.tex` file.
- Update the `TEX = ...` variable in the `Makefile` to match the target filename.

### 4. Compile and Clean
- Execute `make all` to compile the LaTeX source into a PDF using `xelatex`. The `Makefile` will run it twice to build TOC/references.
- Execute `make clean` to remove temporary auxiliary files.

### 5. Version Control Integration
- Ensure `*.pdf` is ignored via `.gitignore`.
- Stage and commit the generated source files (`.md`, `.tex`, `Makefile`, and extraction scripts) to Git.
