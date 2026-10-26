#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python - <<'PY'
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pathlib import Path
root=Path.cwd(); src=root/'assets/cover.png';out=root/'assets/cover.pdf'
c=canvas.Canvas(str(out),pagesize=(170/25.4*72,240/25.4*72),pageCompression=1)
c.drawImage(ImageReader(str(src)),0,0,width=170/25.4*72,height=240/25.4*72)
c.showPage();c.save()
PY
pandoc latex/book.md -s -f markdown-yaml_metadata_block+footnotes+raw_tex+tex_math_dollars+tex_math_single_backslash \
  --top-level-division=chapter -t latex -o latex/book.tex \
  -V documentclass=book -V classoption='11pt,openany' \
  -V papersize=custom -V geometry='paperwidth=170mm,paperheight=240mm,inner=23mm,outer=20mm,top=22mm,bottom=24mm' \
  -V mainfont='Liberation Serif' -V CJKmainfont='Noto Serif CJK SC' -V sansfont='Noto Sans' \
  -V fontsize=11pt -V colorlinks=true --include-in-header=latex/layout.tex
mkdir -p pdf
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=latex latex/book.tex > latex/build-pass1.log 2>&1 || { tail -45 latex/build-pass1.log; exit 1; }
xelatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=latex latex/book.tex > latex/build-pass2.log 2>&1 || { tail -45 latex/build-pass2.log; exit 1; }
cp latex/book.pdf pdf/计划经济的运行改革与历史命运_学术排版版.pdf
pdfinfo pdf/计划经济的运行改革与历史命运_学术排版版.pdf | head -18
