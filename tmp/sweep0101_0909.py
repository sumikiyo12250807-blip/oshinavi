# -*- coding: utf-8 -*-
"""受付中(rlsStatus=0101)の総ざらい・9/9版。
🚨 ぴあの一覧は100ページ＝1,000件で頭打ちになるので、
   総数が950以上のジャンルは pf=（都道府県コード＝JISコード）で割る。
   割らずに回すと「あ行だけ拾って終わり」型の打ち切りになる（2026-08-17の事故）。
ログには total と pages を必ず残す＝ページ到達率で打ち切りを判定するため
   （feedback_newpool_presale_ratio_gate）。
"""
import os, re, sys, io, time, subprocess, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
GENRES = [("06", "イベント"), ("03", "スポーツ"), ("05", "アート"), ("04", "映画"),
          ("02", "演劇"), ("07", "クラシック"), ("01", "音楽")]
PF = ["%02d" % i for i in range(1, 48)]
SPLIT_AT = 950

OUTDIR = "tmp/sweep0101_0909"
os.makedirs(OUTDIR, exist_ok=True)
log = io.open(OUTDIR + "/_driver.log", "w", encoding="utf-8", buffering=1)


def total_of(lg, extra=""):
    url = "https://t.pia.jp/pia/rlsInfo.do?lg=%s&rlsStatus=0101%s&page=1" % (lg, extra)
    try:
        req = urllib.request.Request(url, headers=UA)
        h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return -1
    m = re.search(r"全\s*([\d,]+)\s*件中", h)
    return int(m.group(1).replace(",", "")) if m else 0


def run(lg, filt, tag):
    out = "%s/%s.json" % (OUTDIR, tag)
    t0 = time.time()
    r = subprocess.run([sys.executable, "tools/presale_harvest.py", lg, out, filt],
                       capture_output=True, timeout=3600)
    txt = (r.stdout or b"").decode("utf-8", "replace")
    m = re.search(r"total=(\d+) pages=(\d+)", txt)
    nb = re.search(r"NOT in DB \(new candidates\):\s*(\d+)", txt)
    log.write("[%s] rc=%s %.0fs total=%s pages=%s new=%s\n"
              % (tag, r.returncode, time.time() - t0,
                 m.group(1) if m else "?", m.group(2) if m else "?",
                 nb.group(1) if nb else "?"))
    io.open("%s/%s.log" % (OUTDIR, tag), "w", encoding="utf-8").write(txt)
    return r.returncode


for lg, jp in GENRES:
    t = total_of(lg)
    log.write("\n=== lg=%s (%s) 受付中0101 総数=%s ===\n" % (lg, jp, t))
    if t < 0:
        log.write("  総数が取れなかったので飛ばす\n")
        continue
    if t < SPLIT_AT:
        run(lg, "rlsStatus=0101", "%s_all" % lg)
        continue
    log.write("  1,000の頭打ちを越えるので都道府県で割る\n")
    for pf in PF:
        tp = total_of(lg, "&pf=%s" % pf)
        if tp <= 0:
            log.write("  pf=%s 0件（か取得できず）＝飛ばす\n" % pf)
            time.sleep(1)
            continue
        if tp >= 1000:
            log.write("  🚨pf=%s が %d件＝1,000以上。この県は取りこぼす可能性がある\n" % (pf, tp))
        run(lg, "rlsStatus=0101&pf=%s" % pf, "%s_pf%s" % (lg, pf))
        time.sleep(1)

log.write("\n=== 受付中スイープ 終了 ===\n")
log.close()
print("done -> %s/_driver.log" % OUTDIR)
