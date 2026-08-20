# -*- coding: utf-8 -*-
"""heal_hidden_0710 で convert したエントリを reconcile_pia で独立再照合（二段構え）。"""
import json, subprocess, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('tmp/heal_hidden_0710.json', encoding='utf-8'))
ids = [str(o['id']) for o in d if o.get('status') == 'convert']
# 期限切れtriageで変換した4件も足す
ids += ['125', '1162', '1481', '1993']
ids = sorted(set(ids), key=int)
print(f'照合対象 {len(ids)}件')
r = subprocess.run([sys.executable, 'tools/reconcile_pia.py', '--ids', ','.join(ids)],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
open('tmp/recon_heal_0710.txt', 'w', encoding='utf-8').write(r.stdout + '\n' + r.stderr)
print(r.stdout[-4000:])
if r.stderr.strip():
    print('--- stderr ---')
    print(r.stderr[-1500:])
