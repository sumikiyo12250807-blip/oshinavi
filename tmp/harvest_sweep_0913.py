# -*- coding: utf-8 -*-
"""朝のスイープ（2026-09-13）。
発売前（rlsStatus=0102＝先着・発売前／0202＝抽選・受付前）を全ジャンル回し、
そのあと受付中（0101）も回す（2026-09-07 ユーザー決定＝締切の縛りは外した）。
ジャンルの優先順＝①音楽 ②演劇・クラシック ③その他（memory feedback_harvest_genre_priority）。

使い方: python tmp/harvest_sweep_0913.py <フィルタ式> <lg> [<lg> ...]
例:     python tmp/harvest_sweep_0913.py rlsStatus=0102 02 07 06 03 04 05
出力:   tmp/presale_<lg>_<フィルタの数字>_0913.json ＋ 同名の .txt（ログ）
"""
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

flt = sys.argv[1]
lgs = sys.argv[2:]
tag = flt.split('=')[-1]
summary = []
for lg in lgs:
    out = 'tmp/presale_%s_%s_0913.json' % (lg, tag)
    log = 'tmp/presale_%s_%s_0913.txt' % (lg, tag)
    with io.open(log, 'w', encoding='utf-8') as f:
        r = subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, out, flt],
                           stdout=f, stderr=subprocess.STDOUT)
    try:
        d = json.load(io.open(out, encoding='utf-8'))
        summary.append((lg, d.get('total'), d.get('parsed'), len(d.get('new') or []), r.returncode))
    except Exception as e:
        summary.append((lg, 'ERR', str(e)[:40], 0, r.returncode))
    print('lg=%s %s' % (lg, summary[-1]))

print('=== %s の結果（lg / 全行 / 解析できた行 / 未掲載候補 / 終了コード）===' % flt)
for s in summary:
    print('  ', s)
