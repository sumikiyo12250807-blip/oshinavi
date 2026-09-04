# -*- coding: utf-8 -*-
"""残り46件を「なぜ取り込めていないか」で分ける。

  A 同じ公演の枠は既に載っている（券種違い・まとめページ違いでURLだけ未登録）
    → C型（個別ページ vs まとめページ）の方針が決まれば一気に片付く型
  B 既存が複数エントリに分裂していて、どれに足すか決まらない
  C それ以外（本当に未取り込み）
"""
import json, re, io, unicodedata

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
ex_cds = set(re.findall(r"event(?:Bundle)?Cd=(\w+)", html))
tri = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))


def cd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


ex = []
for e in events:
    for f in ("artist", "name"):
        if e.get(f):
            ex.append((norm(e[f]), e))

A, B, C = [], [], []
for k in ("fresh", "samename", "today", "unknown"):
    for it in tri[k]:
        if cd(it.get("url")) in ex_cds:
            continue
        key = norm(it.get("artist"))
        hits = [e for n, e in ex if n and key.startswith(n)]
        ids = sorted(set(e.get("id") for e in hits))
        if len(ids) == 1:
            A.append((k, it, ids[0]))
        elif len(ids) > 1:
            B.append((k, it, ids))
        else:
            C.append((k, it, []))

buf = []
for tag, g in (("A 統合先は1つに決まる（枠が既にあってURLだけ未登録＝C型と同じ話）", A),
               ("B 既存が複数に分裂＝どれに足すか決まらない", B),
               ("C 統合先が無い＝本当に未取り込み", C)):
    buf.append("=" * 70)
    buf.append("【%s】 %d件" % (tag, len(g)))
    for k, it, ids in g:
        buf.append("  [%s] %s" % (k, (it.get("artist") or "")[:52]))
        buf.append("      %s %s / 発売%s -> %s" % (it.get("pref"), it.get("venue"),
                                                   it.get("rlsdate"), ids))
        buf.append("      %s" % it.get("url"))
io.open("tmp/rest_kind_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("A_url_only=%d  B_split=%d  C_really_new=%d  TOTAL=%d" % (len(A), len(B), len(C), len(A) + len(B) + len(C)))
