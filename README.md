# 《计划经济的运行、改革与历史命运》出版工程

本目录收录**七编二十八讲**完整原稿、非破坏性编校稿、XeLaTeX学术排版版PDF、构成主义与马赛克混合风格原创封面、可搜索静态网站，以及五项独立于HSM的教学互动实验。

## 本次交付的边界

- **28讲原稿全部保留**：`manuscripts/Lecture_01...28.md`。原稿提供在网页 `site/source/` 下。
- `edited/` 由`tools/build.py`从原稿生成，只调整易使Pandoc误识别的Markdown分隔线及空行；不改变历史断言、数值、学术争论或机制卡判定。
- `latex/book.md`是统一合订稿，章节内脚注ID已加讲次前缀避免跨讲冲突，按编插入Part页，后接全书术语、年表、工具箱与HSM证据索引。
- `latex/book.tex`是Pandoc产生的可审阅XeLaTeX成书源文件；`latex/layout.tex`规定开本、字体、行距与页眉。PDF生成时只使用本机已装的字体，不分发任何字体文件。
- `site/`是完整可部署的静态网站，无需服务端执行Python，五项互动计算在浏览器中完成。教材**没有声称**网站教学实验等于HSM历史校准或模拟结果。
- **仓库权属与网站公开发布**：本站仅包括提供的原创讲义与生成的教学素材，不包含HSM被忽略的outputs、个人私有原始史料或受限OCR。

## 本地构建（需要Pandoc，构建PDF另需完整XeLaTeX/Noto CJK）

```bash
python3 tools/build.py
bash tools/build_pdf.sh
python3 -m http.server 8000 --directory site
```

网站本地地址：`http://localhost:8000`。

## 在新建GitHub仓库部署GitHub Pages

此交付包适合导入**独立的公开 GitHub 仓库**，建议名称`planned-economy-lectures`。导入本包目录（包含以点开头的 `.github/`）并推送到 `main`；在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。仓库中的 `.github/workflows/pages.yml` 将使用Pandoc从28份Markdown重建网站并上传 `site/`，之后每次更新 `main` 会触发同样工作流。GitHub Pages发布的实际URL以 GitHub 工作流输出为准，不能提前当作已经上线。

**GitHub连接器目前没有“创建新仓库”的写入接口**。为遵守“单独建教材仓库、不影响HSM科研主线”的既定方案，本交付包没有修改`hungary-socialist-mechanism-lab/main`，也没有将研究仓库改造成站点仓库。

## 文件结构

```text
Planned_Economy_Lectures/
├── manuscripts/                 原始28份 Markdown（不可覆盖的编辑底稿）
├── edited/                      自动规范化的编校副本
├── Appendices/                  术语、人物、年表、工具箱、HSM证据索引
├── latex/book.md                统一合订稿
├── latex/book.tex               XeLaTeX成书源文件
├── latex/layout.tex             版式规范
├── pdf/                          成品PDF
├── assets/cover.png             全尺寸封面图
├── assets/cover-web.jpg         轻量网页封面
├── site/                         GitHub Pages成品HTML、脚本、互动实验
├── tools/build.py                Markdown → HTML / 合订稿
├── tools/build_pdf.sh            XeLaTeX PDF生成脚本
├── notes/source-manifest.json    逐讲SHA和脚注检查
└── .github/workflows/pages.yml   GitHub Pages自动发布
```

## 排版体系

- 版心：170 × 240 mm，正文名义11pt，行距1.39；不使用过度紧凑的正文行距。
- 中文字体：Noto Serif CJK SC，章节标题及页眉结合Noto Sans CJK SC。
- 英文正文：Liberation Serif；表格与代码使用相应无衬线／等宽字体。
- 封面：原创程序化绘制的构成主义×马赛克工业图形，低饱和蓝灰、砖红、米色。封面图可在网站和PDF复用。
- 如欲换成精装印刷版，建议单独处理出血、脊背、CMYK色彩及索引页。

## 学术证据底线

HSM研究仓库当前H6B报告为 **11张机制卡中3张研究包complete、8张blocked、历史SUPPORTED=0**；P06存在消费指数严重复现失配。模型可重放≠历史拟合≠参数识别；请参阅书内第25—28讲及附录D。HSM研究仓库：https://github.com/swjn2017USTC/hungary-socialist-mechanism-lab

**注意**：GitHub Actions 每次提交会重新构建HTML网站；PDF为经过独立排版审查的发行物，只有执行 `bash tools/build_pdf.sh` 并提交新PDF文件后才会同步更新。不要默认为每次更新正文后PDF已自动刷新。
