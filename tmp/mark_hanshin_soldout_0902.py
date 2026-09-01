# -*- coding: utf-8 -*-
"""阪神タイガースの9エントリに「予定枚数終了」を付ける（消さない）。

実ページの生HTMLの statustext を全券種読んだ結果＝**46枠すべて [予定枚数終了] cls=is-active**、
「受付終了」は1件も無し（tmp/hanshin_status_0902.txt）。
売り切れは消さずに出し続ける決まり（feedback_soldout_keep_visible）。
「予定枚数終了」と「販売終了」は別バッジ（feedback_saleended_vs_soldout）なので
`saleEnded` は付けず、`soldout` + `soldoutSince` だけ付ける。

  python tmp/mark_hanshin_soldout_0902.py [--apply]
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
TODAY = '2026-09-02'
IDS = [3841, 3849, 3858, 3978, 3979, 3980, 3981, 4932, 5123]

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EV = json.loads(m.group(2))
n = 0
for e in EV:
    if e['id'] not in IDS:
        continue
    marked = 0
    for t in (e.get('tickets') or []):
        if t.get('soldout'):
            continue
        t['soldout'] = True
        t['soldoutSince'] = TODAY
        marked += 1
        n += 1
    print(f"id{e['id']} {e.get('artist','')[:40]} … {marked}枠に『予定枚数終了』")
print(f'\n合計 {n}枠  APPLY={APPLY}')
if not APPLY:
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
open('index.html.bak_0902_hanshin', 'w', encoding='utf-8', newline='').write(src)
open('index.html', 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('applied（backup: index.html.bak_0902_hanshin）')
