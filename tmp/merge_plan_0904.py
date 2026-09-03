# -*- coding: utf-8 -*-
"""統合候補11件について、新着側と既存側の枠を並べて突合し、
「既存に無い枠だけを足す」統合案を作る（実行はしない・案の書き出しのみ）。"""
import json, re, io

PAIRS = [(6406, 4279), (6407, 3551), (6413, 2121), (6417, 2239), (6418, 450),
         (6432, 2362), (6436, 4223), (6438, 309), (6444, 2471), (6450, 4843),
         (6456, 4291)]

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}
# 新側は未投入＝_merge_pending_0903.json の中にだけある
pend = json.load(io.open("tmp/_merge_pending_0903.json", encoding="utf-8"))
new_by_id = {e.get("id"): e for e in pend}


def key(t):
    """枠の同一判定キー＝券種名(日付部分を落とす)＋受付終了日＋飛び先url"""
    ty = re.sub(r"\d{1,2}/\d{1,2}", "#", t.get("type", ""))
    ty = re.sub(r"\d{1,2}:\d{2}", "#", ty)
    return (ty, t.get("date"), t.get("url") or "")


buf = []
summary = []
for new_id, old_id in PAIRS:
    ne, oe = new_by_id.get(new_id), by_id.get(old_id)
    buf.append("=" * 74)
    if not ne or not oe:
        buf.append("id=%s -> %s : 片方が見つからない (new=%s old=%s)" % (
            new_id, old_id, bool(ne), bool(oe)))
        summary.append((new_id, old_id, -1, -1))
        continue
    buf.append("新 id=%s %s" % (new_id, ne.get("name")))
    buf.append("   %s / %s / %s" % (ne.get("dateLabel"), ne.get("venue"), ne.get("prefecture")))
    buf.append("旧 id=%s %s  [genre=%s]" % (old_id, oe.get("name"), oe.get("genre")))
    buf.append("   %s / %s / %s" % (oe.get("dateLabel"), oe.get("venue"), oe.get("prefecture")))
    oldkeys = set(key(t) for t in oe.get("tickets", []))
    add, dup = [], []
    for t in ne.get("tickets", []):
        (add if key(t) not in oldkeys else dup).append(t)
    buf.append("  旧の枠数=%d / 新の枠数=%d -> 足す枠=%d  既にある枠=%d" % (
        len(oe.get("tickets", [])), len(ne.get("tickets", [])), len(add), len(dup)))
    for t in add:
        buf.append("   ＋足す: %s | 〜%s | %s" % (t.get("type"), t.get("date"), (t.get("url") or "(url無)")[:88]))
    for t in dup:
        buf.append("   ＝既存: %s | 〜%s" % (t.get("type"), t.get("date")))
    buf.append("  旧の既存枠:")
    for t in oe.get("tickets", []):
        buf.append("     %s | 〜%s | %s" % (t.get("type"), t.get("date"), (t.get("url") or "(url無)")[:88]))
    summary.append((new_id, old_id, len(add), len(dup)))

io.open("tmp/merge_plan_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("WROTE tmp/merge_plan_0904.txt")
for a, b, add, dup in summary:
    print("new=%-5s old=%-5s add=%-3s already=%s" % (a, b, add, dup))
