# -*- coding: utf-8 -*-
"""id7753「僕らの時代じゃない」に、抜けていた東京公演（紀伊國屋ホール）を足す。

■ ぴあの実ページ（b2670567・2026-09-10 実測）
  [受付中] 11/14〜11/16 京都劇場（京都）      プレイガイド最速先行  〜9/15 23:59   … 登録済み
  [受付中] 11/7〜11/8  穂の国とよはし芸術劇場PLAT 主ホール（愛知）      〜9/16 23:59   … 登録済み
  [発売前] 10/8〜10/27 紀伊國屋ホール（東京）  一般発売  9/13(日)10:00より発売  … 🚨**会場ごと無かった**

■ 直すもの
  会期が 11/7〜11/16 → **10/8〜11/16** に広がる。
  公演日は「事実の会期」で書く（[[feedback_show_true_dates_not_sellable_range]]）。
  🚨venue は機械の union で作らない＝**手で書く**（過去に別エントリを壊した）。
  最終公演日（date）は 2026-11-16 のまま変わらない。
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WD = '月火水木金土日'


def jp(d):
    dt = datetime.date.fromisoformat(d)
    return '%d年%d月%d日(%s)' % (dt.year, dt.month, dt.day, WD[dt.weekday()])


NEW_LABEL = '%s〜%s 東京・京都・愛知' % (jp('2026-10-08'), jp('2026-11-16'))
NEW_VENUE = '全国ツアー（紀伊國屋ホール／京都劇場／穂の国とよはし芸術劇場PLAT 主ホール）'
NEW_PREF = '東京・京都・愛知'
SLOT = {
    "type": "一般発売（東京 10/8〜10/27公演）9/13 10:00発売",
    "startDate": "2026-09-13",
    "date": "2026-09-13",
    "url": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670567",
}

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

target = None
for e in events:
    if e['id'] == 7753:
        target = e
        break
if target is None:
    print('!! id7753 が無い')
    sys.exit(1)

print('いま:')
print('  dateLabel = %s' % target.get('dateLabel'))
print('  venue     = %s' % target.get('venue'))
print('  pref      = %s / date = %s' % (target.get('prefecture'), target.get('date')))
for t in target.get('tickets') or []:
    print('  - %s' % (t.get('type') or ''))

if any('東京' in (t.get('type') or '') for t in target.get('tickets') or []):
    print('→ 東京の枠が既にある。何もしない')
    sys.exit(0)

target['dateLabel'] = NEW_LABEL
target['venue'] = NEW_VENUE
target['prefecture'] = NEW_PREF
target.setdefault('tickets', []).append(SLOT)

print('')
print('直したあと:')
print('  dateLabel = %s' % target['dateLabel'])
print('  venue     = %s' % target['venue'])
print('  pref      = %s / date = %s（最終公演日は変わらない）'
      % (target['prefecture'], target.get('date')))
print('  足した枠  = %s' % SLOT['type'])

out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('書き込み完了')
