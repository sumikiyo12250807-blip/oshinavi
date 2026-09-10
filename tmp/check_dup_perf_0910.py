# -*- coding: utf-8 -*-
"""楽天の枠を足したあと、同じ（券種の種類・公演日）にぴあと楽天の枠が二重に並ばないかを見る。

画面はチケットを1枠ずつリンクにするので、同じ公演に「ぴあの一般発売」と「楽天の一般発売」が
並ぶと、締切が違って見えて紛らわしい。**足す前に数えておく。**
"""
import io
import json
import re
import sys
import time
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as RH
import build_rakuten_entries as B


def vendor(u):
    if 'rakuten' in (u or '') or 'linksynergy' in (u or ''):
        return '楽天'
    if 'eplus' in (u or ''):
        return 'e+'
    if 'pia.jp' in (u or ''):
        return 'ぴあ'
    return '(空)'


def kind(ty):
    """券種の大まかな種類（一般発売／先行／プリセール…）と公演日。"""
    m = re.search(r'^(.*?)（[^（）]*?((?:R\d+年\s*)?[\d/〜]+)(?:\s+\d{1,2}:\d{2})?公演）', ty or '')
    if not m:
        return (ty or '', '')
    return (m.group(1).strip(), re.sub(r'R\d+年\s*', '', m.group(2)).strip())


h = io.open('index.html', encoding='utf-8').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
by = {e['id']: e for e in json.loads(mm.group(2))}

pairs = json.load(io.open('tmp/rakuten_link_pairs_0910.json', encoding='utf-8'))
for p in pairs:
    e = by.get(p['id'])
    if not e:
        continue
    try:
        rec = RH.parse_page(p['url'], RH.fetch(p['url']))
        ne, why = B.build([rec], e['id'])
    except Exception:
        continue
    if not ne:
        continue
    cur = [(kind(t['type']), vendor(t.get('url')), t['type'], t['date'])
           for t in (e.get('tickets') or [])]
    dup = []
    for t in ne['tickets']:
        k = kind(t['type'])
        same = [c for c in cur if c[0] == k]
        if same:
            dup.append((k, t['type'], t['date'], same))
    if dup:
        print('== id=%-5s %s' % (e['id'], (e.get('name') or '')[:40]))
        for k, ty, d, same in dup:
            print('   🔁 足そうとしている: %-54s date=%s' % (ty[:54], d))
            for kk, v, sty, sd in same:
                print('        既存[%s] %-50s date=%s' % (v, sty[:50], sd))
    time.sleep(0.3)
print('\n（同じ券種・同じ公演日の枠が既にあるものだけを出した）')
