# -*- coding: utf-8 -*-
"""9/8朝のスイープ。発売前(0102/0202)を7ジャンル → そのあと受付中(0101)。
   presale_harvest.py をサブプロセスで順に回すだけ。ログは tmp/sweep_0908/ に残す。"""
import os, sys, subprocess, time, io

GENRES = [("01", "音楽"), ("07", "クラシック"), ("02", "演劇"),
          ("06", "イベント"), ("03", "スポーツ"), ("05", "アート"), ("04", "映画")]

# (フィルタ, 名札)
PHASES = [("rlsStatus=0102", "presale_first"),   # 発売前・先着
          ("rlsStatus=0202", "presale_lot")]     # 発売前・抽選

os.makedirs("tmp/sweep_0908", exist_ok=True)
log = io.open("tmp/sweep_0908/_driver.log", "w", encoding="utf-8", buffering=1)

for filt, tag in PHASES:
    for lg, jp in GENRES:
        out = "tmp/sweep_0908/%s_%s.json" % (tag, lg)
        t0 = time.time()
        log.write("[start] %s lg=%s (%s) filter=%s\n" % (tag, lg, jp, filt))
        try:
            r = subprocess.run([sys.executable, "tools/presale_harvest.py", lg, out, filt],
                               capture_output=True, timeout=1800)
            tail = (r.stdout or b"").decode("utf-8", "replace").strip().splitlines()
            log.write("[done ] %s lg=%s rc=%s %.0fs :: %s\n"
                      % (tag, lg, r.returncode, time.time() - t0,
                         " | ".join(tail[-3:]) if tail else "(no output)"))
            if r.returncode != 0:
                err = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()
                log.write("        stderr: %s\n" % (" | ".join(err[-3:]) if err else "(none)"))
        except subprocess.TimeoutExpired:
            log.write("[TIMEOUT] %s lg=%s\n" % (tag, lg))
        time.sleep(3)   # ぴあを叩きすぎない

log.write("=== 全フェーズ終了 ===\n")
log.close()
print("sweep done -> tmp/sweep_0908/_driver.log")
