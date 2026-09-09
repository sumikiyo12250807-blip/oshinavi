# -*- coding: utf-8 -*-
"""統合の相手が決められなかった5件を、ぴあの実ページで見て判断材料を出す。

🚨部分一致で畳むのは禁止なので、**中身（公演日・会場）で同じ興行かを見る**。
"""
import io
import json
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

HELD = [
    ('イルカ', 'https://ticket.pia.jp/pia/event.do?eventCd=2633651', [620]),
    ('佐藤竹善', 'https://ticket.pia.jp/pia/event.do?eventCd=2628634', [668, 6903]),
    ('吉幾三', None, [588]),
    ('キーウ・クラシック・バレエ', None, [942, 4638, 4834, 4906]),
    ('ＯＺアカデミー女子プロレス', None, [2704, 5199, 7067]),
]

merge = json.load(io.open('tmp/merge_0910.json', encoding='utf-8'))
byname = {}
for c in merge:
    byname.setdefault(c['artist'], []).append(c['url'])

h = io.open('index.html', encoding='utf-8').read()
import re
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
by = {e['id']: e for e in json.loads(m.group(2))}

for name, _u, ids in HELD:
    print('===== %s' % name)
    for u in byname.get(name, []):
        print('  【ハーベストが見つけたページ】%s' % u)
        try:
            e = B.build({'newid': 999999, 'artist': name, 'urls': [u]})
        except Exception as ex:
            print('    ビルド失敗 %r' % (ex,))
            continue
        if not e:
            print('    枠なし（売切など）')
            continue
        print('    公演=%s  会場=%s' % (e.get('dateLabel'), (e.get('venue') or '')[:60]))
        for t in e['tickets']:
            print('      %s' % t['type'][:70])
    for i in ids:
        e = by.get(i)
        if not e:
            continue
        print('  【既存 id=%s】%s' % (i, (e.get('name') or '')[:44]))
        print('    公演=%s  会場=%s' % (e.get('dateLabel'), (e.get('venue') or '')[:60]))
        for t in (e.get('tickets') or [])[:6]:
            print('      %s' % t['type'][:70])
    print()
