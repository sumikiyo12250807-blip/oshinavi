# -*- coding: utf-8 -*-
"""6/29 削除実行: B組(6/28公演終了)10件 + 先行終了38件 = 48件を index.html から除去。
ユーザーOK「全部削除」(2026-06-29)。EVENTS は json.dumps(indent=2) 形式で書き戻す。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

B = [64, 368, 385, 391, 469, 480, 1343, 1348, 1356, 1369]
D = [316, 474, 577, 918, 1146, 1168, 1189, 1194, 1250, 1286, 1393, 1396, 1399,
     1403, 1406, 1408, 1415, 1421, 1422, 1424, 1434, 1437, 1439, 1442, 1461,
     1469, 1471, 1476, 1498, 1499, 1505, 1510, 1512, 1513, 1515, 1536, 1538, 1540]
DEL = set(B + D)

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
open('index.html.bak_0629_morning_delete', 'w', encoding='utf-8').write(h)
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
open('index.html', 'w', encoding='utf-8').write(h2)
print("✅ 削除完了 (backup: index.html.bak_0629_morning_delete)")
