# -*- coding: utf-8 -*-
"""id4340 ENPLEX × Hello! Project 名古屋定期イベント の手当て。
・dateLabel が中止公演(5/25)を起点にしていた → 生きた枠(9/3・9/7)に合わせる
  根拠＝ぴあ b2449029 実ページ。5/25は「この公演は中止になりました」、7/17は「販売終了」。
  reconcile の DROP 2件はこの中止/終了枠で、取り込まないのが正しいと裏取りできた。
・_genre 下書きが fes だったが屋内の映画館イベントで fes の定義(複数組＋屋外)に合わない → idol
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e.get('id') != 4340:
        continue
    print("before dateLabel:", e['dateLabel'], "/ _genre:", e.get('_genre'))
    e['dateLabel'] = "2026年9月3日(木)〜2026年9月7日(月) 愛知 ミッドランドスクエア シネマ2 スクリーン8"
    e['_genre'] = "idol"
    print("after  dateLabel:", e['dateLabel'], "/ _genre:", e.get('_genre'))
    break
else:
    print("id4340 が見つからない"); sys.exit(1)

bak = 'index.html.bak_0816_fix4340'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr.replace('\n', '\r\n') + m.group(3) + h[m.end():])
print("=== 適用 ===")
