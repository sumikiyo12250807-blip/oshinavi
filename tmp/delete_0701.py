# -*- coding: utf-8 -*-
"""7/1 削除実行: 期限切れ削除候補20件を index.html から除去。
A=公演終了確定2件(313,401) / B=先行終了で買える枠ゼロ17件 / C=楽天検証外1件(7)。
ユーザーOK「全部削除でいい」(2026-07-01)。EVENTS は json.dumps(indent=2) 形式で書き戻す。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DEL = set([7, 152, 233, 313, 401, 420, 796, 912, 934, 1170, 1207,
           1414, 1418, 1420, 1429, 1449, 1450, 1488, 1526, 1530])

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

before = len(EVENTS)
gone = [e['id'] for e in EVENTS if e['id'] in DEL]
kept = [e for e in EVENTS if e['id'] not in DEL]
missing = DEL - set(gone)
print(f"削除対象{len(DEL)} / 実削除{len(gone)} / DB未在{sorted(missing)}")
print(f"件数 {before} → {len(kept)}")

new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
open('index.html.bak_0701_morning_delete', 'w', encoding='utf-8').write(h)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(h2)
print("✅ 削除完了 (backup: index.html.bak_0701_morning_delete)")
