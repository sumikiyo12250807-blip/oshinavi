# -*- coding: utf-8 -*-
"""9/3の「同名既存」95件について、統合先の既存エントリを機械で特定する。

🚨判定ルール（[[project_pia_presale_caught_up]]）＝素の部分一致で畳まない。
   「既存の名前が、ぴあ公演名の"頭"に来るか」で判定する。
   （「新日本フィル」が「日本フィル」を含んでしまう事故を避けるため）
出力は3群：
  A 頭一致（自動統合の候補）
  B 含むが頭ではない（1件ずつ人が見る）
  C 一致先が複数 or 見つからない
"""
import json, re, io, unicodedata
from collections import defaultdict

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


# 既存エントリの name/artist を正規化して引けるようにする
ex = []
for e in events:
    if e.get("genre") == "new":
        continue  # 新着プールは統合先にしない
    for f in ("artist", "name"):
        v = e.get(f)
        if v:
            ex.append((norm(v), e))

cand = json.load(io.open("tmp/_triage_0903.json", encoding="utf-8"))["samename"]

A, B, C = [], [], []
for it in cand:
    k = norm(it.get("artist"))
    if not k:
        C.append((it, [])); continue
    head = [e for n, e in ex if n and k.startswith(n)]      # 既存名がぴあ名の頭に来る
    inner = [e for n, e in ex if n and n in k and not k.startswith(n)]
    ids_head = sorted(set(e.get("id") for e in head))
    ids_in = sorted(set(e.get("id") for e in inner))
    if len(ids_head) == 1:
        A.append((it, ids_head))
    elif ids_head:
        C.append((it, ids_head))
    elif ids_in:
        B.append((it, ids_in))
    else:
        C.append((it, []))

by_id = {e.get("id"): e for e in events}
buf = []
for tag, group in (("A 頭一致＝自動統合の候補", A), ("B 含むが頭でない＝人が見る", B),
                   ("C 一致先が複数/無し＝人が見る", C)):
    buf.append("=" * 74)
    buf.append("【%s】 %d件" % (tag, len(group)))
    for it, ids in group:
        names = " / ".join("id%s:%s" % (i, (by_id.get(i, {}).get("name") or "")[:34]) for i in ids)
        buf.append("  %s" % (it.get("artist") or "")[:60])
        buf.append("     公演%s %s %s | %s" % (it.get("perfdate"), it.get("pref"),
                                              it.get("venue"), it.get("saletype")))
        buf.append("     発売%s  %s" % (it.get("rlsdate"), it.get("url")))
        buf.append("     -> %s" % (names or "(統合先なし＝新規かも)"))
io.open("tmp/samename_plan_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

print("A_head_match=%d  B_inner=%d  C_ambiguous=%d  TOTAL=%d" % (len(A), len(B), len(C), len(cand)))
print("WROTE tmp/samename_plan_0904.txt")
