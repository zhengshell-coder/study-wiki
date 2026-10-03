# 我的图书馆

与 AI 共建的个人学习页面库。按模块收纳 HTML 学习页，Mac 与手机随时打开、可离线看。
线上地址：https://zhengshell-coder.github.io/study-wiki/

## 目录结构

```
├── index.html          # 书架首页（继续阅读 / 书目 / 搜索 / 批注 / 设置）
├── reader.html         # 阅读器（进度、书签、批注、搜索词定位）
├── catalog.json        # 目录（由文件夹结构自动生成；简介/标签可手改，会被保留）
├── search-index.json   # 全文索引（自动生成，勿手改）
├── reading.json        # 阅读进度 / 书签 / 批注的同步文件
├── sw.js  manifest.webmanifest  icon-*.png   # PWA 与离线
├── scripts/build_library.py                  # 文件夹 → 目录 + 全文索引
├── .github/workflows/index.yml               # 推送后自动跑上面的脚本
└── AI-技术/ 历史/ 中医/ …                    # 各模块文件夹，放对应 HTML
```

## 使用（文件夹就是真相）

- **存书 / 挪书 / 删书**：在 Mac 上直接放、挪、删 HTML 文件（或对 Claude 说「存进图书馆，放历史」，用 `library-add` skill），推送后 GitHub Actions 自动更新目录、索引、并迁移阅读记录。
- **网页上整理**：书架里进入分类 → 右上角「整理」→ 勾选 → 移动 / 下载 / 删除（需要令牌）。

- **只读**：直接打开网址即可，无需任何令牌。
- **网页上传**：「设置 → GitHub 令牌」填一次（仅存本机），之后可在页面上传书。不填也不影响阅读。
- **本地生成 / 检查**：`python3 scripts/build_library.py [--check]`。

## 托管

GitHub Pages（公开）。内容公开可读，请勿放入需要保密的材料。

## 备份

「设置」里可导出 catalog.json、打包下载全部书籍；也可直接复制整个仓库。
