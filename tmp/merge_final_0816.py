# -*- coding: utf-8 -*-
"""2バッチ目の最終確定。音楽46件＋演劇の追加分（締切がCUT以降のもの）を合わせて50件にし、idを振り直す。"""
import json, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

WANT = 50
CUT = "2026-08-20"

a = json.load(open('tmp/built_final2_0816.json', encoding='utf-8'))
b = json.load(open('tmp/built3_0816.json', encoding='utf-8'))

def last(e):
    t = e.get('tickets') or []
    return max((x.get('date') or '') for x in t) if t else ''

add, drop = [], []
for e in b:
    (add if last(e) >= CUT else drop).append(e)

merged = a + add
merged.sort(key=lambda e: last(e), reverse=True)     # 締切が遠い順
final = merged[:WANT]
rest = merged[WANT:]

start = 4376
for i, e in enumerate(final):
    e['id'] = start + i

json.dump(final, open('tmp/built_final_all_0816.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("投入 %d件 id %d〜%d" % (len(final), final[0]['id'], final[-1]['id']))
print("_genre内訳:", dict(Counter(e.get('_genre') for e in final)))
print()
print("演劇から足した %d件:" % len(add))
for e in add:
    print("   %s 締切%s" % ((e.get('artist') or '')[:34], last(e)))
print()
print("見送り（締切が近い）%d件:" % len(drop))
for e in drop:
    print("   %s 締切%s" % ((e.get('artist') or '')[:34], last(e) or '(枠なし)'))
if rest:
    print()
    print("見送り（50件の枠に入らず）%d件:" % len(rest))
    for e in rest:
        print("   %s 締切%s" % ((e.get('artist') or '')[:34], last(e)))
