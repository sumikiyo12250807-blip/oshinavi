# -*- coding: utf-8 -*-
"""枠1つだけに売り切れの印を付ける（2026-09-12 昼）。消さない＝soldout:true ＋ soldoutSince（DELETE_GATE 1.）。
tools/mark_soldout.py はエントリ単位で「ぴあに買える枠があるか」を見るので、同じエントリの中で1会場だけ売り切れた型を拾えない。
根拠＝ぴあの生HTMLの状態の文字（tools/pia_statustext.py・tmp/statustext_bundle_0912.py の出力）:
  id4500 MONO NO AWARE 京都 R9年1/23 磔磔 … eventCd=2628450 で「予定枚数終了」（tmp/statustext_4500kyoto_0912.txt）
  id3522 カルロス・トシキ 愛知 11/24 名古屋クラブクアトロ … eventCd=2627248 で「予定枚数終了」（tmp/statustext_3522_0912.txt）
  （どちらも別エージェントの抜き取りで先に見つかった）
使い方: python tmp/mark_ticket_soldout_0912.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-12'
TARGETS = [(4500, '（京都 R9年 1/23公演）'), (3522, '（愛知 11/24公演）')]

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
n = 0
for i, key in TARGETS:
    hit = [t for t in by[i]['tickets'] if key in (t.get('type') or '') and not t.get('soldout')]
    print('id%s %s → 当たる枠 %d' % (i, key, len(hit)))
    for t in hit:
        print('   %s | date=%s' % (t['type'], t.get('date')))
        t['soldout'] = True
        t['soldoutSince'] = TODAY
        n += 1
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了 %d枠' % n)
