---
name: course-to-pdf
description: This skill should be used to orchestrate the conversion of processed course materials (transcripts, slide OCR, audio/video summaries) into a structured Markdown document, converting it to LaTeX, and compiling a final PDF.
---

# Course to PDF

This skill encapsulates the standardized workflow to transform raw course transcripts and slide OCR data into a polished, structured PDF document via Markdown and LaTeX. 

## Prerequisites

Before executing this workflow, ensure the target directory contains:
- Raw transcript files (e.g., `.txt` files of audio transcripts).
- Slide OCR text files.
- Key slide images (e.g., `.jpg` or `.png` files) extracted from the video or presentation.
- A list of related reference links (e.g., arXiv papers) if applicable.

## Workflow Instructions

To execute the course-to-pdf workflow, follow these exact steps sequentially:

### 1. Create Structured Markdown
- Read the raw transcript and slide OCR text files.
- Synthesize the content into a structured Markdown (`.md`) document with logical headings, bullet points, and paragraphs.
- Cross-reference the slide OCR text to identify when a specific slide is being discussed.
- Insert key slide images (`![alt text](relative/path/to/image.jpg)`) at the exact relevant sections in the Markdown file.
- Embed related reference links (e.g., arXiv papers) inline where the topic is mentioned.

### 2. Generate LaTeX Source
- Read the generated Markdown document.
- Create a LaTeX (`.tex`) file using the provided template found in `assets/template.tex`.
- Translate the Markdown formatting into LaTeX commands:
  - Headings to `\section{}`, `\subsection{}`.
  - Lists to `\begin{itemize}` and `\end{itemize}`.
  - Images to the `\keyslide{image_path}{caption}` command defined in the template.
  - Bold text to `\textbf{}`.
- Update the title, subtitle, and author information in the LaTeX file to match the course content.

### 3. Setup Compilation Automation
- Copy the provided `assets/Makefile` template into the same directory as the new `.tex` file.
- Edit the `Makefile` and change the `TEX = template` line to match the base name of the newly created `.tex` file (e.g., `TEX = my_course_summary`).

### 4. Compile and Clean
- In the directory containing the `.tex` and `Makefile`, execute `make all` to compile the `.tex` file into a `.pdf` using `xelatex`.
- Ensure the compilation runs twice to properly generate the Table of Contents.
- Execute `make clean` to remove temporary auxiliary files (`.aux`, `.log`, `.toc`, etc.).

### 5. Version Control Integration
- Verify that `*.pdf` is listed in the project's `.gitignore` file to avoid tracking large binary files.
- Stage and commit the generated `.md`, `.tex`, and `Makefile` to the Git repository with a descriptive commit message.