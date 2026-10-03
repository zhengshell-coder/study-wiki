#!/usr/bin/env python3
"""校验 catalog.json 并重建 search-index.json（与前端 htmlToText 同口径：去 script/style/svg 等，空白折叠，截 4 万字）。
正文没变的书保留原 at，避免无意义的提交。用法：python3 scripts/build_index.py [--check]"""
import json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"script", "style", "noscript", "svg", "template"}

class T(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.out = []; self.depth = 0
    def handle_starttag(self, tag, a):
        if tag in SKIP: self.depth += 1
    def handle_endtag(self, tag):
        if tag in SKIP and self.depth: self.depth -= 1
    def handle_data(self, d):
        if not self.depth: self.out.append(d)

def text_of(path):
    p = T(); p.feed(open(path, encoding="utf-8", errors="replace").read())
    return re.sub(r"\s+", " ", "".join(p.out)).strip()[:40000]

def main():
    cat = json.load(open(os.path.join(ROOT, "catalog.json"), encoding="utf-8"))
    mods = {m["id"]: m for m in cat["modules"]}
    idx_path = os.path.join(ROOT, "search-index.json")
    old = json.load(open(idx_path, encoding="utf-8")).get("docs", {}) if os.path.exists(idx_path) else {}
    docs, listed, errors = {}, set(), []
    for p in cat["pages"]:
        m = mods.get(p["moduleId"])
        if not m: errors.append("页面《%s》指向不存在的模块 %s" % (p["title"], p["moduleId"])); continue
        rel = m["folder"] + "/" + p["file"]; listed.add(rel); full = os.path.join(ROOT, rel)
        if not os.path.exists(full): errors.append("目录里有但文件不存在：" + rel); continue
        t = text_of(full); prev = old.get(p["id"])
        docs[p["id"]] = prev if prev and prev.get("t") == t else {"t": t, "at": int(os.path.getmtime(full) * 1000)}
    for m in cat["modules"]:
        d = os.path.join(ROOT, m["folder"])
        for f in (os.listdir(d) if os.path.isdir(d) else []):
            if f.lower().endswith((".html", ".htm")) and m["folder"] + "/" + f not in listed:
                print("提示：文件未收入目录：%s/%s" % (m["folder"], f))
    for e in errors: print("错误：" + e)
    if "--check" in sys.argv: sys.exit(1 if errors else 0)
    new = json.dumps({"v": 1, "docs": docs}, ensure_ascii=False, separators=(",", ":"))
    cur = open(idx_path, encoding="utf-8").read() if os.path.exists(idx_path) else ""
    if cur.strip() != new:
        open(idx_path, "w", encoding="utf-8").write(new); print("search-index.json 已更新（%d 本）" % len(docs))
    else: print("search-index.json 无变化（%d 本）" % len(docs))
    sys.exit(0)

main()
