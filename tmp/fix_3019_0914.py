# -*- coding: utf-8 -*-
"""3019 山本達彦 <Live en Quatre Saisons・Automne>＝会場の公演（9/12・9/13 南青山マンダラ）は終わった。
残るのは e+ Streaming+ の視聴券（アーカイブあり）＝4本とも受付中（2026-09-14 あたしが e+ の実ページで読んだ）:
  4530900001-P0030001P021002＝9/12(土) 開演14:30・受付〜9/18(金)20:00
  4530920001-P0030001P021001＝9/12(土) 開演17:00・受付〜9/18(金)20:00
  4530940001-P0030001P021001＝(昼公演) 9/13(日)〜9/19(土)・受付〜9/19(土)20:00
  4530950001-P0030001P021001＝(夜公演) 9/13(日)〜9/19(土)・受付〜9/19(土)20:00
（朝の削除の独立検証も「e+に配信券あり＝残すべき」と判定＝scratchpad/delcheck_0914_result.json）
やること＝配信の枠4つを足す／date を 9/19 に／配信の決まり（feedback_streaming_events_included）どおり
  name の頭に【動画配信】・venue＝Streaming+（動画配信）・prefecture＝全国
  links.eplus は会場のページ（いまは 404）→ 配信のページに替える。初日 9/12 は触らない（ユーザーに聞く件）。
使い方: python tmp/fix_3019_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 3019)
assert e['date'] == '2026-09-13', e['date']
assert not any('4530900001' in (t.get('url') or '') for t in e['tickets']), '配信の枠はもう入っている'
E = 'https://eplus.jp/sf/detail/'
add = [
    {'type': '先着一般発売【動画配信】（全国 9/12 14:30公演）〜9/18 20:00', 'date': '2026-09-18', 'url': E + '4530900001-P0030001P021002'},
    {'type': '先着一般発売【動画配信】（全国 9/12 17:00公演）〜9/18 20:00', 'date': '2026-09-18', 'url': E + '4530920001-P0030001P021001'},
    {'type': '先着一般発売【動画配信・昼公演】（全国 9/13公演）〜9/19 20:00', 'date': '2026-09-19', 'url': E + '4530940001-P0030001P021001'},
    {'type': '先着一般発売【動画配信・夜公演】（全国 9/13公演）〜9/19 20:00', 'date': '2026-09-19', 'url': E + '4530950001-P0030001P021001'},
]
new = {
    'name': '【動画配信】' + e['name'],
    'date': '2026-09-19',
    'dateLabel': '2026年9月12日(土)〜2026年9月19日(土) 全国 Streaming+（動画配信）',
    'venue': 'Streaming+（動画配信）',
    'prefecture': '全国',
}
for k, v in new.items():
    print('%-10s %s\n        → %s' % (k, e.get(k), v))
    e[k] = v
print('links.eplus %s\n        → %s' % (e['links'].get('eplus'), E + '4530900001-P0030001P021002'))
e['links']['eplus'] = E + '4530900001-P0030001P021002'
for t in add:
    print('足す  %s ｜%s' % (t['type'], t['url']))
e['tickets'].extend(add)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
