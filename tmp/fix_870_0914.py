# -*- coding: utf-8 -*-
"""id870 CREATURE CREATURE に、ツアーの続き＝渋谷9/20 Veats Shibuya（eventCd=2622622・一般発売〜9/15）を入れる（2026-09-14 朝）。

経緯＝削除の検証（別エージェント・反証目線）で「9/13名古屋は終わったが、同じアーティストの9/20渋谷が販売中」と出た。
index.html に 2622622 は1つも無い＝未登録。名古屋の枠は公演が終わっているので、
「これから行われる公演だけを入れる」決まり（memory feedback_show_true_dates_not_sellable_range）に沿って渋谷に入れ替える。
🚨足す枠には必ずそのページのURLを焼き込む（memory feedback_tour_per_ticket_url／merge_with_urls_0912.py の教訓）。
ジャンル（rock）は振り分け済みなので触らない。

使い方: python tmp/fix_870_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B  # noqa: E402

ID = 870
URL = 'https://t.pia.jp/pia/event/event.do?eventCd=2622622'

built = B.build({'newid': ID, 'artist': 'CREATURE CREATURE', 'urls': [URL]})
if not built or not built.get('tickets'):
    print('⚠️ 渋谷の枠が組めなかった＝何もしない')
    sys.exit(1)
tks = built['tickets']
for t in tks:
    t['url'] = URL
print('組めた枠 %d本 / date=%s / venue=%s / 県=%s' % (len(tks), built['date'], built['venue'], built['prefecture']))
print('dateLabel=%s' % built['dateLabel'])
for t in tks:
    print('   %s | start=%s date=%s' % (t.get('type'), t.get('startDate'), t.get('date')))

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == ID)
print('いまの登録: date=%s venue=%s 枠%d本' % (e.get('date'), e.get('venue'), len(e.get('tickets') or [])))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

e['tickets'] = tks
e['date'] = built['date']
e['dateLabel'] = built['dateLabel']
e['venue'] = built['venue']
e['prefecture'] = built['prefecture']
e.setdefault('links', {})['pia'] = URL
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了')
