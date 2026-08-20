# -*- coding: utf-8 -*-
"""今日の削除候補のURL・枠を機械抽出（捏造禁止＝index.htmlの実データのみ）"""
import io, json, re

A = [1272, 1443, 3112, 3226]                     # 公演終了
B = [240, 874, 894, 1050, 1755]                  # 公演未来だが一般発売終了
C = [1179, 1247, 1466, 1494, 1884, 2137, 2188, 2225, 2256, 2299,
     2746, 2747, 2753, 2754, 2861, 2863, 2864, 2928, 3001, 3010]  # 残置型

raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*\[', raw)
s = raw.index('[', m.start())
depth = 0
for i in range(s, len(raw)):
    if raw[i] == '[':
        depth += 1
    elif raw[i] == ']':
        depth -= 1
        if depth == 0:
            e = i + 1
            break
arr = json.loads(raw[s:e])
M = {ev['id']: ev for ev in arr}

def dump(label, ids):
    out = ['■%s (%d件)' % (label, len(ids))]
    for i in ids:
        ev = M.get(i)
        if not ev:
            out.append('  id=%d ★index.htmlに存在しない' % i)
            continue
        lk = {k: v for k, v in (ev.get('links') or {}).items() if v}
        url = lk.get('pia') or lk.get('rakuten') or lk.get('eplus') or lk.get('lawson') or '(URLなし)'
        out.append('  id=%d | %s | %s @ %s | 公演%s | 売り場=%s' % (
            i, ev.get('artist'), ev.get('name'), ev.get('venue'), ev.get('date'),
            '/'.join(k for k in lk if k != 'amazon')))
        out.append('        URL: %s' % url)
        for t in ev.get('tickets', []):
            out.append('        枠: %s | date=%s%s' % (
                t.get('type'), t.get('date'),
                ' startDate=%s' % t['startDate'] if t.get('startDate') else ''))
    return out

lines = []
for label, ids in (('A群 公演終了', A), ('B群 公演未来・一般発売終了', B), ('C群 残置型(先行のみ終了)', C)):
    lines += dump(label, ids) + ['']

io.open('tmp/out_delete_cands_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote tmp/out_delete_cands_0730.txt')
