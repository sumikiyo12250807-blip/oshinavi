# -*- coding: utf-8 -*-
"""今朝の samename 117件について、統合先の既存エントリを機械で特定して build 候補を作る。

判定は「既存の名前が、ぴあ公演名の頭に来るか」。
🚨誤マッチ検算＝ぴあ名から既存名を取り除いた"残り"が空でなく、かつ既存名が短いものは要確認に回す
   （既存「yama」が「YAMATO String Quartet」に刺さる型）。
"""
import json, re, io, unicodedata
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

cand = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))["samename"]
ex_cds = set(re.findall(r"event(?:Bundle)?Cd=(\w+)", html))


def cd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


ok, risky, ambig, already = [], [], [], []
for it in cand:
    if cd(it.get("url")) in ex_cds:
        already.append(it); continue
    k = norm(it.get("artist"))
    if not k:
        ambig.append((it, [])); continue
    hits = [(n, e) for n, e in ex if n and k.startswith(n)]
    ids = sorted(set(e.get("id") for _, e in hits))
    if len(ids) != 1:
        ambig.append((it, ids)); continue
    n, e = max(hits, key=lambda x: len(x[0]))
    rest = k[len(n):]
    if rest and (len(n) <= 4 or len(rest) >= len(n)):
        risky.append((it, ids[0], n, rest))
    else:
        ok.append((it, ids[0]))

by_id = {e.get("id"): e for e in events}
buf = []
buf.append("【自動統合してよい】%d件" % len(ok))
for it, i in ok:
    buf.append("  %s -> id%s %s" % ((it.get("artist") or "")[:44], i, (by_id[i].get("name") or "")[:34]))
    buf.append("     %s / 発売%s / %s" % (it.get("url"), it.get("rlsdate"), it.get("pref")))
buf.append("")
buf.append("【要確認（名前が短い・残りが長い）】%d件" % len(risky))
for it, i, n, rest in risky:
    buf.append("  %s -> id%s 「%s」 残り「%s」" % ((it.get("artist") or "")[:44], i, n, rest))
    buf.append("     %s" % it.get("url"))
buf.append("")
buf.append("【統合先が複数/不明】%d件" % len(ambig))
for it, ids in ambig:
    buf.append("  %s -> %s" % ((it.get("artist") or "")[:44], ids))
    buf.append("     %s" % it.get("url"))
buf.append("")
buf.append("【eventCdが既に登録済み＝何もしない】%d件" % len(already))
io.open("tmp/samename2_plan_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

seq = defaultdict(int)
out = []
for it, i in ok:
    seq[i] += 1
    out.append({"newid": 920000 + i * 10 + seq[i], "artist": it.get("artist", ""),
                "urls": [it["url"]], "_merge_into": i})
json.dump(out, io.open("tmp/samename2_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("SAMENAME=%d" % len(cand))
print("  自動統合=%d（統合先 %dエントリ）" % (len(ok), len(set(i for _, i in ok))))
print("  要確認=%d  統合先が複数/不明=%d  eventCd登録済み=%d" % (len(risky), len(ambig), len(already)))
