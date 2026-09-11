# -*- coding: utf-8 -*-
"""check_expired の出力を2群に分けて id を取り出す（読むだけ）。
使い方: python tmp/expired_ids_0912.py <check_expired の出力ファイル>
出力: tmp/expired_del_0912.txt（公演終了＝削除候補）／tmp/expired_recheck_0912.txt（⚠️要再確認）
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read().splitlines()
dele, rech, live = [], [], []
section = 'del'
for ln in txt:
    if '機械判定だけで削除しないこと' in ln:
        section = 'rech'
        continue
    m = re.match(r'^\s+id=(\d+):', ln)
    if not m:
        continue
    i = int(m.group(1))
    if section == 'del':
        if '買える枠' in ln and '全販売終了' not in ln:
            live.append(i)
        else:
            dele.append(i)
    else:
        rech.append(i)
open('tmp/expired_del_0912.txt', 'w', encoding='utf-8').write(','.join(map(str, dele)))
open('tmp/expired_recheck_0912.txt', 'w', encoding='utf-8').write(','.join(map(str, rech)))
print('公演終了（全販売終了） %d件: %s' % (len(dele), ','.join(map(str, dele))))
print('公演終了だが買える枠あり %d件: %s' % (len(live), ','.join(map(str, live))))
print('要再確認 %d件 → tmp/expired_recheck_0912.txt' % len(rech))
