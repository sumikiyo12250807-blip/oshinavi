# -*- coding: utf-8 -*-
"""さだ工務店のツアーを1エントリに畳む（id3477 に 4531 を合流＋大阪1/16を追加）。

ユーザーが楽天の特設ページを持ってきたのがきっかけで見つかった。
ツアーは1エントリにまとめる（[[feedback_tour_consolidate]]）。

🚨畳む前に**url が空の枠へその会場のぴあURLを焼き込む**（[[feedback_tour_per_ticket_url]]）。
   焼き込まないと、押した人が別会場のページへ飛ぶ。
🚨会期は縮めない（[[feedback_show_true_dates_not_sellable_range]]）。
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
WD = '月火水木金土日'
KEEP, GONE = 3477, 4531


def jp(s):
    y, m, d = [int(x) for x in s.split('-')]
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


src = io.open('index.html', encoding='utf-8').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(mm.group(2))
by = {e['id']: e for e in events}
keep, gone = by[KEEP], by[GONE]

# ① それぞれの url 空の枠に、そのエントリの links.pia を焼き込む
burned = 0
for e in (keep, gone):
    u = (e.get('links') or {}).get('pia')
    for t in e.get('tickets') or []:
        if not t.get('url') and u:
            t['url'] = u
            burned += 1

# ② 大阪1/16（ビルド済み）から、その枠だけ取る
osaka = None
for b in json.load(io.open('tmp/built_sadakoumuten_one_0910.json', encoding='utf-8')):
    for t in b['tickets']:
        if '大阪' in (t.get('type') or ''):
            osaka = dict(t)

# ③ 合流
keep['tickets'] = list(keep.get('tickets') or []) + list(gone.get('tickets') or [])
if osaka:
    keep['tickets'].append(osaka)

venues = ['Zepp DiverCity（TOKYO）', 'COMTEC PORTBASE', 'Zepp Namba（OSAKA）']
keep['venue'] = '全国ツアー（%s）' % '／'.join(venues)
keep['prefecture'] = '東京・愛知・大阪'
keep['date'] = '2027-01-22'
keep['dateLabel'] = '%s〜%s %s' % (jp('2027-01-16'), jp('2027-01-22'), keep['prefecture'])
keep['verified'] = True
keep['verifiedAt'] = '2026-09-10'

events = [e for e in events if e['id'] != GONE]

print('id=%s に id=%s を合流。飛び先を焼き込み %d枠' % (KEEP, GONE, burned))
print('  %s' % keep['dateLabel'])
print('  %s' % keep['venue'])
for t in keep['tickets']:
    print('   %-44s date=%s url=%s' % (t['type'][:44], t['date'], (t.get('url') or '(なし)')[:52]))

if '--apply' not in sys.argv:
    print('\n(--apply で書き込み)')
    sys.exit(0)
arr = json.dumps(events, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    src[:mm.start()] + mm.group(1) + arr + mm.group(3) + src[mm.end():])
print('書き込み完了（id%s は欠番）' % GONE)
