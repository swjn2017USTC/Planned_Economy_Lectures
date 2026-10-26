#!/usr/bin/env python3
"""Single-source publication builder: 28 Markdown chapters -> LaTeX book input and static site."""
from pathlib import Path
import re,subprocess,json,html,shutil,os,hashlib,sys,unicodedata
BASE=Path(__file__).resolve().parent.parent
ORIG=BASE/'manuscripts';SRC=BASE/'edited';SITE=BASE/'site';PDFSRC=BASE/'latex';ASSETS=BASE/'assets'
SRC.mkdir(exist_ok=True)
# Non-destructive editorial normalization: horizontal rules and blank lines.
for source in ORIG.glob('Lecture_*.md'):
    original=source.read_text(encoding='utf-8-sig')
    edited=re.sub(r'(?m)^---[ \t]*$', '\n* * *\n', original)
    (SRC/source.name).write_text(edited,encoding='utf-8')
SITE.mkdir(exist_ok=True);PDFSRC.mkdir(exist_ok=True)
parts=[('第一编','从革命理想到国家经济计划'),('第二编','从煤矿到百货商店：生产机器'),('第三编','从银行到家庭：社会再生产'),('第四编','匈牙利改革的实际运行'),('第五编','外部约束、危机与制度终结'),('第六编','苏东和中国比较'),('第七编','建模、证据与综合解释')]
def partof(n):return (n-1)//4
files=sorted(SRC.glob('Lecture_*.md'))
assert len(files)==28,f"Expected 28 chapters; got {len(files)}"
records=[];cleaned=[];footnoteIssues=[]
for n,p in enumerate(files,1):
 assert re.search(rf'Lecture_{n:02}_',p.name),p.name
 orig=p.read_text(encoding='utf-8-sig').replace('\r\n','\n')
 orig=orig.replace('\u00a0',' ').replace('\u200b','')
 h=re.search(r'^# (.+)$',orig,re.M);assert h,(n,p)
 title=h.group(1).strip()
 ref_re=re.compile(r'\[\^([^\]\n]+)\]')
 ids=set(ref_re.findall(orig))
 refs=set(re.findall(r'(?<!^)\[\^([^\]\n]+)\](?!:)',orig)) # rough
 defs=set(re.findall(r'^\[\^([^\]\n]+)\]:',orig,re.M))
 if ids-defs:footnoteIssues.append((n,sorted(ids-defs)))
 # globally unique ids for book (protect both definitions & references)
 transformed=ref_re.sub(lambda m:'[^L%02d_%s]'%(n,re.sub('[^a-zA-Z0-9_-]','_',m.group(1))),orig)
 cleaned.append(transformed)
 title_plain=re.sub(r'\*','',title)
 records.append({'n':n,'filename':p.name,'title':title_plain,'part':partof(n),'characters':len(orig),'edited_sha256':hashlib.sha256(orig.encode()).hexdigest(),'source_sha256':hashlib.sha256((ORIG/p.name).read_bytes()).hexdigest(),'footnotes':len(defs)})
# combined book: source-faithful; chapter-footnote references namespaced, part boundaries provided by LaTeX
front='''\\includepdf[pages=1,fitpaper]{assets/cover.pdf}
\\frontmatter
\\thispagestyle{empty}
\\vspace*{4cm}
\\begin{center}
{\\Huge\\bfseries 计划经济的运行、改革与历史命运\\par}
\\vspace{1.5cm}
{\\Large 以匈牙利社会主义经济史与 Hungary Socialist Mechanism Lab 为中心\\par}
\\vspace{0.7cm}
{\\large 七编二十八讲 · 研究型教材\\par}
\\vfill
{\\normalsize 统一编校版 · 2026年10月\\par}
\\end{center}
\\cleardoublepage
\\tableofcontents
\\cleardoublepage
\\mainmatter
'''
front=front.replace("\\frontmatter\n", "")
book=[front]
for i,(rec,chunk) in enumerate(zip(records,cleaned)):
 if rec['n']%4==1:
  tag,title=parts[rec['part']]
  book.append(f'\\part{{{tag}｜{title}}}\n')
 book.append(chunk)
book.append('\\appendix')
for appendix_name in ['术语与人物索引.md','比较历史年表.md','经济数学工具箱.md','HSM证据与书目说明.md']:
 book.append((BASE/'Appendices'/appendix_name).read_text(encoding='utf-8'))
