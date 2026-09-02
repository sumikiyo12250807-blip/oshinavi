# -*- coding: utf-8 -*-
"""ぴあの発売前を7ジャンル総ざらいする（rlsStatus=0102 先着＋0202 抽選）。
memory reference_pia_presale_full_filter＝発売前の正しい絞り込みはこの2つ。
rlsIn=03（30日以内）は31日より先の発売を1件も拾えないので使わない。
出力は tmp/_sw_<lg>_<status>_0903.json（9/2と同じ形）。
"""
import subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LGS = ['01', '02', '03', '04', '05', '06', '07']
STATUSES = ['0102', '0202']

for lg in LGS:
    for st in STATUSES:
        out = 'tmp/_sw_%s_%s_0903.json' % (lg, st)
        print('=== lg=%s rlsStatus=%s -> %s ===' % (lg, st, out), flush=True)
        r = subprocess.run(
            [sys.executable, 'tools/pia_sweep_all.py', lg, out, 'rlsStatus=' + st],
            capture_output=True, text=True, encoding='utf-8', errors='replace')
        sys.stdout.write(r.stdout or '')
        if r.returncode != 0:
            sys.stdout.write('!! exit=%d\n%s\n' % (r.returncode, (r.stderr or '')[-800:]))
        sys.stdout.flush()
print('=== 全バケツ完了 ===')
