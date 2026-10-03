#!/usr/bin/env python3
"""文件夹就是真相：根据文件夹结构生成 catalog.json，并重建 search-index.json。

规则
- 顶层每个含 .html 的文件夹 = 一个分类；里面的 .html = 一本书。
- 已登记的书保留 id / 简介 / 标签 / 日期；新文件自动登记（书名取 <title>，简介取 meta description）。
- 文件换了文件夹（同名文件）= 移动：保留所有信息，并把 reading.json 里的进度/书签/批注一起迁过去。
- 文件不在了 = 从目录移除。已有分类即使暂时没书也保留。

用法：python3 scripts/build_library.py [--check]   （--check 只检查不写文件，有问题退出码为 1）
"""
import json, os, re, sys, time, random, string
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {"scripts", "app", "icons", "node_modules"}
TEXT_SKIP = {"script", "style", "noscript", "svg", "template"}
ICONS = {"历史": "🏛️", "文学": "📖", "政治": "⚖️", "经济": "📈", "哲学": "🧠", "宗教": "📿", "数学": "➗",
         "科技": "🔬", "中医": "🌿", "工作总结": "📝", "AI-技术": "🤖", "AI-芯片硬件": "🔌", "AI-商业趋势": "📊"}

def uid():
    return format(int(time.time() * 1000), "x")[-7:] + "".join(random.choices(string.ascii_lowercase + string.digits, k=5))

class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.depth, self.title, self.in_title, self.meta = [], 0, "", False, ""
    def handle_starttag(self, tag, a):
        if tag in TEXT_SKIP: self.depth += 1
        if tag == "title": self.in_title = True
        if tag == "meta":
            d = dict(a)
            if (d.get("name") or "").lower() == "description" and not self.meta: self.meta = (d.get("content") or "").strip()
    def handle_endtag(self, tag):
        if tag in TEXT_SKIP and self.depth: self.depth -= 1
        if tag == "title": self.in_title = False
    def handle_data(self, d):
        if self.in_title: self.title += d
        elif not self.depth: self.out.append(d)

def parse(path):
    p = Page(); p.feed(open(path, encoding="utf-8", errors="replace").read())
    return re.sub(r"\s+", " ", "".join(p.out)).strip()[:40000], re.sub(r"\s+", " ", p.title).strip(), p.meta

def main():
    check = "--check" in sys.argv
    cat_path = os.path.join(ROOT, "catalog.json")
    cat = json.load(open(cat_path, encoding="utf-8")) if os.path.exists(cat_path) else {"modules": [], "pages": []}
    mods = cat["modules"]; by_folder = {m["folder"]: m for m in mods}; mid = {m["id"]: m for m in mods}
    notes = []

    # 1. 扫描磁盘
    disk = {}  # "folder/file" -> (folder, file)
    for d in sorted(os.listdir(ROOT)):
        full = os.path.join(ROOT, d)
        if d.startswith(".") or d in SKIP_DIRS or not os.path.isdir(full): continue
        for f in sorted(os.listdir(full)):
            if f.lower().endswith((".html", ".htm")): disk[d + "/" + f] = (d, f)
    for d in sorted({v[0] for v in disk.values()}):
        if d not in by_folder:
            m = {"id": uid(), "name": d, "folder": d, "icon": ICONS.get(d, "📁"), "color": "#8A8378"}
            mods.append(m); by_folder[d] = m; mid[m["id"]] = m; notes.append("新分类：" + d)

    # 2. 对账
    key_of = lambda p: (mid[p["moduleId"]]["folder"] + "/" + p["file"]) if p["moduleId"] in mid else None
    kept, lost = [], []
    for p in cat["pages"]:
        (kept if key_of(p) in disk else lost).append(p)
    claimed = {key_of(p) for p in kept}
    fresh = [k for k in disk if k not in claimed]
    moves = {}
    for p in list(lost):
        cand = [k for k in fresh if disk[k][1] == p["file"]]
        if len(cand) == 1:
            old = key_of(p) or ("?/" + p["file"]); new = cand[0]
            p["moduleId"] = by_folder[disk[new][0]]["id"]; moves[old] = new
            kept.append(p); fresh.remove(new); lost.remove(p); notes.append("移动：%s → %s" % (old, new))
    for p in lost: notes.append("移除（文件已不存在）：%s" % (key_of(p) or p["file"]))
    for k in fresh:
        folder, f = disk[k]; _, title, meta = parse(os.path.join(ROOT, k))
        kept.append({"id": uid(), "moduleId": by_folder[folder]["id"], "title": title or re.sub(r"\.html?$", "", f, flags=re.I),
                     "file": f, "desc": meta[:120], "tags": [], "date": time.strftime("%Y-%m-%d"), "rev": int(time.time() * 1000)})
        notes.append("新书：" + k)
    new_cat = {"modules": mods, "pages": kept}

    # 3. 迁移阅读记录
    rd_path = os.path.join(ROOT, "reading.json"); new_rd = None
    if moves and os.path.exists(rd_path):
        rd = json.load(open(rd_path, encoding="utf-8")); n = 0
        for sect in ("positions", "bookmarks", "notes"):
            o = rd.get(sect) or {}
            for old, new in moves.items():
                if old in o: o[new] = o.pop(old); n += 1
        if n: new_rd = json.dumps(rd, ensure_ascii=False, separators=(",", ":")); notes.append("迁移阅读记录 %d 条" % n)

    # 4. 索引
    idx_path = os.path.join(ROOT, "search-index.json")
    old_idx = json.load(open(idx_path, encoding="utf-8")).get("docs", {}) if os.path.exists(idx_path) else {}
    docs = {}
    for p in kept:
        k = mid[p["moduleId"]]["folder"] + "/" + p["file"]; full = os.path.join(ROOT, k)
        t = parse(full)[0]; prev = old_idx.get(p["id"])
        docs[p["id"]] = prev if prev and prev.get("t") == t else {"t": t, "at": int(os.path.getmtime(full) * 1000)}

    for n in notes: print(n)
    if check: sys.exit(0)
    def write(path, text):
        cur = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if cur is None or cur.strip() != text.strip():
            open(path, "w", encoding="utf-8").write(text); print("已更新", os.path.basename(path)); return True
        return False
    write(cat_path, json.dumps(new_cat, ensure_ascii=False, indent=2))
    if new_rd: write(rd_path, new_rd)
    write(idx_path, json.dumps({"v": 1, "docs": docs}, ensure_ascii=False, separators=(",", ":")))
    print("完成：%d 类 / %d 本" % (len(mods), len(kept)))

main()