book.append('''
\\cleardoublepage
\\backmatter
\\chapter*{编校说明}
\\addcontentsline{toc}{chapter}{编校说明}
本版按照统一写作规程汇集二十八讲。各讲保留独立史料来源与研究边界；为避免误引，未将各讲参考书目擅自合并为一个被默认为全部核查的书目。书内存在不同研究阶段的模拟报告时，以各讲注明的场景、日期和证据等级为准；HSM 的研究包完整不等于历史机制已经得到验证。
''')
(PDFSRC/'book.md').write_text('\n\n'.join(book),encoding='utf-8')
# website assets
(SITE/'assets').mkdir(exist_ok=True)
for p in (ASSETS/'cover-web.jpg',ASSETS/'cover-art.jpg'):
 shutil.copy2(p,SITE/'assets'/p.name)
for p in (ORIG).glob('*.md'): # downloads for transparency
 (SITE/'source').mkdir(exist_ok=True)
 shutil.copy2(p,SITE/'source'/p.name)
# create responsive site
CSS=r'''@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&family=Noto+Serif+SC:wght@400;500;600;700&display=swap');
:root{--bg:#f6f3ed;--paper:#fffcf7;--ink:#29373c;--muted:#6e7776;--red:#a34a40;--border:#dedad0;--warm:#e9e4da;--blue:#4b6a6f;--max:850px}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.9 'Noto Serif SC', 'Noto Serif CJK SC',Georgia,serif}a{color:#8b463b;text-decoration:none}a:hover{text-decoration:underline}p{margin:0 0 1.1em;text-align:justify}h1,h2,h3,h4{color:#23343b;font-family:'Noto Sans SC','Noto Sans CJK SC',sans-serif;line-height:1.48;scroll-margin-top:4.5rem}h1{font-size:2rem;letter-spacing:.015em}h2{font-size:1.43rem;margin:2.5em 0 1em;border-bottom:1px solid var(--border);padding-bottom:.45em}h3{font-size:1.15rem;margin:2em 0 .8em}h4{font-size:1.02rem}blockquote{margin:1.2em 0;padding:12px 22px;border-left:3px solid var(--red);background:#f3eee5;color:#4d5959}blockquote p{margin:.3em 0;text-align:left}.layout{display:grid;grid-template-columns:280px minmax(0,1fr);min-height:100vh}.sidebar{position:sticky;top:0;height:100vh;overflow-y:auto;padding:28px 20px;background:#eeeae0;border-right:1px solid var(--border);font-family:'Noto Sans SC',sans-serif}.brand{font-weight:700;font-size:1.08rem;line-height:1.6;display:block;color:var(--ink);margin-bottom:12px}.small{font-size:.76rem;color:var(--muted);line-height:1.65}.search{width:100%;padding:10px 12px;border:1px solid #cfc8bc;border-radius:7px;background:#fffdfa;color:var(--ink);font-size:.91rem;margin:12px 0 16px}.nav-part{font-size:.78rem;font-weight:700;color:var(--red);margin-top:20px;margin-bottom:6px}.nav-item{display:block;padding:5px 8px;margin:2px 0;border-radius:5px;color:#3d484c;font-size:.78rem;line-height:1.6}.nav-item.active,.nav-item:hover{background:#ddd8ce;color:#8b4038;text-decoration:none}.main{min-width:0}.top{position:sticky;top:0;z-index:8;background:#f6f3edee;backdrop-filter:blur(8px);border-bottom:1px solid var(--border);padding:12px max(24px,calc((100% - 925px)/2));display:flex;gap:18px;align-items:center;font:500 .85rem 'Noto Sans SC',sans-serif}.top a{white-space:nowrap}.top .spacer{flex:1}.wrap{max-width:960px;padding:48px 48px 90px;margin:auto}.article{max-width:var(--max);margin:auto}.article>h1:first-child{margin-top:0;font-size:2.13rem}.article>blockquote:first-of-type{font:400 .89rem/1.8 'Noto Sans SC',sans-serif}.article li{margin:.4em 0}.article ul,.article ol{padding-left:1.7em}.article hr{border:0;border-top:1px solid var(--border);margin:2rem 0}.article table{border-collapse:collapse;font:400 .83rem/1.7 'Noto Sans SC',sans-serif;margin:1.5rem 0;width:100%;min-width:470px}.article th,.article td{border-bottom:1px solid #d9d5ca;padding:8px 10px;text-align:left;vertical-align:top}.article th{background:#eee8dc}.article code{font:.86em Consolas,'SFMono-Regular',monospace;background:#eeeae1;padding:1px 4px;border-radius:3px;overflow-wrap:anywhere}.article pre{background:#29393d;color:#f0eee8;padding:18px 20px;border-radius:8px;overflow:auto;font:13px/1.6 Consolas,'SFMono-Regular',monospace}.article pre code{background:none;color:inherit}.article img{max-width:100%}.table-wrap{overflow-x:auto}.footnotes{margin-top:3rem;padding-top:1rem;border-top:1px solid #cabfb0;color:#4c5656;font-size:.85em}.footnotes ol{padding-left:1.3em}.footnotes li{word-break:break-word}.paged{border-top:1px solid var(--border);padding-top:28px;display:flex;justify-content:space-between;gap:12px;margin-top:50px;font:500 .87rem 'Noto Sans SC',sans-serif}.hero{display:grid;grid-template-columns:minmax(0,1fr) 280px;gap:44px;align-items:center;margin:15px auto 48px;max-width:900px}.hero h1{font-size:2.6rem;margin:0 0 15px}.hero img{width:100%;border-radius:3px;box-shadow:10px 16px 30px #3f46412c}.lead{font-size:1.08rem;line-height:2;color:#455354}.pill{font:600 .78rem 'Noto Sans SC',sans-serif;color:var(--red);letter-spacing:.1em}.part-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(265px,1fr));gap:17px;margin:22px 0 45px}.part-card{background:var(--paper);padding:22px 22px 14px;border:1px solid var(--border);border-radius:9px}.part-card h2{font-size:1rem;margin:0 0 10px;border:0;padding:0}.part-card a{display:block;font:400 .84rem/1.65 'Noto Sans SC',sans-serif;padding:5px 0;color:#425354}.callout{background:#efe8dd;border-left:3px solid var(--red);padding:14px 20px;margin:18px 0;font:400 .92rem/1.8 'Noto Sans SC',sans-serif}.button{display:inline-block;border:1px solid var(--red);background:var(--red);color:white;padding:9px 15px;border-radius:5px;font:600 .84rem 'Noto Sans SC',sans-serif;margin:10px 5px 10px 0}.button.light{color:var(--red);background:transparent}.button:hover{text-decoration:none;filter:brightness(.95)}.mobile-menu{display:none}.search-results{max-width:var(--max);margin:0 auto}.hit{padding:17px 0;border-bottom:1px solid var(--border)}.hit a{font:600 1rem 'Noto Sans SC',sans-serif}.hit .excerpt{font-size:.87rem;color:#596362;line-height:1.75;margin:.4rem 0 0}.exp{padding:24px;border:1px solid var(--border);background:var(--paper);border-radius:10px;margin:28px 0}.exp h2{margin:0 0 10px}.control{display:grid;grid-template-columns:200px 1fr 70px;align-items:center;gap:12px;margin:15px 0;font:500 .85rem 'Noto Sans SC',sans-serif}.control input{width:100%;accent-color:var(--red)}.result{background:#edece5;padding:16px;margin:14px 0;border-radius:7px;font:500 .9rem/1.85 'Noto Sans SC',sans-serif}.bars{display:flex;align-items:end;gap:18px;height:175px;margin:28px 0 10px;border-bottom:1px solid #979f97;padding:10px 12px 0}.bar-col{height:100%;flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;font:500 .79rem 'Noto Sans SC',sans-serif}.bar{width:65%;max-width:80px;min-height:2px;background:var(--blue);transition:height .2s}.bar.red{background:var(--red)}.bar.gold{background:#b69c61}.bar-caption{padding-top:7px;text-align:center;font:500 .78rem 'Noto Sans SC',sans-serif}.footer{padding:40px 0;text-align:center;color:var(--muted);font:400 .8rem 'Noto Sans SC',sans-serif}.skip{position:absolute;left:-999px}.skip:focus{left:10px;top:10px;z-index:50;background:white;padding:8px}@media(max-width:900px){.layout{display:block}.sidebar{position:fixed;z-index:20;transform:translateX(-101%);transition:.2s;max-width:85vw;box-shadow:0 10px 35px #0002}.sidebar.open{transform:translateX(0)}.mobile-menu{display:inline-block;background:transparent;border:0;font-size:1rem;cursor:pointer;color:var(--red)}.wrap{padding:28px 23px 65px}.top{padding:11px 22px}.hero{grid-template-columns:1fr 160px;gap:18px}.hero h1{font-size:1.85rem}}@media(max-width:560px){.hero{grid-template-columns:1fr}.hero img{max-width:220px}.article>h1:first-child{font-size:1.65rem}h2{font-size:1.23rem}.control{grid-template-columns:1fr 80px;gap:7px}.control label{grid-column:1/3}.control input{grid-column:1/2}.control output{grid-column:2/3}.wrap{padding:25px 18px 60px}.top{gap:10px}}
'''
(SITE/'assets'/'style.css').write_text(CSS,encoding='utf-8')
# nav html
navparts=''.join(f'<div class="nav-part">{p[0]} · {html.escape(p[1])}</div>'+''.join(f'<a class="nav-item {{active{r["n"]}}}" href="lecture-{r["n"]:02d}.html">{r["n"]:02d} · {html.escape(r["title"].split("｜",1)[-1][:26])}</a>' for r in records if r['part']==pi) for pi,p in enumerate(parts))
# Avoid escaping double braces: use string replacement
navparts=navparts.replace('{active','{active')
header='''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>__TITLE__ · 计划经济的运行、改革与历史命运</title><meta name="description" content="七编二十八讲：社会主义经济史、政治经济学与历史计算实验。"><link rel="stylesheet" href="assets/style.css"><script defer src="assets/site.js"></script><script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script></head><body><a class="skip" href="#content">跳转到正文</a><div class="layout"><aside class="sidebar" id="sidebar"><a class="brand" href="index.html">计划经济的运行、改革与历史命运</a><div class="small">社会主义经济史 · 七编二十八讲</div><form action="search.html"><input class="search" aria-label="搜索讲义" type="search" name="q" placeholder="搜索28讲全文…"></form><a class="nav-item" href="experiments.html">◈ 互动机制实验室</a><a class="nav-item" href="reading.html">◎ 阅读指南与版本说明</a><a class="nav-item" href="appendices.html">◉ 全书附录、年表及术语</a>__SIDENAV__</aside><div class="main"><div class="top"><button class="mobile-menu" aria-label="打开目录" onclick="document.getElementById('sidebar').classList.toggle('open')">☰ 目录</button><a href="index.html">课程首页</a><a href="experiments.html">互动实验</a><div class="spacer"></div><a href="reading.html">关于本书</a></div><main class="wrap" id="content">__BODY__</main><footer class="footer">© 2026 · 计划经济系列讲义 · 本站为独立教学材料，模型结果不等于历史验证</footer></div></div></body></html>'''
def page(name,title,body,n=None):
 nav=navparts
 for r in records:nav=nav.replace('{active'+str(r['n'])+'}', 'active' if r['n']==n else '')
 s=header.replace('__TITLE__',html.escape(title)).replace('__SIDENAV__',nav).replace('__BODY__',body)
 (SITE/name).write_text(s,encoding='utf-8')
