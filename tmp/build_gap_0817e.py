# -*- coding: utf-8 -*-
"""ビルドで落ちた候補を洗い出し、429が明けてから取り直すための再実行用candを作る。
[[reference_pia_rate_limit_429]]＝harvest→build→reconcileを続けざまに回すと429で静かに壊れる。"""
import io, sys, json
sys.stdout.reconfigure(encoding='utf-8')

cand = json.load(io.open('tmp/cand_0817e.json', encoding='utf-8'))
built = json.load(io.open('tmp/entries_0817e.json', encoding='utf-8'))
ok = {e['id'] for e in built}
ng = [c for c in cand if c['newid'] not in ok]

print('候補 %d件 / 組めた %d件 / 落ちた %d件' % (len(cand), len(ok), len(ng)))
print()
print('落ちたid:', [c['newid'] for c in ng])
json.dump(ng, io.open('tmp/cand_0817e_retry.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ tmp/cand_0817e_retry.json（id据え置きで再実行できる）')

print()
print('=== 組めた25件の枠の状態 ===')
n_no_start = 0
for e in built:
    ts = e.get('tickets') or []
    if not ts:
        print('  ⚠️ id%d 枠ゼロ %s' % (e['id'], e.get('artist', '')))
    for t in ts:
        if not t.get('startDate'):
            n_no_start += 1
print('  枠合計 %d本 / startDate無し %d本' % (sum(len(e.get('tickets') or []) for e in built), n_no_start))
