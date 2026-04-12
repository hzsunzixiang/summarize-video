# Makefile for FHE Transcript PDFs
# Compile with xelatex (CJK support)

# Summary version (with LLM-summarized transcript)
TEX_SUMMARY = fhe_transcript_with_slides.tex
PDF_SUMMARY = $(TEX_SUMMARY:.tex=.pdf)

# Full verbatim transcript version (whisper raw output)
TEX_FULL    = fhe_full_transcript.tex
PDF_FULL    = $(TEX_FULL:.tex=.pdf)

XELATEX  = xelatex
FLAGS    = -interaction=nonstopmode -halt-on-error

# Build all PDFs
all: $(PDF_SUMMARY) $(PDF_FULL)

# Build only the full transcript version
full: $(PDF_FULL)

# Build only the summary version
summary: $(PDF_SUMMARY)

$(PDF_SUMMARY): $(TEX_SUMMARY) $(wildcard images/*.jpg)
	$(XELATEX) $(FLAGS) $(TEX_SUMMARY)
	$(XELATEX) $(FLAGS) $(TEX_SUMMARY)

$(PDF_FULL): $(TEX_FULL) $(wildcard images/*.jpg)
	$(XELATEX) $(FLAGS) $(TEX_FULL)
	$(XELATEX) $(FLAGS) $(TEX_FULL)

# Quick compile (single pass, TOC may be wrong)
quick:
	$(XELATEX) $(FLAGS) $(TEX_FULL)

# Clean auxiliary files
clean:
	rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz *.nav *.snm *.vrb

# Deep clean (including PDF)
distclean: clean
	rm -f $(PDF_SUMMARY) $(PDF_FULL)

# Watch for changes and recompile (requires fswatch)
watch:
	@echo "Watching $(TEX_FULL) for changes..."
	fswatch -o $(TEX_FULL) | xargs -n1 -I{} make quick

.PHONY: all full summary quick clean distclean watch