# Pandoc conversion standalone fragments with MathJax markers (script loading comes from custom page)
for r in records:
 p=SRC/r['filename']
 cmd=['pandoc','--from=markdown-yaml_metadata_block+footnotes+tex_math_dollars+tex_math_single_backslash+raw_tex','--to=html5','--mathjax','--wrap=none',str(p)]
 raw=subprocess.check_output(cmd,stderr=subprocess.DEVNULL).decode('utf-8')
 raw=re.sub(r'<table(\s|>)',r'<table\1',raw)
 raw=re.sub(r'(<table[^>]*>.*?</table>)',r'<div class="table-wrap">\1</div>',raw,flags=re.S)
 # add didactic model note after first paragraph only on relevant chapters
 jump=f'<p class="callout">本讲相关互动实验：<a href="experiments.html">打开经济机制实验室 →</a>。实验为简化教学模型，不代表匈牙利历史估计。</p>' if r['n'] in [3,4,7,8,9,17,18,25,26,27] else ''
 jump = '<p class="small"><a href="source/'+r['filename']+'" download>下载本讲原始 Markdown</a></p>' + jump
 idx=r['n']-1
 prev=records[idx-1] if idx>0 else None;nx=records[idx+1] if idx<27 else None
 navlinks='<div class="paged">'+(f'<a href="lecture-{prev["n"]:02d}.html">← 第{prev["n"]:02d}讲</a>' if prev else '<span>全书开始</span>')+(f'<a href="lecture-{nx["n"]:02d}.html">第{nx["n"]:02d}讲 →</a>' if nx else '<span>全书完</span>')+'</div>'
 page(f'lecture-{r["n"]:02d}.html',r['title'],f'<article class="article">{raw}{jump}{navlinks}</article>',r['n'])
