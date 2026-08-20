# -*- coding: utf-8 -*-
"""新着プール37件を「実ページから作り直したもの」と突合する（独立再照合）。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

reb = {e['id']: e for e in json.load(io.open('tmp/rebuilt_0821.json', encoding='utf-8'))}
h = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
cur = {e['id']: e for e in EV if e.get('genre') == 'new'}

out = []
P = out.append
P('=== 新着プール 独立再照合 (today=2026-08-21) ===')
P('登録 %d件 / 再構築できた %d件' % (len(cur), len(reb)))
P('')
ng = 0
for i in sorted(cur):
    c = cur[i]
    b = reb.get(i)
    if not b:
        P('❌ id=%d %s ← 再構築できなかった（ぴあが売切/混雑を返した）' % (i, c.get('name')))
        ng += 1
        continue
    msgs = []
    if len(c.get('tickets') or []) != len(b.get('tickets') or []):
        msgs.append('枠数 登録%d ≠ 実%d' % (len(c.get('tickets') or []), len(b.get('tickets') or [])))
    if c.get('date') != b.get('date'):
        msgs.append('公演日 登録%s ≠ 実%s' % (c.get('date'), b.get('date')))
    if (c.get('prefecture') or '') != (b.get('prefecture') or ''):
        msgs.append('県 登録%s ≠ 実%s' % (c.get('prefecture'), b.get('prefecture')))
    if (c.get('venue') or '') != (b.get('venue') or ''):
        msgs.append('会場 登録%s ≠ 実%s' % (c.get('venue'), b.get('venue')))
    ct = [t.get('type') for t in c.get('tickets') or []]
    bt = [t.get('type') for t in b.get('tickets') or []]
    if sorted(ct) != sorted(bt):
        only_c = [x for x in ct if x not in bt]
        only_b = [x for x in bt if x not in ct]
        if only_c:
            msgs.append('登録にしか無い枠: %s' % only_c)
        if only_b:
            msgs.append('実ページにしか無い枠: %s' % only_b)
    if msgs:
        ng += 1
        P('⚠️ id=%d %s' % (i, c.get('name')))
        for m in msgs:
            P('     %s' % m)
    else:
        P('✅ id=%d %s | 枠%d 公演日%s 一致' % (i, (c.get('name') or '')[:30], len(ct), c.get('date')))
P('')
P('=== 一致 %d件 / 要確認 %d件 ===' % (len(cur) - ng, ng))
io.open('tmp/recheck_diff_0821.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/recheck_diff_0821.txt  一致%d / 要確認%d' % (len(cur) - ng, ng))
