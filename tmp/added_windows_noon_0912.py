# -*- coding: utf-8 -*-
"""前回のpush（origin/main）から今までに、既存のエントリ（新着プール以外）へ増えた枠を並べる（読むだけ）。
新着プールの分は翌朝の再チェックを通るが、既存に足した枠はそのまま公開される＝push前に抜き取りで確かめる対象。
使い方: python tmp/added_windows_0912.py [抜き取り数=25]
出力: tmp/added_windows_noon_0912.txt（全件）／ tmp/push_sample_noon_0912.txt（抜き取り・エージェントに渡す）
"""
import io
import json
import random
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 25


def load(text):
    m = re.search(r'  const EVENTS = (\[.*?\]);', text, re.S)
    return {e['id']: e for e in json.loads(m.group(1))}


old = load(subprocess.run(['git', 'show', 'origin/main:index.html'], capture_output=True).stdout.decode('utf-8', 'replace'))
new = load(io.open('index.html', encoding='utf-8').read())

rows = []
for i, e in new.items():
    if e.get('genre') == 'new' or i not in old:
        continue
    before = {(t.get('type'), t.get('date')) for t in old[i].get('tickets') or []}
    lp = (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('eplus') or ''
    for t in e.get('tickets') or []:
        if (t.get('type'), t.get('date')) in before:
            continue
        rows.append((i, e.get('name') or '', t.get('type'), t.get('date'), t.get('startDate') or '', t.get('url') or lp))

with io.open('tmp/added_windows_noon_0912.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write('id%s | %s | %s | date=%s start=%s | %s\n' % r)
random.seed(1512)
sample = random.sample(rows, min(N, len(rows)))
with io.open('tmp/push_sample_noon_0912.txt', 'w', encoding='utf-8') as f:
    for i, name, ty, d, sd, u in sorted(sample):
        f.write('%s\t%s\t%s\n' % (i, u, name[:40]))
print('既存エントリに増えた（または書き換わった）枠 %d件 → tmp/added_windows_noon_0912.txt' % len(rows))
print('抜き取り %d件 → tmp/push_sample_noon_0912.txt' % len(sample))