# home
cards=''.join('<section class="part-card"><h2>'+parts[i][0]+'｜'+html.escape(parts[i][1])+'</h2>'+''.join(f'<a href="lecture-{r["n"]:02d}.html">{r["n"]:02d}　{html.escape(r["title"].split("｜",1)[-1])}</a>' for r in records if r['part']==i)+'</section>' for i in range(7))
home='''<div class="hero"><div><div class="pill">社会主义经济史 · 数字研究型教材</div><h1>计划经济的运行、改革与历史命运</h1><p class="lead">国家如何组织生产？改革改变了哪些约束？为什么社会主义经济产生了不同的历史结局？以匈牙利1956—1989年的制度史为主线，联系苏联、东欧与中国，辅以可审计的计算实验。</p><a class="button" href="lecture-01.html">从第一讲开始</a><a class="button light" href="experiments.html">体验互动模型</a></div><img src="assets/cover-web.jpg" alt="苏东构成主义与马赛克风格教材封面"></div><p class="callout"><strong>阅读原则：</strong>历史事实、理论解释、模拟输出与作者推论分层展示。HSM当前没有获得历史机制 SUPPORTED 的机制卡；互动实验仅用于揭示约束与反事实逻辑。</p><h2>七编 · 二十八讲</h2><div class="part-grid">'''+cards+'</div>'
home += '<p><a class="button light" href="appendices.html">术语与全书附录</a><a class="button light" href="pdf/book.pdf" download>下载合订PDF</a></p>'
page('index.html','全书目录',home)
reading='''<article class="article"><h1>阅读说明与出版版本</h1><p>本书由28份原始Markdown统一编校而成。编辑仅处理结构、链接、书面排版及脚注全书合并时的名称冲突，不擅改原始史料结论。网站逐讲提供原始 Markdown，可通过阅读器底部或网站目录访问。</p><h2>证据分级</h2><p><strong>[H] 史实</strong>：历史原始文献和可复核研究。<strong>[T] 理论</strong>：学者与理论框架的解释。<strong>[S] 模拟</strong>：声明规则下产生的模型输出。<strong>[I] 推论</strong>：作者提出的条件性历史综合判断。</p><h2>研究边界</h2><p>HSM当前模型运行至1985Q4；不得把1986—1989年当作已模拟历史。2026年10月26日核对当前主分支，H6B研究包三项complete、八项blocked、历史SUPPORTED=0。软件运行通过不等于历史校准与因果识别。</p><h2>学术引用与资料权限</h2><p>各讲参考文献和注释保持各自章节完整。部分历史文献只获研究性阅读权限，本站不转载这些第三方原件。若需学术引用，应返回原始统计表、档案或正式出版物核对页码与版本。</p><h2>出版方式</h2><p>相同28讲原稿经统一程序生成可检索HTML及XeLaTeX PDF。离线下载请使用源码包及合订版PDF；PDF封面使用原创构成主义/马赛克风格图形。</p><p><a href="index.html">返回全书目录</a></p></article>'''
page('reading.html','阅读说明',reading)
appendix_html=[]
for ap in sorted((BASE/'Appendices').glob('*.md')):
 h=subprocess.check_output(['pandoc','--from=markdown-yaml_metadata_block+footnotes+tex_math_dollars+tex_math_single_backslash','--to=html5','--mathjax',str(ap)],stderr=subprocess.DEVNULL).decode()
 appendix_html.append(h)
