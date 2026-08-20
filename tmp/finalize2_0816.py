# -*- coding: utf-8 -*-
"""2バッチ目：build済み70件から投入する50件を決めてidを振り直す。
全部が受付中なので「もうじき締切る子は載せない」＝最も遅い締切が CUT 以降のものだけ。
"""
import json, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

WANT = 50
CUT = "2026-08-20"

built = json.load(open('tmp/built2_0816.json', encoding='utf-8'))
alive, dropped = [], []
for e in built:
    tks = e.get('tickets') or []
    last = max((t.get('date') or '') for t in tks) if tks else ''
    if last and last >= CUT:
        alive.append((e, last))
    else:
        dropped.append((e['id'], (e.get('artist') or '')[:26], last or '(枠なし)'))

alive.sort(key=lambda x: x[1], reverse=True)     # 締切が遠い順
final = [e for e, _ in alive[:WANT]]
rest = [(e['id'], (e.get('artist') or '')[:26], d) for e, d in alive[WANT:]]

start = 4376
for i, e in enumerate(final):
    e['id'] = start + i

json.dump(final, open('tmp/built_final2_0816.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("投入 %d件 id %d〜%d" % (len(final), final[0]['id'], final[-1]['id']))
print("_genre内訳:", dict(Counter(e.get('_genre') for e in final)))
print()
print("見送り（締切が近い）%d件:" % len(dropped))
for r in dropped:
    print("   id%s %s 締切%s" % r)
print("見送り（50件の枠に入らず）%d件" % len(rest))
