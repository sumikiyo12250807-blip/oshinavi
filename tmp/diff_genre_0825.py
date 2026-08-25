# -*- coding: utf-8 -*-
"""あたしの下書き(_genre)と、検証エージェントが独立に出したジャンルを突合。
割れた件・エージェントが confidence 低 と言った件は**振り分けずプールに残す**
（[[feedback_new_pool_ok_before_assign]]／[[feedback_consultation_mark]]）。"""
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

plan = json.load(io.open('tmp/assign_plan_0825.json', encoding='utf-8'))
mine = {str(r['id']): r for r in plan['auto']}
theirs = json.load(io.open('tmp/genre_out_0825.json', encoding='utf-8'))

split, lowconf, agree = [], [], []
for k, r in sorted(mine.items(), key=lambda kv: int(kv[0])):
    t = theirs.get(k)
    if not t:
        split.append((k, r, None, '検証結果が無い'))
        continue
    if t.get('genre') != r['genre']:
        split.append((k, r, t, '判定が割れた'))
    elif t.get('confidence') == '低':
        lowconf.append((k, r, t))
    else:
        agree.append((k, r, t))

print('=== 一致(confidence高/中) %d件 / 判定が割れた %d件 / 低confidence %d件 ===' %
      (len(agree), len(split), len(lowconf)))
print('\n--- 🚨判定が割れた（振り分けない） ---')
for k, r, t, why in split:
    print('id%-5s %-40s あたし=%-9s 相手=%-9s [%s]' % (
        k, r['name'][:38], r['genre'], (t or {}).get('genre'), r['sub']))
    if t and t.get('note'):
        print('        理由: %s' % t['note'][:120])
print('\n--- ⚠️低confidence（振り分けない） ---')
for k, r, t in lowconf:
    print('id%-5s %-40s → %-9s [%s]' % (k, r['name'][:38], r['genre'], r['sub']))
    if t.get('note'):
        print('        理由: %s' % t['note'][:120])

hold = sorted(set([k for k, *_ in split] + [k for k, *_ in lowconf]), key=int)
json.dump({'apply': [{'id': int(k), 'name': mine[k]['name'], 'genre': mine[k]['genre'],
                      'sub': mine[k]['sub'], 'url': mine[k]['url'],
                      'extra': mine[k]['extra']} for k, *_ in [(x[0],) for x in agree]],
           'hold': hold},
          open('tmp/assign_decided_0825.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n振り分ける %d件 / 保留 %d件 → tmp/assign_decided_0825.json' % (len(agree), len(hold)))
print('保留id:', ','.join(hold))
