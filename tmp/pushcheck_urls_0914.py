# -*- coding: utf-8 -*-
"""朝のpush前の独立検証用に、今朝触ったエントリを id と ぴあURL だけにして2つに割る（登録値は出さない）。
A＝今朝投入した新着（8385〜8431 のぴあ由来）
B＝今朝手で触ったエントリ（畳み込み先・870・4307・2500・止まった4件）＋ヒール本体で当てたものから10件（id順に等間隔）
使い方: python tmp/pushcheck_urls_0914.py
出力: tmp/pushcheck_A_0914.txt ／ tmp/pushcheck_B_0914.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}


def pia_urls(e):
    urls = []
    L = e.get('links') or {}
    if L.get('pia'):
        urls.append(L['pia'])
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        if 'pia.jp' in u and u not in urls:
            urls.append(u)
    return urls


A = [i for i in range(8385, 8432) if i in by and pia_urls(by[i])]
touched = [3892, 5155, 549, 7326, 727, 5332, 8405, 870, 4307, 2500, 615, 4412, 5016, 5193]
heal = [h['id'] for h in json.load(io.open('tmp/heal_stale.json', encoding='utf-8')) if h.get('status') == 'convert']
heal = [i for i in sorted(set(heal)) if i in by and i not in touched and i != 3853]
step = max(1, len(heal) // 10)
B = touched + heal[::step][:10]
for name, ids in (('A', A), ('B', B)):
    with io.open('tmp/pushcheck_%s_0914.txt' % name, 'w', encoding='utf-8') as f:
        for i in ids:
            us = pia_urls(by[i])
            if us:
                f.write('%s\t%s\n' % (i, ' '.join(us)))
    print('%s %d件: %s' % (name, len(ids), ','.join(str(i) for i in ids)))
