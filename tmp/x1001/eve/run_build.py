# -*- coding: utf-8 -*-
# build_pia_entries を新規候補→足し込み候補の順に1本ずつ（ぴあは同時に回さない）
import subprocess, sys, os
os.chdir('C:/Users/user/oshinavi')
for src, dst in [('tmp/x1001/eve/pia_merge_in.json', 'tmp/x1001/eve/pia_built_merge_raw.json'),
                 ('tmp/x1001/eve/pia_cands.json', 'tmp/x1001/eve/pia_built_raw.json')]:
    with open(dst, 'w', encoding='utf-8') as fo, open(dst + '.log', 'w', encoding='utf-8') as fe:
        subprocess.run([sys.executable, 'tools/build_pia_entries.py', src], stdout=fo, stderr=fe, encoding='utf-8')
print('done')
