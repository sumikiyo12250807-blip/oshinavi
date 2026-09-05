# -*- coding: utf-8 -*-
"""9/6朝の発売前スイープ。ぴあの7ジャンルを順に回す（同時に叩かない＝429対策）。
優先順は feedback_harvest_genre_priority ＝①音楽 ②演劇/クラシック ③その他。
9/5は音楽・演劇・クラシックだけだったので、スポーツ・映画・アート・イベントが未スイープ。
"""
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

LG = [("01", "音楽"), ("02", "演劇"), ("07", "クラシック"),
      ("03", "スポーツ"), ("04", "映画"), ("05", "アート"), ("06", "イベント")]

for code, name in LG:
    out = "tmp/presale_%s_0906.json" % code
    print("=== lg=%s %s ===" % (code, name), flush=True)
    r = subprocess.run([sys.executable, "tools/presale_harvest.py", code, out],
                       capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    for line in txt.splitlines()[-6:]:
        print("   " + line, flush=True)
    if r.returncode != 0:
        print("   ⚠️ exit=%d" % r.returncode, flush=True)
        print("   " + r.stderr.decode("utf-8", "replace")[-500:], flush=True)
    time.sleep(20)          # ぴあを続けて叩かない

print("=== 全ジャンル完了 ===", flush=True)
