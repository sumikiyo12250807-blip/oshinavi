# -*- coding: utf-8 -*-
"""9855 反田恭平 ピアノリサイタル 2026＝会期が「買える枠の範囲」（10/24〜11/13）に縮んでいたのを、事実の会期に直す（2026-09-14）。
根拠＝ぴあ b2668259 を pia_tickets.py --all で全券種読んだ（あたしが自分で）＝これからの公演は 10/24 新潟〜12/14 静岡（富士宮市民文化会館）。
  売り切れ・会員先行だけの公演（東京すみだ10/28・神奈川11/6・青森11/8・愛知11/9・東京芸術劇場11/10・大阪11/14・福岡11/22・静岡12/14）も
  これから行われる公演なので会期に入れる（feedback_show_true_dates_not_sellable_range）。枠（tickets）と会場の一覧は触らない。
使い方: python tmp/fix_9855_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 9855)
assert e['date'] == '2026-11-13', e['date']
new = {'date': '2026-12-14', 'dateLabel': '2026年10月24日(土)〜2026年12月14日(月) 全国ツアー'}
for k, v in new.items():
    print('%-10s %s → %s' % (k, e.get(k), v))
    e[k] = v
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
