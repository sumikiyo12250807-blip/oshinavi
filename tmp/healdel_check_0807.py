# -*- coding: utf-8 -*-
"""昼ヒールで出た削除候補3件を精査する（2026-08-07）。
罠＝①本日発売で発売時刻前だと0枠に見える ②w.pia直販形式は券種カードが無く0枠に見える
    ③ぴあ0枠でも他社で生きている。だから実ページを --all で開いて終了枠まで見る。
"""
import io
import json
import re
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402

IDS = [3319, 3380, 3876]
evs = {e["id"]: e for e in extract_events_array(r"C:\Users\user\oshinavi\index.html")}

for n, eid in enumerate(IDS):
    e = evs.get(eid)
    if not e:
        print("id%d 見つからない" % eid)
        continue
    print("=" * 78)
    print("id%d %s" % (eid, e.get("name")))
    print("   %s / %s / 公演 %s" % (e.get("prefecture"), (e.get("venue") or "")[:44], e.get("date")))
    for t in e.get("tickets") or []:
        print("   登録枠: %s | date=%s start=%s" % (t.get("type"), t.get("date"), t.get("startDate")))
    lk = e.get("links") or {}
    for k, v in lk.items():
        if v and k != "amazon":
            print("   %s: %s" % (k, v))
    url = lk.get("pia")
    if not url:
        continue
    if n:
        time.sleep(6)
    r = subprocess.run([sys.executable, "tools/pia_tickets.py", url, "--json", "--all"],
                       capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    try:
        rows = json.loads(txt)
    except Exception as ex:
        print("   🚨 ぴあ解析失敗: %s / 生出力の先頭 %s" % (ex, txt[:200]))
        continue
    print("   --- ぴあ実ページ 全%d券種 ---" % len(rows))
    for x in rows:
        pr = x["perfdate"] + ("〜" + x["perf_end"] if x.get("perf_end") and x["perf_end"] != x["perfdate"] else "")
        print("     [%s] %s %s | %s | %s" % (x["state"], pr, x["pref"], x["title"][:52], x["when"]))
    if not rows:
        print("     🚨 券種カードが1枚も無い＝w.pia直販形式を疑う（削除NG・要目視）")