page('appendices.html','跨讲附录', '<article class="article">'+''.join(appendix_html)+'</article>')

# search corpus: paragraph and heading sized snippets
index=[]
for r in records:
 s=(SRC/r['filename']).read_text()
 chunks=re.split(r'\n\s*\n',s)
 for c in chunks:
  c=re.sub(r'\[([^]]+)\]\([^)]*\)',r'\1',c)
  c=re.sub(r'[#*_`|>\\$\[\]{}]',' ',c)
  c=' '.join(c.split())
  if len(c)<23:continue
  for j in range(0,len(c),420):
   seg=c[j:j+460]
   if seg: index.append({'n':r['n'],'t':r['title'],'s':seg})
(SITE/'assets'/'search.json').write_text(json.dumps(index,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
searchpage='''<article class="article"><h1>搜索二十八讲全文</h1><p>搜索标题、正文段落和主要概念（例如“科尔奈”、“投入产出”、“外债”、“软预算”）。点击结果进入对应讲次。</p><input class="search" id="search-query" placeholder="输入关键词，按 Enter" autofocus><div id="search-status" class="small"></div><div id="results" class="search-results"></div></article>'''
page('search.html','全文搜索',searchpage)
js='''const el=document.getElementById('search-query');if(el){const val=new URLSearchParams(location.search).get('q')||'';el.value=val;const clean=s=>s.normalize('NFKC').toLowerCase();fetch('assets/search.json').then(r=>r.json()).then(entries=>{function run(){const q=clean(el.value.trim());let host=document.getElementById('results'),status=document.getElementById('search-status');if(!q){status.textContent='';host.innerHTML='';return;}const terms=q.split(/\\s+/).filter(Boolean);let hits=entries.filter(e=>terms.every(t=>clean(e.s+' '+e.t).includes(t))).slice(0,85);status.textContent='找到 '+hits.length+(hits.length===85?'+':'')+' 条相关片段';host.replaceChildren(...hits.map(h=>{const d=document.createElement('div');d.className='hit';const a=document.createElement('a');a.href='lecture-'+String(h.n).padStart(2,'0')+'.html';a.textContent=h.t;const p=document.createElement('p');p.className='excerpt';p.textContent=h.s;d.append(a,p);return d;}))}el.addEventListener('input',run);run();});el.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();history.replaceState({},'',`search.html?q=${encodeURIComponent(el.value)}`)}})}document.querySelectorAll('.article a').forEach(a=>{if(a.href.startsWith('http'))a.rel='noopener noreferrer'});
'''
(SITE/'assets'/'site.js').write_text(js,encoding='utf-8')
# metadata
(BASE/'notes'/'source-manifest.json').write_text(json.dumps({'version':'2026-10-26','chapters':records,'footnote_issues':footnoteIssues},ensure_ascii=False,indent=2),encoding='utf-8')
print('Chapters:',len(records),'search blocks:',len(index),'footnote issues:',footnoteIssues)
# Five interactive, entirely browser-side, illustrative mechanisms (not actual HSM executions)
exph='''<article class="article"><div class="pill">INTERACTIVE ECONOMIC LABORATORY</div><h1>经济机制互动实验室</h1><p>以下五个实验采用<strong>有意简化、公开可见的教学方程</strong>。滑块改变的是教学参数，不是历史匈牙利、苏联或中国的测量数值，更不是 HSM 中任何机制卡的已识别系数。每个实验都给出假设、守恒/上限关系及边界。</p>
<section class="exp" id="allocation"><h2>实验一｜100吨钢如何分配？</h2><p>甲、乙两厂分别申请80和70吨钢；计划分配先受库存限制，再受总运输能力限制。改变供给、运力和分配优先级，观察实际交付。</p><div class="control"><label for="a-stock">钢材库存（吨）</label><input id="a-stock" type="range" min="30" max="180" value="100"><output id="a-stock-o"></output></div><div class="control"><label for="a-ship">当期运输能力（吨）</label><input id="a-ship" type="range" min="25" max="170" value="90"><output id="a-ship-o"></output></div><div class="control"><label for="a-priority">甲厂优先份额（%）</label><input id="a-priority" type="range" min="20" max="80" value="60"><output id="a-priority-o"></output></div><div class="bars" id="bar-alloc"></div><div class="result" id="res-alloc" aria-live="polite"></div><p class="small">计算规则：可运交付总量≤min(库存,运力,合计申请)。按甲厂优先份额分配，再将剩余额度分给仍有需求的工厂。无法在当季运走的钢不是当季已交付的钢。延伸阅读：<a href="lecture-03.html">第03讲</a>、<a href="lecture-08.html">第08讲</a>。</p></section>
<section class="exp" id="network"><h2>实验二｜能源瓶颈怎样沿生产链传播？</h2><p>假设钢铁产出每单位耗能0.4，机器每台需要1.5单位钢材和0.25单位能源；能源资源的60%优先投向炼钢，其余支持机器组装。没有跨期库存或外部进口。</p><div class="control"><label for="n-energy">能源供给（单位）</label><input id="n-energy" type="range" min="20" max="160" value="80"><output id="n-energy-o"></output></div><div class="control"><label for="n-raw">钢铁潜在能力（单位）</label><input id="n-raw" type="range" min="30" max="180" value="110"><output id="n-raw-o"></output></div><div class="bars" id="bar-network"></div><div class="result" id="res-network" aria-live="polite"></div><p class="small">钢产量=min(潜在能力,0.6×能源/0.4)；机器产量=min(70,钢产量/1.5,0.4×能源/0.25)。分配系数固定，并不表示真实企业采用了这一算法。延伸：<a href="lecture-08.html">第08讲</a>。</p></section>
<section class="exp" id="budget"><h2>实验三｜放宽信用是否必然增加真实投资？</h2><p>一家企业计划订购100单位新设备；自有现金35，信贷和救助可弥补支付缺口，但当期机器供给上限70。</p><div class="control"><label for="b-credit">可用信用额度</label><input id="b-credit" type="range" min="0" max="100" value="40"><output id="b-credit-o"></output></div><div class="control"><label for="b-bailout">财政救助额度</label><input id="b-bailout" type="range" min="0" max="100" value="10"><output id="b-bailout-o"></output></div><div class="control"><label for="b-goods">实际设备供给上限</label><input id="b-goods" type="range" min="10" max="120" value="70"><output id="b-goods-o"></output></div><div class="bars" id="bar-budget"></div><div class="result" id="res-budget" aria-live="polite"></div><p class="small">批准订购=min(100,35+信用+救助)；当期安装=min(批准订购,物量上限)。财政资金不自动创造机器。该实验只建模当期交付，不自动推导企业长期最优行为。延伸：<a href="lecture-09.html">第09讲</a>、<a href="lecture-27.html">第27讲</a>。</p></section>
<section class="exp" id="external"><h2>实验四｜外债怎样暂时维持进口？</h2><p>一个高度简化的可兑换货币结算情景：每年出口收入固定80，计划进口需求115；新贷款可弥补当年外汇差额，利息计入债务。观察五期滚动结果。</p><div class="control"><label for="e-loan">年度新增借款上限</label><input id="e-loan" type="range" min="0" max="60" value="35"><output id="e-loan-o"></output></div><div class="control"><label for="e-interest">利息（%）</label><input id="e-interest" type="range" min="0" max="20" value="7"><output id="e-interest-o"></output></div><div class="control"><label for="e-import">进口计划需求（金额）</label><input id="e-import" type="range" min="85" max="150" value="115"><output id="e-import-o"></output></div><div class="result" id="res-external" aria-live="polite"></div><div class="table-wrap"><table><thead><tr><th>期次</th><th>进口需求</th><th>实际进口</th><th>新借款</th><th>期末债务</th></tr></thead><tbody id="table-external"></tbody></table></div><p class="small">假设本息当期资本化、不还本、不存在汇率变动或贷款中断，逐期债务=(旧债+新增借款)×(1+利率)。实际进口=min(计划进口,80+新增贷款)。这里完全没有模拟真实国际金融市场的融资成本和违约风险。延伸：<a href="lecture-17.html">第17讲</a>、<a href="lecture-18.html">第18讲</a>。</p></section>
<section class="exp" id="forecast"><h2>实验五｜为什么预测更准，经济结果却不变？</h2><p>上期供给报告为130，再上期为95。简单持平预测=130；线性趋势预测=165。另设教学评估目标150，则两种方法绝对预测误差分别为20和15。采购申请受行政订单上限约束，下游配送最多85单位。</p><div class="control"><label for="f-cap">订单上限（单位）</label><input id="f-cap" type="range" min="40" max="220" value="100"><output id="f-cap-o"></output></div><div class="control"><label for="f-ship">交付能力（单位）</label><input id="f-ship" type="range" min="40" max="180" value="85"><output id="f-ship-o"></output></div><div class="bars" id="bar-forecast"></div><div class="result" id="res-forecast" aria-live="polite"></div><p class="small">申请=min(预测量,订单上限)，交付=min(申请,交付能力)。两种预测可能产生不同预测误差，但如果申请被同一个约束截断，经济结果仍可能完全一样。这一教学例子受到HSM M09的启发，但数字不是 M09 的实际输出。延伸：<a href="lecture-27.html">第27讲</a>。</p></section><p class="callout">复现方法：本页公式与参数公开在本地 <code>assets/experiments.js</code>；无服务器，所有运算在访问者浏览器内完成。不要把页面结果引用为历史因果证据。</p></article><script defer src="assets/experiments.js"></script>'''
page('experiments.html','互动机制实验室',exph)
expjs=r'''(function(){'use strict';const $=id=>document.getElementById(id);const val=id=>+$ (id).value;const fmt=x=>(Math.round(x*100)/100).toLocaleString('zh-CN',{maximumFractionDigits:2});const inp=(ids,f)=>{ids.forEach(x=>{const e=$(x);e.addEventListener('input',f);});f()};const bars=(id,entries,top)=>{$(id).replaceChildren(...entries.map(([name,num,color])=>{let col=document.createElement('div');col.className='bar-col';let number=document.createElement('span');number.textContent=fmt(num);let bar=document.createElement('div');bar.className='bar '+(color||'');bar.style.height=Math.max(2,Math.min(100,num/top*100))+'%';let lab=document.createElement('div');lab.className='bar-caption';lab.textContent=name;col.append(number,bar,lab);return col;}))};
inp(['a-stock','a-ship','a-priority'],()=>{let stock=val('a-stock'),ship=val('a-ship'),priority=val('a-priority');['a-stock','a-ship','a-priority'].forEach(x=>$(x+'-o').textContent=val(x));let all=Math.min(stock,ship,150),a=Math.min(80,all*priority/100),b=Math.min(70,all-a);a+=Math.min(80-a,all-a-b);let d=a+b;bars('bar-alloc',[['甲厂',a,''],['乙厂',b,'red'],['未满足',150-d,'gold']],150);$('res-alloc').textContent=`甲厂交付 ${fmt(a)} 吨；乙厂交付 ${fmt(b)} 吨；申请缺口 ${fmt(150-d)} 吨。实际交付不超过库存 ${stock} 吨和运力 ${ship} 吨。`});
inp(['n-energy','n-raw'],()=>{let e=val('n-energy'),r=val('n-raw');$('n-energy-o').textContent=e;$('n-raw-o').textContent=r;let s=Math.min(r,.6*e/.4),m=Math.min(70,s/1.5,.4*e/.25);bars('bar-network',[['潜在钢产',r,'gold'],['实际钢产',s,''],['机器产出',m,'red']],180);$('res-network').textContent=`实际钢产 ${fmt(s)}；机器产量 ${fmt(m)}（需求70）。炼钢分得能源 ${fmt(.6*e)}，机器阶段分得 ${fmt(.4*e)}；生产瓶颈会在下游放大。`});
inp(['b-credit','b-bailout','b-goods'],()=>{let c=val('b-credit'),b=val('b-bailout'),g=val('b-goods');['b-credit','b-bailout','b-goods'].forEach(x=>$(x+'-o').textContent=val(x));let a=Math.min(100,35+c+b),real=Math.min(a,g);bars('bar-budget',[['计划需求',100,'gold'],['订购',a,''],['实装',real,'red']],110);$('res-budget').textContent=`融资支持的订单 ${fmt(a)}；真实机器安装 ${fmt(real)}；物资交付缺口 ${fmt(a-real)}。继续放宽信用，未必能突破物量上限。`});
inp(['e-loan','e-interest','e-import'],()=>{['e-loan','e-interest','e-import'].forEach(x=>$(x+'-o').textContent=val(x)+(x==='e-interest'?'%':''));let debt=0,rows=[],sum=0,loanMax=val('e-loan'),rate=val('e-interest')/100,desired=val('e-import');for(let year=1;year<=5;year++){let borrow=Math.min(loanMax,Math.max(0,desired-80)),actual=Math.min(desired,80+borrow);debt=(debt+borrow)*(1+rate);sum+=actual;rows.push(`<tr><td>${year}</td><td>${desired}</td><td>${fmt(actual)}</td><td>${fmt(borrow)}</td><td>${fmt(debt)}</td></tr>`)}$('table-external').innerHTML=rows.join('');$('res-external').textContent=`五期累计实际进口 ${fmt(sum)}；第五期期末债务 ${fmt(debt)}。信用可以缓和当期进口约束，也在未偿付情况下积累未来支付责任。`});
inp(['f-cap','f-ship'],()=>{let cap=val('f-cap'),ship=val('f-ship');$('f-cap-o').textContent=cap;$('f-ship-o').textContent=ship;let a=Math.min(130,cap),b=Math.min(165,cap),da=Math.min(a,ship),db=Math.min(b,ship);bars('bar-forecast',[['持平预测交付',da,''],['趋势预测交付',db,'red'],['订单上限',cap,'gold']],220);$('res-forecast').textContent=`持平申请 ${fmt(a)}、交付 ${fmt(da)}；趋势申请 ${fmt(b)}、交付 ${fmt(db)}。两组交付差额 ${fmt(db-da)}。给定教学评估目标150，趋势预测误差15小于持平预测误差20；但预测改进不保证交付改进。`});})();'''
(SITE/'assets'/'experiments.js').write_text(expjs,encoding='utf-8')
print('Interactive experiments generated: 5')
