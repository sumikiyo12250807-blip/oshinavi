# -*- coding: utf-8 -*-
"""夕方のヒール適用の前後で「画面に出る枠」が減っていないかを数える（骨格＋飛び先URL）。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

TODAY = "2026-09-09"
BEFORE = "index.html.bak_0909_preeveheal"
AFTER = "index.html"
OUT = "tmp/heal_diff_eve_0909.txt"


def load(path):
    h = io.open(path, encoding="utf-8", newline="").read()
    return {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))}


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


def head(ty):
    m = re.match(r'^(.*?（[^（）]*公演）)', ty or '')
    return m.group(1) if m else (ty or '')


A, B = load(BEFORE), load(AFTER)
lost, gained, shrunk = [], [], []
ta = tb = 0
for i, ea in A.items():
    va = {head(t.get('type')) for t in ea.get('tickets', []) if visible(t)}
    ta += len(va)
    eb = B.get(i)
    if eb is None:
        lost.append((i, ea.get('name', '')[:36], sorted(va)))
        continue
    vb = {head(t.get('type')) for t in eb.get('tickets', []) if visible(t)}
    tb += len(vb)
    if va - vb:
        lost.append((i, ea.get('name', '')[:36], sorted(va - vb)))
    if vb - va:
        gained.append((i, ea.get('name', '')[:36], len(va), len(vb)))
    if (ea.get('date') or '') != (eb.get('date') or '') or (ea.get('dateLabel') or '') != (eb.get('dateLabel') or ''):
        shrunk.append((i, ea.get('name', '')[:30], ea.get('date'), eb.get('date')))
for i, eb in B.items():
    if i not in A:
        tb += sum(1 for t in eb.get('tickets', []) if visible(t))

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write('前 %d枠 → 後 %d枠 （差 %+d）\n' % (ta, tb, tb - ta))
    f.write('骨格ごと消えたエントリ %d / 増えた %d / 会期が動いた %d\n\n' % (len(lost), len(gained), len(shrunk)))
    for i, n, g in lost:
        f.write('🚨 id%-6d %s\n' % (i, n))
        for k in g:
            f.write('      - %s\n' % k)
    for i, n, da, db in shrunk:
        f.write('会期 id%-6d %s  %s → %s\n' % (i, n, da, db))
    f.write('\n【増えた】\n')
    for i, n, a, b in gained:
        f.write('  id%-6d %s  %d→%d\n' % (i, n, a, b))

print('前=%d 後=%d 差=%+d / 消えた%d件 増えた%d件 会期が動いた%d件'
      % (ta, tb, tb - ta, len(lost), len(gained), len(shrunk)))
