# -*- coding: utf-8 -*-
# ぴあ発売前スイープ＝7ジャンル×rlsStatus 0102/0202（1本ずつ順番に・ぴあは同時2本回さない）
import subprocess, sys, json, io, os
root = 'C:/Users/user/oshinavi/'
os.chdir(root)
summary = []
for lg in ['01', '02', '07', '06', '03', '04', '05']:
    for st in ['0102', '0202']:
        out = f'tmp/x1001/eve/presale_{lg}_{st}.json'
        r = subprocess.run([sys.executable, 'tools/presale_harvest.py', lg, out, f'rlsStatus={st}'],
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        tail = (r.stdout or '')[-600:]
        summary.append(f'=== {lg} {st} rc={r.returncode}\n{tail}')
        io.open('tmp/x1001/eve/pia_presale_sweep.txt', 'w', encoding='utf-8').write('\n'.join(summary))
print('done')
