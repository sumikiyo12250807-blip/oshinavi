# -*- coding: utf-8 -*-
"""ぴあの発売前スイープを7ジャンル×2フィルタで回す（朝の新着収集）。

🚨 発売前を全部取る絞り込みは rlsStatus=0102（先着の発売前）と 0202（抽選の受付前）の2本
   （reference_pia_presale_full_filter）。片方だけだと半分落ちる。
🚨 叩きすぎると 429/sorry ページを掴んでゲートが静かに壊れるので、ジャンル間に間を置く
   （reference_pia_rate_limit_429）。
"""
import subprocess, sys, time, io, os

LGS = [("01", "音楽"), ("02", "演劇"), ("07", "クラシック"), ("06", "イベント"),
       ("03", "スポーツ"), ("04", "映画"), ("05", "アート")]
FILTERS = ["rlsStatus=0102", "rlsStatus=0202"]

log = io.open("tmp/sweep_0907.txt", "w", encoding="utf-8")
for lg, name in LGS:
    for f in FILTERS:
        out = "tmp/presale_0907_%s_%s.json" % (lg, f.split("=")[1])
        r = subprocess.run([sys.executable, "tools/presale_harvest.py", lg, out, f],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        tail = (r.stdout or "").strip().splitlines()
        log.write("=== lg=%s(%s) %s exit=%s ===\n" % (lg, name, f, r.returncode))
        for ln in tail[-6:]:
            log.write("   %s\n" % ln)
        if r.returncode != 0:
            log.write("   STDERR: %s\n" % (r.stderr or "")[-400:])
        log.flush()
        time.sleep(6)
log.close()
print("done")
