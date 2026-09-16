# -*- coding: utf-8 -*-
"""新着プール（genre:"new"）の中身を数える（読むだけ・2026-09-15 朝）。
id の範囲（last_batch.json のバッチ）ごとに、件数・下書きジャンル(_genre)・売り場（ぴあ／e+／楽天／その他）を出す。
使い方: python tmp/pool_summary_0915.py
"""
import collections
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
pool = [e for e in ev if e.get('genre') == 'new']
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))['batches']


def vendor(e):
    urls = [e.get('url') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]
    s = set()
    for u in urls:
        if 'pia.jp' in u:
            s.add('pia')
        elif 'eplus' in u:
            s.add('eplus')
        elif 'rakuten' in u:
            s.add('rakuten')
        elif u:
            s.add('other')
    return '+'.join(sorted(s)) or 'none'


def batch_of(i):
    for b in lb:
        if 'ids' in b and i in b['ids']:
            return '%s %s' % (b['date'], b['slot'])
        if b['id_from'] <= i <= b['id_to']:
            return '%s %s' % (b['date'], b['slot'])
    return '(記録なし)'


print('新着プール %d件' % len(pool))
by = collections.OrderedDict()
for e in sorted(pool, key=lambda x: x['id']):
    by.setdefault(batch_of(e['id']), []).append(e)
for k, es in by.items():
    g = collections.Counter(e.get('_genre') or '(なし)' for e in es)
    v = collections.Counter(vendor(e) for e in es)
    print('\n[%s] %d件  id %d〜%d' % (k, len(es), es[0]['id'], es[-1]['id']))
    print('  売り場: ' + ' / '.join('%s %d' % kv for kv in v.most_common()))
    print('  下書き: ' + ' / '.join('%s %d' % kv for kv in g.most_common()))
    if len(es) <= 12:
        print('  ids: ' + ','.join(str(e['id']) for e in es))
