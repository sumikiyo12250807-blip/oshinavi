# -*- coding: utf-8 -*-
"""新着プールに残した子を、確認用の直URL付きで一覧にする（2026-08-05夜・ユーザー「明日リンクと一緒に見せて」）。

URLは登録データから機械で抜くだけ＝**組み立てや推測をしない**（[[feedback_delete_candidates_with_url]]
の「検索ワードでなく確認用の直URLを貼る」と同じ流儀）。
なぜプールに残っているのかの理由も添える。
"""
import datetime
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"

h = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
EVENTS = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", h, re.S).group(1))
pool = sorted([e for e in EVENTS if e.get("genre") == "new"], key=lambda x: x["id"])

MANUAL = {3676: "引換場所のラベルをぴあの並び順から推定して付けた＝根拠が推定",
          3801: "ジャンルが kaidan か owarai か相談中"}

out = ["# 新着プール 残置%d件 チェックリスト（%s 時点）" % (len(pool), datetime.date.today()), ""]
for e in pool:
    L = e.get("links") or {}
    why = []
    if not L.get("pia"):
        why.append("ぴあリンク無し＝機械照合が効かない")
    dup = Counter((t.get("date"), t.get("startDate")) for t in (e.get("tickets") or []))
    if any(v > 1 for v in dup.values()):
        why.append("同じ締切の枠が複数＝reconcileが照合できない枠を含む")
    if e["id"] in MANUAL:
        why.append(MANUAL[e["id"]])

    out.append("## id%d %s" % (e["id"], e.get("artist")))
    out.append("- 残した理由: %s" % " ／ ".join(why))
    out.append("- %s ／ %s ／ %s" % (e.get("dateLabel"), e.get("venue"), e.get("prefecture")))
    out.append("- 下書きジャンル: %s%s" % (
        e.get("_genre"), "＋" + ",".join(e.get("_extraGenres") or []) if e.get("_extraGenres") else ""))
    for t in e.get("tickets") or []:
        out.append("  - %s（〆 %s%s）" % (t.get("type"), t.get("date"),
                                        " ／ 発売 " + t["startDate"] if t.get("startDate") else ""))
    for k, label in (("pia", "ぴあ"), ("eplus", "e+"), ("rakuten", "楽天"), ("lawson", "ローチケ")):
        if L.get(k):
            out.append("- %s: %s" % (label, L[k]))
    # 枠ごとに別URLがある場合も全部出す（ここを省くと確認できない枠が出る）
    tu = [t["url"] for t in (e.get("tickets") or []) if t.get("url")]
    for u in dict.fromkeys(tu):
        out.append("- 枠別URL: %s" % u)
    out.append("")

p = os.path.join(ROOT, "tmp", "newpool_review_list.md")
io.open(p, "w", encoding="utf-8").write("\n".join(out))
print("→ %s（%d件）" % (p, len(pool)))
