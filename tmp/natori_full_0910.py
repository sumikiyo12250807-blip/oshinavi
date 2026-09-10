# -*- coding: utf-8 -*-
"""ぴあの「なとり」検索27件を全部出して、本人の公演がどれだけ載っているかを見る。

ユーザー（2026-09-10）＝「ぴあになとりの取りこぼし結構あると思う」

🚨さっきは「未登録」だけ見て、**登録済みの中身を見ていなかった**。
「なとり」は地名（名取市／タイハクホール名取）ともぶつかるので、
本人の公演かどうかを1件ずつ判定する。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
codes = set(re.findall(r'event(?:Bundle)?Cd=([\w]+)', h))

audit = json.load(io.open('tmp/x_audit_0911.json', encoding='utf-8'))
hits = audit.get('なとり', [])

print('ぴあ「なとり」検索 %d件' % len(hits))
print('')

hon, chimei = [], []
for x in hits:
    nm = x['name']
    ven = x['venue']
    # 会場名に「名取」が入るもの／公演名が別アーティストのものは地名ぶつかり
    if '名取' in ven or 'ムジカーザ' in ven:
        chimei.append(x)
    elif 'なとり' in nm or 'ナトリ' in nm or 'natori' in nm.lower():
        hon.append(x)
    else:
        chimei.append(x)

print('■ 本人「なとり」の公演らしいもの … %d件' % len(hon))
for x in hon:
    cd = (re.search(r'event(?:Bundle)?Cd=([\w]+)', x['url']) or [None, ''])[1]
    mark = 'OK 登録済' if cd in codes else '🚨未登録'
    print('  %s [%s] %-34s %s / %s' % (mark, x['state'], x['name'][:34],
                                       x['date'][:24], x['venue'][:26]))
    print('        %s' % x['url'])

print('')
print('■ 地名「名取」など別物 … %d件' % len(chimei))
for x in chimei[:30]:
    print('   [%s] %-34s %s / %s' % (x['state'], x['name'][:34], x['date'][:20], x['venue'][:24]))

print('')
print('--- いま登録にある「なとり」 ---')
for e in EVENTS:
    a = (e.get('artist') or '') + (e.get('name') or '')
    if 'なとり' in a and '名取' not in (e.get('venue') or ''):
        print('  id%-5d %-34s 公演%s / %s'
              % (e['id'], (e.get('name') or '')[:34], e.get('date'), e.get('venue', '')[:26]))
        for t in e.get('tickets') or []:
            print('      - %-48s date=%s' % ((t.get('type') or '')[:48], t.get('date')))
