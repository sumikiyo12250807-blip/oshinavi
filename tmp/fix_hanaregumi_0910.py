# -*- coding: utf-8 -*-
"""id6972 ハナレグミ のジャンルを gakusai（学園祭）から jpop に直す。

2026-09-09 夜にユーザーが発見。ぴあの区分を機械で引き直したら
  eventCd=2636130 → _piaSub「音楽/J-POP・ROCK」＝ jpop
だった（[[feedback_genre_pia_asis_and_other]]＝ぴあの言う通りに写す）。
会場名に「昭和女子大学人見記念講堂」が入っているのが学園祭に化けた原因と思われる。

⚠️ id6441 マルシィ（Zepp Fukuoka）は**直さない**。
   ぴあの区分自体が「イベント/学園祭」＝ gakusai で正しい。会場で判断しない。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

for e in events:
    if e['id'] != 6972:
        continue
    print('id=6972 %s : genre %s → jpop' % (e['name'], e.get('genre')))
    e['genre'] = 'jpop'
    e['_piaSub'] = '音楽/J-POP・ROCK'
    break
else:
    raise SystemExit('id6972 が無い')

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('書き込み完了')
