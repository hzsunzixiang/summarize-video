SUBDIRS := p1_pdf p2_pdf p3_pdf p4_pdf

.PHONY: all clean distclean $(SUBDIRS)

# 默认目标：编译所有子目录中的所有 tex 文件
all: $(SUBDIRS)

# 遍历每个子目录并编译其中的每一个 .tex 文件两次（确保交叉引用和目录正确）
$(SUBDIRS):
	@echo "========================================"
	@echo "Building all TeX files in $@..."
	@echo "========================================"
	@cd $@ && for texfile in *.tex; do \
		if [ -f "$$texfile" ]; then \
			echo "--> Compiling $$texfile"; \
			xelatex -interaction=nonstopmode -halt-on-error "$$texfile"; \
			xelatex -interaction=nonstopmode -halt-on-error "$$texfile"; \
		fi \
	done

# 清理中间产生的文件
clean:
	@for dir in $(SUBDIRS); do \
		echo "Cleaning temporary files in $$dir..."; \
		(cd $$dir && rm -f *.aux *.log *.out *.toc *.synctex.gz *.fls *.fdb_latexmk) || true; \
	done
	@echo "Clean complete."

# 深度清理（包含生成的 PDF）
distclean: clean
	@for dir in $(SUBDIRS); do \
		echo "Removing PDF files in $$dir..."; \
		(cd $$dir && rm -f *.pdf) || true; \
	done
	@echo "Distclean complete."
