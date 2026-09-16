# -*- coding: utf-8 -*-
"""楽天の「販売の終わりが書かれていない枠」を決まりの形にそろえる（2026-09-11 ユーザー依頼）。
決まり＝[[feedback_sale_end_unknown_display]]：
  saleEndUnknown:true ＋ startDate（発売日）＋ date（画面から消えないための下限＝千秋楽）
  券種名の末尾は「M/D HH:MM発売〜」（時刻が書かれていなければ「M/D発売〜」）
実ページ（2026-09-11 読み直し）:
  id3674 クーザ rtfjscy … 「先行発売日 2026年9月12日(土)～」「一般発売日 2026年9月19日(土)～」（時刻・終わりなし）
     → 今は date=発売日＝発売日の翌日に画面から消える形だった
  id7582 たまがわ花火 rtb9s48 … 「一般販売 7月26日(日)午後2時 ～ (先着順)」（終わりなし）
     → 発売日が入っていなかった
使い方: python tmp/fix_rakuten_unknown_0911.py [--apply]
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
FIX = {
    (3674, '先行発売（東京 R9年 2/24〜4/25公演）9/12発売'):
        {'type': '先行発売（東京 R9年 2/24〜4/25公演）9/12発売〜', 'startDate': '2026-09-12', 'date': '2027-04-25'},
    (3674, '一般発売（東京 R9年 2/24〜4/25公演）9/19発売'):
        {'type': '一般発売（東京 R9年 2/24〜4/25公演）9/19発売〜', 'startDate': '2026-09-19', 'date': '2027-04-25'},
    (7582, '一般販売（東京 10/3公演）'):
        {'type': '一般販売（東京 10/3公演）7/26 14:00発売〜', 'startDate': '2026-07-26', 'date': '2026-10-03'},
}
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
ev = json.loads(m.group(2))
n = 0
for e in ev:
    for t in e.get('tickets') or []:
        f = FIX.get((e['id'], t.get('type')))
        if f:
            print('id%s %s (date=%s start=%s)' % (e['id'], t['type'], t.get('date'), t.get('startDate')))
            t.update(f)
            t['saleEndUnknown'] = True
            print('   → %s (date=%s start=%s saleEndUnknown)' % (t['type'], t['date'], t['startDate']))
            n += 1
print('直す枠 %d/%d' % (n, len(FIX)))
if '--apply' in sys.argv and n == len(FIX):
    open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + json.dumps(ev, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
    print('書き込み完了')
