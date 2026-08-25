# -*- coding: utf-8 -*-
"""ぴあ発売前(rlsIn=03)を全7ジャンル順にスイープする（2026-08-24 朝の新着収集）。

シェルの for ループは「Contains expansion」の確認で自走が止まるので python 1発にする
（memory: feedback_no_expansion_commands）。ジャンルは順番に回す＝並列にするとぴあが429を返し、
そのあとの QC ゲートが静かに壊れる（memory: reference_pia_rate_limit_429）。
"""
import subprocess
import sys
import time

STAMP = '0824'
LGS = [('01', '音楽'), ('02', '演劇'), ('07', 'クラシック'), ('03', 'スポーツ'),
       ('06', 'イベント'), ('04', '映画'), ('05', 'アート')]

for lg, name in LGS:
    out = 'tmp/presale_%s_%s.json' % (lg, STAMP)
    t0 = time.time()
    r = subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, out],
                       capture_output=True)
    tail = r.stdout.decode('utf-8', 'replace').strip().splitlines()[-1:] or ['(出力なし)']
    print('[%s %s] exit=%d %.0fs %s' % (lg, name, r.returncode, time.time() - t0, tail[0]))
    sys.stdout.flush()
    time.sleep(3)
print('スイープ完了')
