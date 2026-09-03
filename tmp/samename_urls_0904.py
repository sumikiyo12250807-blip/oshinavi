# -*- coding: utf-8 -*-
"""統合対象90件を「既存エントリごと」にまとめて、build に渡すURLリストを作る。
🚨build_pia_entries は複数URLを渡すと2本目以降の ticket.url が落ちる
   （[[feedback_build_pia_multiurl_loses_ticket_url]]）ので、**1URLずつ回す**前提で並べる。"""
import json, re, io, unicodedata
from collections import defaultdict

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


ex = []
for e in events:
    if e.get("genre") == "new":
        continue
    for f in ("artist", "name"):
        if e.get(f):
            ex.append((norm(e[f]), e))

cand = json.load(io.open("tmp/_triage_0903.json", encoding="utf-8"))["samename"]
groups = defaultdict(list)
for it in cand:
    k = norm(it.get("artist"))
    if not k:
        continue
    hits = [e for n, e in ex if n and k.startswith(n)]
    ids = sorted(set(e.get("id") for e in hits))
    if len(ids) == 1:
        groups[ids[0]].append(it)

by_id = {e.get("id"): e for e in events}
buf, urls = [], []
for eid in sorted(groups):
    e = by_id[eid]
    items = groups[eid]
    buf.append("id=%s %s  [genre=%s] 既存枠%d ← 足す候補%d件" % (
        eid, e.get("name"), e.get("genre"), len(e.get("tickets", [])), len(items)))
    for it in items:
        buf.append("    %s %s %s | 発売%s" % (it.get("perfdate"), it.get("pref"),
                                             it.get("venue"), it.get("rlsdate")))
        buf.append("    %s" % it.get("url"))
        urls.append("%s\t%s" % (eid, it.get("url")))

io.open("tmp/samename_groups_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
io.open("tmp/samename_urls_0904.tsv", "w", encoding="utf-8").write("\n".join(urls))
print("TARGET_ENTRIES=%d  URLS=%d" % (len(groups), len(urls)))
print("WROTE tmp/samename_groups_0904.txt / tmp/samename_urls_0904.tsv")
