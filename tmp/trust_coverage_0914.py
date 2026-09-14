# -*- coding: utf-8 -*-
"""昼に出す新着（genre:new）1,093件のうち、どこまで確かめたかを数える（読むだけ・2026-09-14）。
  ①別エージェントの独立の読み直し（scratchpad/pushcheck_*_result.json・朝の再チェック recheck_*）に入った件数
  ②照合（reconcile_new5）で「未照合 skip」になった枠を持つエントリ
使い方: python tmp/trust_coverage_0914.py
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\ada2db76-3770-4399-ab5a-9e566d50214d\scratchpad'
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
new = {e['id']: e for e in ev if e.get('genre') == 'new'}
print('新着 %d件' % len(new))

seen = {}
for p in sorted(glob.glob(os.path.join(SP, '*result*.json'))):
    try:
        rows = json.load(io.open(p, encoding='utf-8'))
    except Exception:
        continue
    if not isinstance(rows, list):
        continue
    ids = {r.get('id') for r in rows if isinstance(r, dict)}
    hit = ids & set(new)
    if hit:
        seen[os.path.basename(p)] = hit
allseen = set().union(*seen.values()) if seen else set()
for k, v in seen.items():
    print('  %-40s %d件' % (k, len(v)))
print('独立に読み直した新着 %d件 / %d件（%.0f%%）' % (len(allseen), len(new), 100.0 * len(allseen) / len(new)))

by_g = {}
for i, e in new.items():
    g = e.get('_genre') or '?'
    a, b = by_g.get(g, (0, 0))
    by_g[g] = (a + 1, b + (1 if i in allseen else 0))
for g, (a, b) in sorted(by_g.items(), key=lambda x: -x[1][0]):
    print('  %-10s %4d件中 読み直し %3d' % (g, a, b))
