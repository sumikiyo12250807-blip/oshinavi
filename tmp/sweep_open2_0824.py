# -*- coding: utf-8 -*-
"""終端判定を直した presale_harvest で、打ち切られていた受付中スイープを取り直す（2026-08-24）。

1回目は「新規URLが増えないページ＝終端」の誤判定で、音楽0101が448ページ中32ページ(7.1%)、
演劇/スポーツ/クラシックも約50%で止まっていた。ジャンル優先順に回す。
"""
import subprocess
import sys
import time

STAMP = '0824'
JOBS = [('01', '音楽', '0101'), ('07', 'クラシック', '0101'),
        ('02', '演劇', '0101'), ('03', 'スポーツ', '0101')]

for lg, name, st in JOBS:
    out = 'tmp/open_%s_%s_%s.json' % (lg, st, STAMP)
    t0 = time.time()
    r = subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, out, 'rlsStatus=' + st],
                       capture_output=True)
    txt = r.stdout.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'parsed items' in l] or ['(不明)']
    print('[%s %s %s] exit=%d %.0fs %s' % (lg, name, st, r.returncode, time.time() - t0, line[0]))
    sys.stdout.flush()
    time.sleep(5)
print('取り直し完了')
