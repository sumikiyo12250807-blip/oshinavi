# -*- coding: utf-8 -*-
"""既存の楽天エントリ(links.rakuten あり)のidを列挙。新着48件は除く（もう照合済み）。
さらに「startDate==date の単日形（隠れ枠）」を持つ楽天枠も洗い出す
＝ヒール(heal_stale_deadlines)はぴあ専用なので、楽天で単日形が出来ると誰も直せない。"""
import json
import re

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

rak = [e for e in EV if (e.get('links') or {}).get('rakuten')]
old = [e for e in rak if e.get('genre') != 'new']
print('楽天エントリ 全%d件 / うち既存(振り分け済) %d件' % (len(rak), len(old)))
print('ids=' + ','.join(str(e['id']) for e in old))

lines = ['=== 楽天エントリで「発売日==締切日」の単日形(隠れ枠)を持つもの ===']
n = 0
for e in rak:
    bad = [t for t in (e.get('tickets') or [])
           if t.get('startDate') and t.get('startDate') == t.get('date')
           and not t.get('saleUntilSoldOut')]
    if bad:
        n += 1
        lines.append(f"id={e['id']} {(e.get('artist') or '')[:44]} genre={e.get('genre')}")
        for t in bad:
            lines.append(f"    {t.get('type')}  [date={t.get('date')} start={t.get('startDate')}]")
lines.append('')
lines.append(f'=== 該当 {n}件 ===')
open('tmp/rakuten_ids_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
