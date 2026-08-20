# -*- coding: utf-8 -*-
"""7/29夜に消えた5件のe+実態を機械確認（買える窓があるか＝復元すべきか）"""
import io, sys, json
sys.path.insert(0, 'tools')
from eplus_harvest import fetch
from reconcile_eplus import parse_blocks
import datetime

TODAY = datetime.date.today()

TARGETS = [
    (3011, '玉置浩二',   'https://eplus.jp/sf/detail/0011860001'),
    (3015, '米倉利紀',   'https://eplus.jp/sf/detail/4568770001-P0030001P021001'),
    (3033, 'ハルナ',     'https://eplus.jp/sf/detail/3982190001-P0030007P021001'),
    (3043, '遠藤響子',   'https://eplus.jp/sf/detail/4523530001-P0030001P021001'),
    (3052, 'REBECCA',    'https://eplus.jp/sf/detail/1562950001-P0030019P021001'),
]

out = ['today=%s' % TODAY]
for eid, name, url in TARGETS:
    out.append('=== id=%d %s' % (eid, name))
    out.append('    %s' % url)
    try:
        h = fetch(url)
    except Exception as ex:
        out.append('    ❌FETCH %s' % str(ex)[:120])
        continue
    blocks = parse_blocks(h)
    if not blocks:
        out.append('    ⚠️ block-ticket 0件（受付期間の記載なし）')
    alive = 0
    for b in blocks:
        future = b['ed'] >= TODAY
        buyable = b['status'] in ('open', 'before') and future
        if buyable:
            alive += 1
        out.append('    窓 %s %s〜%s %s  status=%s  締切未来=%s  買える=%s' % (
            b['sd'], b['st'], b['ed'], b['et'], b['status'], future, buyable))
    out.append('    → 買える窓 %d件 / 全%d件' % (alive, len(blocks)))
    out.append('')

io.open('tmp/out_lost5_eplus.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_lost5_eplus.txt')
