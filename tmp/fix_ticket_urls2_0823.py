# -*- coding: utf-8 -*-
"""統合で「今日足した枠」のうち url が無い6枠だけに、その売り場のURLを刻む（対象を明示指定）。

なぜ要るか: build_pia_entries に複数URLを渡すと、2本目以降から拾った枠に ticket.url が付かず、
エントリの links.pia（古い公演のページ）に飛ぶ＝その枠を売っていないページに着地する。
reconcile が STALE で検出した。範囲を広げると既存の枠まで巻き込むので、対象を手で指定する。
"""
import re, io, json, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv

TARGETS = [
    (2992, '一般発売（愛知 11/22公演）9/20 10:00発売', 'https://t.pia.jp/pia/event/event.do?eventCd=2622966'),
    (3514, 'プリセール（愛知 12/26公演）8/30 10:00発売', 'https://t.pia.jp/pia/event/event.do?eventCd=2633380'),
    (3514, '一般発売（愛知 12/26公演）11/28 10:00発売', 'https://t.pia.jp/pia/event/event.do?eventCd=2633380'),
    (4115, '一般発売（大阪 11/20公演）8/29 10:00発売', 'https://t.pia.jp/pia/event/event.do?eventCd=2625001'),
    (4167, '一般発売（大阪 9/25公演）8/29 10:00発売', 'https://t.pia.jp/pia/event/event.do?eventCd=2633244'),
    (4167, '一般発売（大阪 9/26公演）8/29 10:00発売', 'https://t.pia.jp/pia/event/event.do?eventCd=2633244'),
]

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

done, miss = [], []
for eid, ty, url in TARGETS:
    e = by.get(eid)
    hit = [t for t in (e.get('tickets') or []) if t.get('type') == ty] if e else []
    if len(hit) != 1:
        miss.append((eid, ty, len(hit)))
        continue
    if hit[0].get('url'):
        miss.append((eid, ty, 'すでにURLあり'))
        continue
    done.append((eid, ty, url))
    if APPLY:
        hit[0]['url'] = url

print('刻む %d件 / 当たらなかった %d件' % (len(done), len(miss)))
for x in done:
    print('  id%-5d %s → %s' % x)
for x in miss:
    print('  !! id%-5d %s (%s)' % x)

if APPLY and not miss:
    io.open('index.html.bak_0823_ticketurl', 'w', encoding='utf-8').write(h)
    io.open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
    print('適用した')
elif APPLY:
    print('当たらない枠があるので適用しない')
