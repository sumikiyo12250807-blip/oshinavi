# -*- coding: utf-8 -*-
"""ヒールの安全弁でブロックされたエントリのビルド結果だけを取り出す。

heal_stale_deadlines.py --apply は「生きた枠が消える」と見ると丸ごと適用を見送る。
見送られた分は tmp/heal_stale.json に convert として残っているので、
それを refresh_deadlines_0909.py（**消さない・上書きと追加だけ**）に流す。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

log = open('tmp/heal_apply_noon_0912.txt', encoding='utf-8').read()
sec = log.split('🛡️')[1] if '🛡️' in log else ''
sec = sec.split('🚨🚨')[0]
ids = [int(x) for x in re.findall(r'id=(\d+) ', sec)]

built = json.load(open('tmp/heal_stale.json', encoding='utf-8'))
by = {b['id']: b for b in built}
# 🚨id3853 阪神×広島は外す＝既存が「ビジター専用応援席／一般発売」（全角スラッシュ）で
#   ビルドが半角「/」を返すので、表記ゆれで同じ枠が二重に増える（2026-09-09 と同じ罠）。
EXCLUDE = {3853}  # 7508 は朝に宮城の枠名をぴあの今の呼び名に揃えた＝二重にならないので外さない（外すと今日12:00発売の先行に締切が入らない）
out = []
for i in ids:
    if i in EXCLUDE:
        continue
    b = by.get(i)
    if b and b.get('status') == 'convert' and b.get('tickets'):
        out.append({'id': i, 'tickets': b['tickets']})

json.dump(out, open('tmp/blocked_built_noon_0912.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('ブロックされた %d件 → ビルド結果が取れた %d件 → tmp/blocked_built_noon_0912.json'
      % (len(ids), len(out)))
print('id: %s' % ','.join(str(i) for i in ids))
