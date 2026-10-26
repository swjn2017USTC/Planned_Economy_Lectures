#!/usr/bin/env python3
"""Static verification of source/website, plus PDF structural checks."""
from pathlib import Path
from urllib.parse import unquote, urlparse
from bs4 import BeautifulSoup
import fitz,json,re,sys
P=Path(__file__).resolve().parent.parent; S=P/'site'
chapters=sorted((P/'manuscripts').glob('Lecture_*.md'))
assert len(chapters)==28
pages=sorted(S.glob('*.html'))
assert len(pages)==33,(len(pages),[x.name for x in pages])
errs=[]
for p in pages:
 soup=BeautifulSoup(p.read_text(encoding='utf-8'),'html.parser')
 assert soup.title, p.name
 for attr,tag in [('href','a'),('src','script'),('src','img'),('href','link')]:
  for el in soup.find_all(tag):
   u=el.get(attr,'');r=urlparse(u)
   if not u or u.startswith('#') or r.scheme or r.netloc:continue
   dest=(S/unquote(r.path))
   if not dest.exists():errs.append((p.name,tag,u))
for n in range(1,29):
 t=(S/f'lecture-{n:02}.html').read_text()
 assert t.count('<article')>=1 and '下载本讲原始 Markdown' in t
idx=json.loads((S/'assets/search.json').read_text());assert len(idx)>=5000
js=(S/'assets/experiments.js').read_text(); assert all(z in js for z in ['res-alloc','res-network','res-budget','res-external','res-forecast'])
fn=json.loads((P/'notes/source-manifest.json').read_text());assert not fn['footnote_issues']
pdf=P/'pdf/计划经济的运行改革与历史命运_学术排版版.pdf'
d=fitz.open(pdf)
assert len(d)>800 and len(d.get_toc())==40
assert not errs,errs[:20]
print(json.dumps({'chapters':len(chapters),'html_pages':len(pages),'search_passages':len(idx),'interactive_experiments':5,'pdf_pages':len(d),'pdf_bookmarks':len(d.get_toc()),'missing_links':len(errs),'footnote_issues':len(fn['footnote_issues'])},ensure_ascii=False,indent=2))
