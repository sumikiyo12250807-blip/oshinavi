# -*- coding: utf-8 -*-
"""楽天チケットの「隠れ枠」を走査する（ぴあの heal_stale_deadlines の楽天版・第一歩）。

🚨なぜ要るか＝ぴあの隠れ枠ヒールは**ぴあ専用**。楽天の枠で
   `startDate == date`（＝「M/D発売」の単日形。締切がまだ取り込めていない）を作ると、
   **発売日の翌日から画面に出なくなる**のに、直す道具が1つも無い
   （[[reference_rakuten_harvest]] / [[feedback_delete_nonpia_blindspot]]）。

まずは「どれだけあるか」を数える。走査だけで、書き換えはしない。

使い方:
  python tools/rakuten_heal_scan.py            # 一覧をファイルに出す
  python tools/rakuten_heal_scan.py --ids      # 対象idをカンマ区切りで
"""
import argparse
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

TODAY = datetime.date.today().isoformat()
PATH = "index.html"


def is_rakuten(t, ev):
    u = (t.get("url") or "") or ((ev.get("links") or {}).get("rakuten") or "")
    return ("rakuten" in u) or ("linksynergy" in u)


def visible(t):
    """今日の画面に出るか（index.html の表示ルールと同じ考え方）"""
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", action="store_true")
    ap.add_argument("--out", default="tmp/rakuten_heal_scan.txt")
    a = ap.parse_args()

    h = io.open(PATH, encoding="utf-8", newline="").read()
    EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

    rows, ids = [], []
    n_rk_slots = n_rk_entries = 0
    for e in EV:
        rk = [t for t in (e.get("tickets") or []) if is_rakuten(t, e)]
        if not rk:
            continue
        n_rk_entries += 1
        n_rk_slots += len(rk)
        hidden = [t for t in rk
                  if t.get("startDate") and t.get("startDate") == t.get("date")
                  and not t.get("soldout") and not t.get("saleUntilSoldOut")]
        gone = [t for t in hidden if not visible(t)]
        if hidden:
            rows.append((e["id"], e.get("name") or "", e.get("date") or "",
                         len(hidden), len(rk), len(gone)))
            ids.append(str(e["id"]))

    rows.sort(key=lambda r: (-r[5], -r[3]))
    if a.ids:
        print(",".join(ids))
        return 0

    o = io.open(a.out, "w", encoding="utf-8")
    o.write("=== 楽天の隠れ枠スキャン (today=%s) ===\n\n" % TODAY)
    o.write("楽天の枠を持つエントリ %d件 / 楽天の枠 %d枠\n" % (n_rk_entries, n_rk_slots))
    o.write("うち「発売日==締切日」の単日形を持つエントリ **%d件**\n" % len(rows))
    o.write("  （この形は締切を取り込めていない＝発売日の翌日から画面に出なくなる）\n\n")
    o.write("| id | 公演名 | 公演日 | 単日形 | 楽天枠 | もう画面から消えている |\n|---|---|---|---|---|---|\n")
    for i, name, d, nh, nr, ng in rows[:80]:
        o.write("| %d | %s | %s | %d | %d | %s |\n"
                % (i, name[:30], d, nh, nr, "🚨%d" % ng if ng else "0"))
    n_gone = sum(1 for r in rows if r[5])
    o.write("\n🚨**すでに画面から消えているエントリ … %d件**\n" % n_gone)
    o.write("（＝載せたのに買えなくなっている。ぴあならヒールが毎朝直す型）\n")
    o.close()
    print("楽天枠を持つ %d件 / 単日形 %d件 / うち消えている %d件 -> %s"
          % (n_rk_entries, len(rows), n_gone, a.out))
    return 2 if n_gone else 0


if __name__ == "__main__":
    sys.exit(main())
