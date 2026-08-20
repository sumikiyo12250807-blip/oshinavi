# -*- coding: utf-8 -*-
"""build済み71件から投入する50件を決めてidを振り直す。
・発売前(rlsIn=03/04)の子は全部残す
・受付中(music_onsale)は「もうじき締切る子は載せない」＝最も遅い締切が CUT 以降のものだけ
  （feedback_presale_first_harvest のローリング判断。今日8/16なので8/20を線にする）
"""
import json, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

WANT = 50
CUT = "2026-08-20"

built = json.load(open('tmp/built_0816.json', encoding='utf-8'))
cand = {c['newid']: c for c in json.load(open('tmp/cand_pick_0816.json', encoding='utf-8'))}

presale, onsale, dropped = [], [], []
for e in built:
    grp = (cand.get(e['id']) or {}).get('_grp', '?')
    last = max((t.get('date') or '') for t in e.get('tickets') or []) if e.get('tickets') else ''
    if grp == 'music_onsale':
        if last and last >= CUT:
            onsale.append((e, last))
        else:
            dropped.append((e['id'], e.get('artist', '')[:26], last, '締切が近い'))
    else:
        presale.append(e)

need = WANT - len(presale)
onsale.sort(key=lambda x: x[1], reverse=True)      # 締切が遠い順
take = [e for e, _ in onsale[:max(0, need)]]
rest = [(e['id'], e.get('artist', '')[:26], d, '50件の枠に入らず') for e, d in onsale[max(0, need):]]

final = presale + take
start = 4326
for i, e in enumerate(final):
    e['id'] = start + i

json.dump(final, open('tmp/built_final_0816.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("投入 %d件（発売前 %d + 受付中 %d）id %d〜%d" % (
    len(final), len(presale), len(take), final[0]['id'], final[-1]['id']))
print("_genre内訳:", dict(Counter(e.get('_genre') for e in final)))
print()
print("見送り %d件:" % (len(dropped) + len(rest)))
for r in dropped + rest:
    print("   id%s %s 締切%s ← %s" % r)
