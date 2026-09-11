# -*- coding: utf-8 -*-
"""発売前の総ざらい・9/12版（rlsStatus=0102 先着発売前 ＋ 0202 抽選受付前）。

🚨 rlsIn=03（30日以内）だけだと 31日より先に発売される公演を1件も拾えない
   （[[reference_pia_presale_full_filter]]／[[reference_pia_rlsin_measured]]）。
発売前は在庫が小さいので都道府県で割る必要は普通は無いが、
**総数が950を超えたら割る**（1,000件で頭打ちになるため）。
ログに total と pages を必ず残す＝ページ到達率で打ち切りを判定する
   （[[feedback_newpool_presale_ratio_gate]]）。
"""
import io
import os
import re
import subprocess
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
GENRES = [('01', '音楽'), ('02', '演劇'), ('07', 'クラシック'), ('06', 'イベント'),
          ('03', 'スポーツ'), ('05', 'アート'), ('04', '映画')]
FILTERS = ['rlsStatus=0102', 'rlsStatus=0202']
PF = ['%02d' % i for i in range(1, 48)]
SPLIT_AT = 950

OUTDIR = 'tmp/sweep_presale_0912'
os.makedirs(OUTDIR, exist_ok=True)
log = io.open(OUTDIR + '/_driver.log', 'w', encoding='utf-8', buffering=1)


def total_of(lg, filt, extra=''):
    url = 'https://t.pia.jp/pia/rlsInfo.do?lg=%s&%s%s&page=1' % (lg, filt, extra)
    try:
        req = urllib.request.Request(url, headers=UA)
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    except Exception:
        return -1
    m = re.search(r'全\s*([\d,]+)\s*件中', h)
    return int(m.group(1).replace(',', '')) if m else 0


def run(lg, filt, tag):
    out = '%s/%s.json' % (OUTDIR, tag)
    t0 = time.time()
    r = subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, out, filt],
                       capture_output=True, timeout=3600)
    txt = (r.stdout or b'').decode('utf-8', 'replace')
    m = re.search(r'total=(\d+) pages=(\d+)', txt)
    nb = re.search(r'NOT in DB \(new candidates\):\s*(\d+)', txt)
    log.write('[%s] rc=%s %.0fs total=%s pages=%s new=%s\n'
              % (tag, r.returncode, time.time() - t0,
                 m.group(1) if m else '?', m.group(2) if m else '?',
                 nb.group(1) if nb else '?'))
    io.open('%s/%s.log' % (OUTDIR, tag), 'w', encoding='utf-8').write(txt)
    return r.returncode


for filt in FILTERS:
    for lg, jp in GENRES:
        t = total_of(lg, filt)
        log.write('\n=== lg=%s (%s) %s 総数=%s ===\n' % (lg, jp, filt, t))
        if t < 0:
            log.write('  総数が取れなかったので飛ばす\n')
            continue
        if t == 0:
            log.write('  0件\n')
            continue
        tag = '%s_%s' % (lg, filt.split('=')[1])
        if t < SPLIT_AT:
            run(lg, filt, tag)
            continue
        log.write('  1,000の頭打ちを越えるので都道府県で割る\n')
        for pf in PF:
            tp = total_of(lg, filt, '&pf=%s' % pf)
            if tp <= 0:
                continue
            log.write('   pf=%s 総数=%s\n' % (pf, tp))
            run(lg, '%s&pf=%s' % (filt, pf), '%s_pf%s' % (tag, pf))

log.write('\n=== 終わり ===\n')
print('終わったわ → %s/_driver.log' % OUTDIR)
