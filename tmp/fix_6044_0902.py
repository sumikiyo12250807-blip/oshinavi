# -*- coding: utf-8 -*-
"""id6044 ハナレグミ（Billboard Live TOKYO／OSAKA）を実ページに合わせて直す。

`tools/eplus_detail.py` で4枠とも実ページを読んだ結果（2026-09-02 12:4x 実測）:
  P0030004P021001  2026/11/27 TOKYO  予定枚数終了 | 先着★一般発売 | 9/2 12:00〜11/20 18:00
  P0030004P021002  2026/11/27 TOKYO  予定枚数終了 | 先着★一般発売 | 9/2 12:00〜11/20 18:00
  P0030005P021001  2026/12/13 OSAKA  予定枚数終了 | 先着★一般発売 | 9/2 12:00〜12/6 18:00
  P0030005P021002  2026/12/13 OSAKA  予定枚数終了 | 先着★一般発売 | 9/2 12:00〜12/6 18:00
  P0030002P021001  2026/11/27 TOKYO  受付終了     | 抽選 オフィシャル先行 | 8/7〜8/16
    ＝**t0 に刻まれていたURLはこの「先行」のページ**だった。一般発売の枠に先行のURLが
      付いていた＝押すと別の（もう終わった）受付に着地する。P0030004P021001 へ張り替える。

売り切れは消さずに「予定枚数終了」で出し続ける（feedback_soldout_keep_visible）。
「販売終了」ではないので saleEnded は付けない（feedback_saleended_vs_soldout）。

  python tmp/fix_6044_0902.py [--apply]
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
TODAY = '2026-09-02'
FIX_URL = ('https://eplus.jp/sf/detail/4306490002-P0030002P021001',
           'https://eplus.jp/sf/detail/4306490002-P0030004P021001')

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EV = json.loads(m.group(2))
n = 0
for e in EV:
    if e['id'] != 6044:
        continue
    for j, t in enumerate(e['tickets']):
        if t.get('url') == FIX_URL[0]:
            print(f"  t{j} URL張り替え: …{FIX_URL[0][-20:]} → …{FIX_URL[1][-20:]}")
            t['url'] = FIX_URL[1]
        if not t.get('soldout'):
            t['soldout'] = True
            t['soldoutSince'] = TODAY
            n += 1
            print(f"  t{j} 予定枚数終了を付けた: {t.get('type')}")
print(f'\n{n}枠に「予定枚数終了」  APPLY={APPLY}')
if not APPLY:
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
open('index.html.bak_0902_6044', 'w', encoding='utf-8', newline='').write(src)
open('index.html', 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('applied（backup: index.html.bak_0902_6044）')
