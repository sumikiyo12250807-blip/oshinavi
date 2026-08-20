# -*- coding: utf-8 -*-
"""QC-EVDATE 第2弾＝ヒールで枠が伸びたのに ev.date が古いままの3件を直す。

根拠＝reconcile_pia が実ぴあから出した千秋楽／登録tickets の（県 M/D公演）。
dateLabel は登録枠の範囲に合わせて端を伸ばすだけ（会場名は捏造しない・venueは触らない）。

  2744 大橋ちっぽけ  date 11/3 → 11/20（買える枠＝東京11/20のみ）
  3472 M-line       date 11/3 → 11/21（買える枠＝愛知11/21のみ）
  4095 稲葉浩志      date 12/13 → 12/20（15枠＝群馬10/4〜石川12/20・県は全国へ）
"""
import re, json, io, sys, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv
WD = '月火水木金土日'


def jp(d):
    y, m, dd = (int(x) for x in d.split('-'))
    return '%d年%d月%d日(%s)' % (y, m, dd, WD[datetime.date(y, m, dd).weekday()])


FIX = {
    2744: {'date': '2026-11-20',
           'dateLabel': jp('2026-09-13') + '〜' + jp('2026-11-20') + ' 全国ツアー'},
    3472: {'date': '2026-11-21',
           'dateLabel': jp('2026-10-31') + '〜' + jp('2026-11-21') + ' 全国ツアー'},
    4095: {'date': '2026-12-20',
           'dateLabel': jp('2026-10-04') + '〜' + jp('2026-12-20') + ' 全国ツアー',
           'prefecture': '全国'},
}

PATH = 'index.html'
h = open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

for e in EV:
    f = FIX.get(e['id'])
    if not f:
        continue
    print('=== id=%d %s' % (e['id'], (e.get('artist') or '')[:24]))
    for k, v in f.items():
        print('   %-10s %s' % (k, e.get(k)))
        print('   %-10s → %s' % ('', v))
        e[k] = v

if not APPLY:
    print('\n（提案のみ。適用は --apply）')
    sys.exit(0)

bak = PATH + '.bak_0814_evdate2'
open(bak, 'w', encoding='utf-8', newline='').write(h)
body = json.dumps(EV, ensure_ascii=False, indent=2)
if '\r\n' in h:
    body = body.replace('\r\n', '\n').replace('\n', '\r\n')
open(PATH, 'w', encoding='utf-8', newline='').write(h[:m.start(2)] + body + h[m.end(2):])
print('\n=== 適用した (backup: %s) ===' % bak)
