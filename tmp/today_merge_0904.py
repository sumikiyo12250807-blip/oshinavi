# -*- coding: utf-8 -*-
"""本日発売ぶんのうち「既存と同名」で投入を見送った12件について、統合先を特定して候補を作る。
判定は「既存の名前がぴあ公演名の頭に来るか」。統合先が1つに決まらないものは保留に回す。"""
import json, io, re, unicodedata
from collections import defaultdict

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


ex = []
for e in events:
    for f in ("artist", "name"):
        if e.get(f):
            ex.append((norm(e[f]), e))

items = json.load(io.open("tmp/today_skipname_0904.json", encoding="utf-8"))
ex_cds = set(re.findall(r"event(?:Bundle)?Cd=(\w+)", html))


def cd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


ok, hold = [], []
for it in items:
    if cd(it.get("url")) in ex_cds:
        continue
    k = norm(it.get("artist"))
    hits = [e for n, e in ex if n and k.startswith(n)]
    ids = sorted(set(e.get("id") for e in hits))
    if len(ids) == 1:
        ok.append((it, ids[0]))
    else:
        hold.append((it, ids))

by_id = {e.get("id"): e for e in events}
buf = ["【統合する】%d件" % len(ok)]
for it, i in ok:
    buf.append("  %s -> id%s %s" % ((it.get("artist") or "")[:44], i, (by_id[i].get("name") or "")[:34]))
    buf.append("     %s" % it.get("url"))
buf.append("")
buf.append("【統合先が決まらない＝保留】%d件" % len(hold))
for it, ids in hold:
    buf.append("  %s -> %s" % ((it.get("artist") or "")[:44], ids))
    buf.append("     %s" % it.get("url"))
io.open("tmp/today_merge_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

seq = defaultdict(int)
cand = []
for it, i in ok:
    seq[i] += 1
    cand.append({"newid": 930000 + i * 10 + seq[i], "artist": it.get("artist", ""),
                 "urls": [it["url"]], "_merge_into": i})
json.dump(cand, io.open("tmp/today_merge_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump([it for it, _ in hold], io.open("tmp/today_merge_hold_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("ITEMS=%d  統合する=%d  保留=%d" % (len(items), len(ok), len(hold)))
