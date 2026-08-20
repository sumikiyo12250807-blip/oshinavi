# -*- coding: utf-8 -*-
"""reconcile_pia の QC-EVDATE 指摘を直す＝ev.date(千秋楽)をぴあ実公演に合わせる。

heal_stale_deadlines は tickets しか置換しないので、ぴあ側で公演が伸びていると
ev.date が古いまま残り「まだ買えるのにカードが先に消える」。

  979  ROLL((CAKE))TIME  date 2026-08-20 → 2026-08-24（dateLabelは既に8/20〜8/24なので日付だけ）
  1401 いきものがかり      date 2027-03-27 → 2027-04-03
       ＋残った買える枠が 宮城2/7・福井2/27・石川4/3 の3公演になったので、
         沖縄1公演のままの dateLabel/venue/prefecture をツアー形に直す。
         会場名は ぴあ実ページの機械パース（tmp/pia_rows_0814.py）で確認した実物。
"""
import re, json, io, sys, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
APPLY = '--apply' in sys.argv
WD = '月火水木金土日'


def jp(d):
    y, m, dd = (int(x) for x in d.split('-'))
    w = WD[datetime.date(y, m, dd).weekday()]
    return '%d年%d月%d日(%s)' % (y, m, dd, w)


FIX = {
    979: {'date': '2026-08-24'},
    1401: {
        'date': '2027-04-03',
        'dateLabel': jp('2027-02-07') + '〜' + jp('2027-04-03') + ' 全国ツアー',
        'venue': '全国ツアー（仙台サンプラザホール／フェニックス・プラザ エルピス 大ホール／本多の森北電ホール）',
        'prefecture': '全国',
    },
}

PATH = 'index.html'
h = open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

for e in EV:
    f = FIX.get(e['id'])
    if not f:
        continue
    print('=== id=%d %s' % (e['id'], (e.get('artist') or '')[:20]))
    for k, v in f.items():
        print('   %-11s %s' % (k, e.get(k)))
        print('   %-11s → %s' % ('', v))
        e[k] = v

if not APPLY:
    print('\n（提案のみ。適用は --apply）')
    sys.exit(0)

bak = PATH + '.bak_0814_evdate'
open(bak, 'w', encoding='utf-8', newline='').write(h)
body = json.dumps(EV, ensure_ascii=False, indent=2)
if '\r\n' in h:
    body = body.replace('\r\n', '\n').replace('\n', '\r\n')
open(PATH, 'w', encoding='utf-8', newline='').write(h[:m.start(2)] + body + h[m.end(2):])
print('\n=== 適用した (backup: %s) ===' % bak)
