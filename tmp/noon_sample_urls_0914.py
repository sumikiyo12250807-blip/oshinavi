# -*- coding: utf-8 -*-
"""昼のpush前の独立検証に渡す抜き取り（id と ぴあURL だけ・登録値は出さない）。
id範囲の新着（genre:"new"）から、id順に等間隔で N件を取る。畳み込み先（引数で渡す）も全部入れる。
使い方: python tmp/noon_sample_urls_0914.py <id_from> <id_to> <N> <出力名> [畳み込み先id,…]
出力: tmp/noon_<出力名>_0914.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
lo, hi, N, tag = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
extra = [int(x) for x in (sys.argv[5] if len(sys.argv) > 5 else '').split(',') if x.strip()]
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


pool = [i for i in sorted(by) if lo <= i <= hi and by[i].get('genre') == 'new' and pia_urls(by[i])]
step = max(1, len(pool) // N)
pick = pool[::step][:N] + [i for i in extra if i in by]
with io.open('tmp/noon_%s_0914.txt' % tag, 'w', encoding='utf-8') as f:
    for i in pick:
        f.write('%s\t%s\n' % (i, ' '.join(pia_urls(by[i]))))
print('新着 %d件から %d件＋畳み込み先 %d件 → tmp/noon_%s_0914.txt' % (len(pool), min(N, len(pool[::step])), len(extra), tag))
print(','.join(str(i) for i in pick))
