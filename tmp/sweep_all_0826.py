# -*- coding: utf-8 -*-
"""発売前(rlsIn=03)を7ジャンル順に総ざらいする。
ジャンルの優先順は feedback_harvest_genre_priority ＝①音楽 ②演劇/クラシック/お笑い ③その他。
1発実行にしてあるのは feedback_no_expansion_commands（複合コマンドで自走が止まる）対策。"""
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

ORDER = [("01", "音楽"), ("02", "演劇"), ("07", "クラシック"),
         ("06", "イベント"), ("03", "スポーツ"), ("04", "映画"), ("05", "アート")]

for lg, name in ORDER:
    out = "tmp/sweep_%s_0826.json" % lg
    print("=" * 60, flush=True)
    print("[%s %s] → %s" % (lg, name, out), flush=True)
    r = subprocess.run([sys.executable, "tools/pia_sweep_all.py", lg, out],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = "\n".join((r.stdout or "").strip().split("\n")[-6:])
    print(tail, flush=True)
    if r.returncode != 0:
        print("⚠️ returncode=%s / stderr: %s" % (r.returncode, (r.stderr or "")[-300:]), flush=True)
    time.sleep(20)   # ぴあを続けざまに叩かない（reference_pia_rate_limit_429）
print("=" * 60, flush=True)
print("スイープ完了", flush=True)
