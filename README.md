# 我的图书馆

与 AI 共建的个人学习页面库。按模块收纳 HTML 学习页，Mac 与手机随时打开、可离线看。
线上地址：https://zhengshell-coder.github.io/study-wiki/

## 目录结构

```
├── index.html          # 书架首页（继续阅读 / 书目 / 搜索 / 批注 / 设置）
├── reader.html         # 阅读器（进度、书签、批注、搜索词定位）
├── catalog.json        # 目录数据（模块、页面列表）—— 唯一数据源
├── search-index.json   # 全文索引（由 Actions 自动重建，勿手改）
├── reading.json        # 阅读进度 / 书签 / 批注的同步文件
├── sw.js  manifest.webmanifest  icon-*.png   # PWA 与离线
├── scripts/build_index.py                    # 目录校验 + 重建索引
├── .github/workflows/index.yml               # 推送后自动跑上面的脚本
└── AI-技术/ 历史/ 中医/ …                    # 各模块文件夹，放对应 HTML
```

## 使用

- **只读**：直接打开网址即可，无需任何令牌。
- **上传 / 更新 / 删除**：在「设置」里填一次 GitHub 令牌（仅存本机），之后在页面上传书，会自动提交到本仓库；全文索引由 GitHub Actions 自动重建。
- **本地校验**：`python3 scripts/build_index.py --check`（目录里有但文件不存在时报错；文件未收入目录时提示）。

## 托管

GitHub Pages（公开）。内容公开可读，请勿放入需要保密的材料。

## 备份

「设置」里可导出 catalog.json、打包下载全部书籍；也可直接复制整个仓库。
