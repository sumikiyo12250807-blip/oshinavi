# -*- coding: utf-8 -*-
"""id51 俺だけレベルアップな件 展＝最終日が 11/1 に伸びていたのを、公式の会期 9/27 に戻す（2026-09-14）。
公式（sololeveling-exhibition.com）とぴあ特設ページ（t.pia.jp/pia/events/sololeveling-ex/）の会期はどちらも 7/17〜9/27・延長の記載なし。
ぴあのスーパーパス前売券のカードだけが「7/17〜11/1 公演・〜11/1 20:00」になっていて、足し込みの時にそれで最終日が伸びた。
特設ページのスーパーパスの販売期間は「展示終了日まで」＝9/27。公演日より後の締切は公演日で締める（feedback_sale_end_cap_show_date）。
締切の時刻は公式に書いていないので入れない（推測で入れない）。
初日（9/19）は触らない＝開催中の展覧会の初日をどう書くかはユーザーに聞く。
使い方: python tmp/fix_51_0914.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 51)
assert e['date'] == '2026-11-01', e['date']
hit = [t for t in e['tickets'] if t['type'] == '一般発売（東京 7/17〜11/1公演）〜11/1 20:00']
assert len(hit) == 1, [t['type'] for t in e['tickets']]
t = hit[0]
print('枠   %s (%s)' % (t['type'], t['date']))
t['type'] = '一般発売【スーパーパス前売券】（東京 7/17〜9/27公演）〜9/27'
t['date'] = '2026-09-27'
print('  → %s (%s)' % (t['type'], t['date']))
print('date %s → 2026-09-27' % e['date'])
e['date'] = '2026-09-27'
old = e['dateLabel']
assert '2026年11月1日(日)' in old, old
e['dateLabel'] = old.replace('2026年11月1日(日)', '2026年9月27日(日)')
print('dateLabel %s → %s' % (old, e['dateLabel']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
