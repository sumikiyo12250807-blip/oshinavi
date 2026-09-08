# -*- coding: utf-8 -*-
"""9/9朝のスイープ（発売前）。0102=先着・0202=抽選 を7ジャンル。
   presale_harvest.py をサブプロセスで順に回すだけ。ログは tmp/sweep_0909/ に残す。
   ページ到達率(total/pages)を必ずログに残す＝打ち切りを判定するため。"""
import os, re, sys, subprocess, time, io

GENRES = [("01", "音楽"), ("07", "クラシック"), ("02", "演劇"),
          ("06", "イベント"), ("03", "スポーツ"), ("05", "アート"), ("04", "映画")]

PHASES = [("rlsStatus=0102", "presale_first"),   # 発売前・先着
          ("rlsStatus=0202", "presale_lot")]     # 発売前・抽選

os.makedirs("tmp/sweep_0909", exist_ok=True)
log = io.open("tmp/sweep_0909/_driver.log", "w", encoding="utf-8", buffering=1)

for filt, tag in PHASES:
    for lg, jp in GENRES:
        out = "tmp/sweep_0909/%s_%s.json" % (tag, lg)
        t0 = time.time()
        log.write("[start] %s lg=%s (%s) filter=%s\n" % (tag, lg, jp, filt))
        try:
            r = subprocess.run([sys.executable, "tools/presale_harvest.py", lg, out, filt],
                               capture_output=True, timeout=1800)
            txt = (r.stdout or b"").decode("utf-8", "replace")
            io.open("tmp/sweep_0909/%s_%s.log" % (tag, lg), "w", encoding="utf-8").write(txt)
            tail = txt.strip().splitlines()
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
print("sweep done -> tmp/sweep_0909/_driver.log")
