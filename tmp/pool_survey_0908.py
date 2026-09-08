# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の棚卸し。売り手別・ジャンル下書き別に数え、一覧を出す。"""
import io, re, json, collections

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
pool = [e for e in EV if e.get("genre") == "new"]

def vendor(e):
    lk = e.get("links", {}) or {}
    urls = [lk.get(k) or "" for k in ("pia", "eplus", "rakuten", "lawson")]
    urls += [(t.get("url") or "") for t in (e.get("tickets") or [])]
    blob = " ".join(urls)
    if "eplus.jp" in blob: return "e+"
    if "t.pia.jp" in blob: return "ぴあ"
    if "rakuten" in blob: return "楽天"
    if "l-tike" in blob or "lawson" in blob: return "ローチケ"
    return "不明"

cnt = collections.Counter(vendor(e) for e in pool)
gcnt = collections.Counter((vendor(e), e.get("_genre") or "(下書き無し)") for e in pool)

o = io.open("tmp/pool_survey_0908.md", "w", encoding="utf-8")
W = o.write
W("# 新着プールの棚卸し（2026-09-08）\n\n")
W("- プール全体＝**%d件**\n" % len(pool))
for k, v in cnt.most_common():
    W("  - %s … %d件\n" % (k, v))

W("\n## ジャンル下書き(_genre)の内訳\n\n| 売り手 | 下書きジャンル | 件数 |\n|---|---|---|\n")
for (vd, g), n in sorted(gcnt.items()):
    W("| %s | %s | %d |\n" % (vd, g, n))

W("\n## ぴあ由来の一覧（振り分け候補）\n\n")
W("| id | 公演名 | 会場 | 公演日 | 下書き | 枠 |\n|---|---|---|---|---|---|\n")
for e in sorted([x for x in pool if vendor(x) == "ぴあ"], key=lambda x: x["id"]):
    W("| %d | %s | %s | %s | **%s** | %d |\n" % (
        e["id"],
        (e.get("title") or "").replace("|", "｜")[:38],
        (e.get("venue") or "").replace("|", "｜")[:26],
        e.get("date") or "",
        e.get("_genre") or "(無し)",
        len(e.get("tickets") or [])))

W("\n## ぴあ以外の一覧（ユーザー確認待ち＝振り分けない）\n\n")
W("| id | 売り手 | 公演名 | 公演日 | 下書き |\n|---|---|---|---|---|\n")
for e in sorted([x for x in pool if vendor(x) != "ぴあ"], key=lambda x: x["id"]):
    W("| %d | %s | %s | %s | %s |\n" % (
        e["id"], vendor(e),
        (e.get("title") or "").replace("|", "｜")[:38],
        e.get("date") or "", e.get("_genre") or "(無し)"))
o.close()
print("wrote tmp/pool_survey_0908.md  pool=%d  %s" % (len(pool), dict(cnt)))
