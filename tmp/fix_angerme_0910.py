# -*- coding: utf-8 -*-
"""id4490 アンジュルム（全国ツアー）に、抜けていた2公演を足す。

■ 見つけ方
ローチケの週スキャン（9/21〜9/27発売）で「載っているが、その窓に発売が始まる枠が無い」に出た。
中を見たら**会場ごと2つ落ちていた**。

■ 実測（2026-09-10）
  ぴあ b2670340 …  [受付中] 2026-09-29 千葉県 森のホール２１ 大ホール  一般発売  〜9/27(日)23:59
                   🚨**締切まであと2日**なのに、うちに無かった
  ローチケ      …  2026/11/11(水) 札幌市教育文化会館 大ホール（北海道）
                   先着 一般発売 発売前 2026/9/27(日)10:00 〜 2026/11/8(日)22:00
                   lcode=11604 / pfkeys=20260731000002263530 / sn=1 / mthd=01 / venuecd=12704

■ 会期
登録の会期は「2026年9月20日(日)〜2026年11月15日(日) 全国ツアー」＝**両方この中に入る**ので、
dateLabel と date は変えない。venue にだけ2会場を足す（機械のunionでなく手で書く）。
"""
import io
import json
import re
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')

PIA = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670340'
LT_SAPPORO = ('https://l-tike.com/order/?gLcode=11604&gPfKey=20260731000002263530'
              '&gEntryMthd=01&gScheduleNo=1&gCarrierCd=08&gPfName='
              + quote('アンジュルム') + '&gBaseVenueCd=12704')

NEW_VENUE = ('全国ツアー（長野市芸術館 メインホール／倉敷市民会館／水戸市民会館 グロービスホール／'
             'Niterra日本特殊陶業市民会館 フォレストホール／NHK大阪ホール／仙台サンプラザホール／'
             'シンフォニアテクノロジー響ホール伊勢 大ホール／森のホール21 大ホール／'
             '札幌市教育文化会館 大ホール）')

SLOTS = [
    {"type": "一般発売（千葉 9/29公演）〜9/27 23:59",
     "date": "2026-09-27", "url": PIA},
    {"type": "一般発売（北海道 11/11公演）9/27 10:00発売",
     "startDate": "2026-09-27", "date": "2026-09-27", "url": LT_SAPPORO},
]

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

target = None
for e in events:
    if e['id'] == 4490:
        target = e
        break
if target is None:
    print('!! id4490 が無い')
    sys.exit(1)

have = {(t.get('url') or '') for t in target.get('tickets') or []}
kinds = {(t.get('type') or '') for t in target.get('tickets') or []}
added = 0
for s in SLOTS:
    if s['type'] in kinds:
        print('  すでにある: %s' % s['type'])
        continue
    target.setdefault('tickets', []).append(s)
    print('  足した: %s' % s['type'])
    added += 1

if not added:
    print('足すものが無かった')
    sys.exit(0)

target['venue'] = NEW_VENUE
print('  枠数 %d → %d' % (len(target['tickets']) - added, len(target['tickets'])))
print('  venue に 森のホール21 と 札幌市教育文化会館 を足した')
print('  dateLabel と 公演日は変えない（%s ／ %s）'
      % (target.get('dateLabel'), target.get('date')))

out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('書き込み完了')
