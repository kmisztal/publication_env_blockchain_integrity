PDF=build/main.pdf

.PHONY: pdf clean review

pdf:
	mkdir -p build
	latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex

clean:
	latexmk -C -outdir=build main.tex

review:
	@echo "Build the manuscript first with: make pdf"
	@echo "Then create a review version in paper-reviewer using VERSION=$(VERSION)"
	@echo "Expected PDF: $(PDF)"
