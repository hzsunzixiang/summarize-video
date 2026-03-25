# Makefile for course-to-pdf template
TEX    = template
ENGINE = xelatex
FLAGS  = -interaction=nonstopmode -halt-on-error

.PHONY: all quick clean distclean watch

all: $(TEX).pdf

$(TEX).pdf: $(TEX).tex
	$(ENGINE) $(FLAGS) $(TEX).tex
	$(ENGINE) $(FLAGS) $(TEX).tex   # Compile twice for TOC and cross-references

quick:
	$(ENGINE) $(FLAGS) $(TEX).tex

clean:
	rm -f $(TEX).aux $(TEX).log $(TEX).out $(TEX).toc $(TEX).synctex.gz $(TEX).fls $(TEX).fdb_latexmk

distclean: clean
	rm -f $(TEX).pdf

watch:
	fswatch -o $(TEX).tex | xargs -n1 -I{} make quick
