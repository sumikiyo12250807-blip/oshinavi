# -*- coding: utf-8 -*-
"""あたしの決定表と、独立検証エージェントの判定を機械で突き合わせる。
一致しない件は「振り分けない（保留）」に落ちているかを確認する
（[[feedback_selfrun_gates_only_two]] A＝疑義ゼロ／B＝割れたら止めて報告）。"""
import io, sys, json
sys.stdout.reconfigure(encoding='utf-8')

dec = json.load(io.open('tmp/decision_0817b.json', encoding='utf-8'))
mine = {int(k): v for k, v in dec['assign'].items()}
hold = set(dec['hold'])
res = json.load(io.open('tmp/verify_result_0817b.json', encoding='utf-8'))
theirs = {a['id']: a.get('genre') for a in res.get('assignments', [])}
conf = {a['id']: a.get('confidence') for a in res.get('assignments', [])}
unsure = {u['id'] for u in res.get('unsure', [])}

merged_away = {4446, 4477, 4478}

print('=== 突き合わせ ===')
agree = dis = 0
for eid in sorted(set(mine) | set(theirs)):
    if eid in merged_away:
        continue
    m, t = mine.get(eid), theirs.get(eid)
    if eid in hold:
        continue
    if m is None:
        print('  ⚠️ id%-5d あたしの表に無い（エージェント=%s）' % (eid, t)); dis += 1
    elif t is None:
        print('  ⚠️ id%-5d エージェントの表に無い（あたし=%s）' % (eid, m)); dis += 1
    elif m != t:
        print('  ❌ id%-5d 割れた: あたし=%-9s エージェント=%-9s' % (eid, m, t)); dis += 1
    else:
        agree += 1

print('  一致 %d件 / 不一致 %d件' % (agree, dis))

print()
print('=== 保留(hold)にした %d件が、割れ/低確信を全部拾えているか ===' % len(hold))
risky = {eid for eid in theirs if conf.get(eid) == 'low'} | unsure
risky |= {eid for eid in set(mine) | set(theirs)
          if eid not in merged_away and mine.get(eid) and theirs.get(eid) and mine[eid] != theirs[eid]}
for eid in sorted(risky):
    mark = '✅保留' if eid in hold else '🚨振り分けようとしている'
    print('  id%-5d %s  (あたし=%s / エージェント=%s / 確信=%s)'
          % (eid, mark, mine.get(eid, '-'), theirs.get(eid, '-'), conf.get(eid, '-')))
leak = sorted(risky - hold)
print()
print('取りこぼし:', leak or 'なし')
print('重複としてエージェントが挙げた組:', [d['ids'] for d in res.get('duplicates', [])])
sys.exit(1 if (dis or leak) else 0)
