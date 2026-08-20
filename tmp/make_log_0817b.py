# -*- coding: utf-8 -*-
"""振り分け結果を logs/ に追記する（[[feedback_new_pool_ok_before_assign]] C＝後から見られるリンクを残す）。
新着タブが空になる代わりの「見る場所」なので、公演名＋ジャンル＋確認用URLを必ず入れる。"""
import io, os, re, sys, json, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

dec = json.load(io.open('tmp/decision_0817b.json', encoding='utf-8'))
ASSIGN = {int(k): v for k, v in dec['assign'].items()}
HOLD = dec['hold']
WHY = dec['hold_reason']

idx = io.open('index.html', encoding='utf-8').read()
EV = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))}

L = []
L.append('')
L.append('---')
L.append('')
L.append('## 🕐 8/17 昼の便（ユーザー指示「今日の新着はこのまま、振り分けて」）')
L.append('')
L.append('### ツアー統合 3組（同じツアーが2エントリに割れていた）')
for keep, absorb in [(4436, 4446), (4450, 4477), (4455, 4478)]:
    e = EV[keep]
    L.append('- **id%d %s** ← id%d を統合／%s／%s' % (keep, e.get('artist', ''), absorb,
                                                      e.get('prefecture', ''), e.get('dateLabel', '')))
    for t in e.get('tickets') or []:
        L.append('  - %s → %s' % (t.get('type', ''), t.get('url', '')))
L.append('')
L.append('### 振り分け %d件' % len(ASSIGN))
by = collections.defaultdict(list)
for eid, g in ASSIGN.items():
    by[g].append(eid)
for g in sorted(by, key=lambda x: (-len(by[x]), x)):
    L.append('')
    L.append('**%s（%d件）**' % (g, len(by[g])))
    L.append('')
    L.append('| id | 公演名 | 都道府県 | 公演日 | 確認用URL |')
    L.append('|---|---|---|---|---|')
    for eid in sorted(by[g]):
        e = EV[eid]
        L.append('| %d | %s | %s | %s | %s |' % (
            eid, e.get('artist', '').replace('|', '｜'), e.get('prefecture', ''),
            e.get('date', ''), (e.get('links') or {}).get('pia', '')))
L.append('')
L.append('### ⏸ 振り分けなかった %d件（相談待ち・新着タブに残置）' % len(HOLD))
L.append('')
L.append('| id | 公演名 | 確認用URL | 相談内容 |')
L.append('|---|---|---|---|')
for eid in HOLD:
    e = EV.get(eid)
    if not e:
        continue
    L.append('| %d | %s | %s | %s |' % (
        eid, e.get('artist', '').replace('|', '｜'), (e.get('links') or {}).get('pia', ''),
        WHY.get(str(eid), '')))
L.append('')
L.append('### 検証（[[feedback_selfrun_gates_only_two]] A）')
L.append('- 別エージェントに**あたしの判定を見せず**50件をゼロから再導出させた → **一致42件・不一致0件**')
L.append('- エージェントが「低確信」を付けた件・判定が割れた件は**全部保留に落とした**（取りこぼしゼロを機械照合）')
L.append('- 4456 AGLEE はエージェントが hiphop と言ったが、ぴあ実ページには出演「BARK」としか無く**裏が取れないので保留**')

p = 'logs/assigned_2026-08-17.md'
old = io.open(p, encoding='utf-8').read() if os.path.exists(p) else '# 振り分け記録 2026-08-17\n'
io.open(p, 'w', encoding='utf-8').write(old.rstrip('\n') + '\n' + '\n'.join(L) + '\n')
print('追記しました → %s（%d行）' % (p, len(L)))
