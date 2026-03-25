# Makefile for p4_context_engineering_deep
TEX    = p4_context_engineering_deep
ENGINE = xelatex
FLAGS  = -interaction=nonstopmode -halt-on-error

.PHONY: all quick clean distclean watch

all: $(TEX).pdf

$(TEX).pdf: $(TEX).tex
	$(ENGINE) $(FLAGS) $(TEX).tex
	$(ENGINE) $(FLAGS) $(TEX).tex   # 第二次编译以生成目录和交叉引用

quick:
	$(ENGINE) $(FLAGS) $(TEX).tex

clean:
	rm -f $(TEX).aux $(TEX).log $(TEX).out $(TEX).toc $(TEX).synctex.gz $(TEX).fls $(TEX).fdb_latexmk

distclean: clean
	rm -f $(TEX).pdf

watch:
	fswatch -o $(TEX).tex | xargs -n1 -I{} make quick
