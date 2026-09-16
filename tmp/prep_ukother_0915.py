# -*- coding: utf-8 -*-
"""受付中（音楽以外6ジャンル）の組み上がり（tmp/built_ukother_0915.json）から、新規で入れる分を取り出す（読むだけ・2026-09-15 昼）。
split_built_ukother0915.txt の結果:
  畳む5件（名前が完全一致）＝merge の試し流しで足す枠0＝全部既存にある＝何もしない
  部分一致7件＝入れない
    二重＝10551 PNC 9/19（3397）／10616 コンサドーレ×大分 9/19（3710）／10631 細田守展 大阪（3629）／
          10662 松崎しげる XmasDS 神奈川（742）／10674 牛田智大 Vol.4 東京（1835）
    保留＝10617・10618 コンサドーレの駐車券だけのページ（券種名に【駐車券】が無いと試合の券と見分けがつかない）
  新規＝名前が既存に無い分（split の「新規」行）
使い方: python tmp/prep_ukother_0915.py
出力: tmp/inject_ukother_0915.json ／ tmp/inject_ukother_ids_0915.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_ukother_0915.json', encoding='utf-8'))}
split = io.open('tmp/split_built_ukother0915.txt', encoding='utf-8').read()
pure_new = sorted(int(m.group(1)) for m in re.finditer(r'^新規\s+new(\d+)', split, re.M))
json.dump([built[i] for i in pure_new], io.open('tmp/inject_ukother_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open('tmp/inject_ukother_ids_0915.txt', 'w', encoding='utf-8').write(','.join(map(str, pure_new)))
for i in pure_new:
    b = built[i]
    print('  new%-6s %-10s %s ｜ %s' % (i, b.get('_genre'), (b.get('name') or '')[:36], b.get('dateLabel')))
print('新規 %d件 → tmp/inject_ukother_0915.json' % len(pure_new))
