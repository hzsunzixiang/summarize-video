# Makefile for Context Engineering PDF
# 使用 xelatex 编译（支持中文）

TEX      = p1_context_engineering.tex
PDF      = $(TEX:.tex=.pdf)
XELATEX  = xelatex
FLAGS    = -interaction=nonstopmode -halt-on-error

# 需要编译两次：第一次生成目录引用，第二次解析引用
all: $(PDF)

$(PDF): $(TEX) $(wildcard *.jpg)
	$(XELATEX) $(FLAGS) $(TEX)
	$(XELATEX) $(FLAGS) $(TEX)

# 只编译一次（快速预览，目录页码可能不对）
quick:
	$(XELATEX) $(FLAGS) $(TEX)

# 清理辅助文件
clean:
	rm -f *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz *.nav *.snm *.vrb

# 清理全部（包括 PDF）
distclean: clean
	rm -f $(PDF)

# 自动监听变化并重新编译（需要 fswatch）
watch:
	@echo "监听 $(TEX) 的变化..."
	fswatch -o $(TEX) | xargs -n1 -I{} make quick

.PHONY: all quick clean distclean watch
