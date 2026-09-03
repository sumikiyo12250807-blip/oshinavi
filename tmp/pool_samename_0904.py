# -*- coding: utf-8 -*-
"""新着プール69件が既存エントリと同名でないかを確かめる（振り分け前の必須チェック）。
🚨2026-08-18に「50件のうち39件が既存と同名＝ツアー分裂」だった前例がある。

判定は「既存の名前が、プールの名前の頭に来るか」＝素の部分一致で畳まない
（[[project_pia_presale_caught_up]]の「新日本フィル」事故を避ける）。"""
import json, re, io, unicodedata

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


pool = [e for e in events if e.get("genre") == "new"]
others = [e for e in events if e.get("genre") != "new"]
ex = []
for e in others:
    for f in ("artist", "name"):
        if e.get(f):
            ex.append((norm(e[f]), e))

hits, clean = [], []
for p in pool:
    k = norm(p.get("name") or p.get("artist"))
    if not k:
        clean.append((p, [])); continue
    cand = [e for n, e in ex if n and k.startswith(n)]
    ids = sorted(set(e.get("id") for e in cand))
    (hits if ids else clean).append((p, ids))

by_id = {e.get("id"): e for e in events}
buf = []
buf.append("【既存と同名＝統合を検討】 %d件" % len(hits))
for p, ids in hits:
    buf.append("  new id=%-5s %s" % (p.get("id"), (p.get("name") or "")[:50]))
    buf.append("       %s / %s" % (p.get("dateLabel", "")[:44], p.get("venue", "")))
    for i in ids:
        e = by_id[i]
        buf.append("    -> 既存 id=%-5s %s [%s] %s" % (
            i, (e.get("name") or "")[:40], e.get("genre"), e.get("dateLabel", "")[:34]))
buf.append("")
buf.append("【同名なし＝そのまま振り分けてよい】 %d件" % len(clean))
for p, _ in clean:
    buf.append("  id=%-5s [%s] %s" % (p.get("id"), p.get("_genre"), (p.get("name") or "")[:50]))
io.open("tmp/pool_samename_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

print("POOL=%d  SAMENAME=%d  CLEAN=%d" % (len(pool), len(hits), len(clean)))
print("SAMENAME_IDS=" + ",".join(str(p.get("id")) for p, _ in hits))
