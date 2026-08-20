# -*- coding: utf-8 -*-
"""id4333 薬師丸ひろ子の手当て（昼ヒールの安全弁が正しく働いたケース）。
ぴあ b2668840 実ページ（14:30時点）の実態:
  予定枚数終了 = 千葉9/4 / 香川9/9 / 栃木9/13 / 愛知9/19-20 / 静岡9/23 / 埼玉9/29
  買える       = 長野9/30「本日発売初日 〜2026/9/14(月)23:59」
  抽選受付中   = プレリザーブ最終(北海道・山形・福岡 10/18〜11/20)〜8/25 23:00 ← 登録済み
mark_soldout はエントリ一括で付けるため長野の生き枠を巻き込む。ここは枠ごとに手で当てる。
"""
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

TODAY = "2026-08-16"
SOLDOUT_KEYS = ["千葉 9/4", "香川 9/9", "栃木 9/13", "愛知 9/19", "静岡 9/23", "埼玉 9/29"]

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    if e.get('id') != 4333:
        continue
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if any(k in ty for k in SOLDOUT_KEYS):
            if not t.get('soldout'):
                t['soldout'] = True
                t['soldoutSince'] = TODAY
                print("予定枚数終了 →", ty)
        elif "長野 9/30" in ty:
            t['type'] = "一般発売（長野 9/30公演）〜9/14 23:59"
            t['date'] = "2026-09-14"
            t.pop('startDate', None)
            print("販売中に変換 →", t['type'], t['date'])
    e['tickets'].sort(key=lambda t: (t.get('date') or ''))
    break
else:
    print("id4333 が見つからない"); sys.exit(1)

bak = 'index.html.bak_0816_fix4333'
if not os.path.exists(bak):
    open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr.replace('\n', '\r\n') + m.group(3) + h[m.end():])
print("=== 適用 ===")
