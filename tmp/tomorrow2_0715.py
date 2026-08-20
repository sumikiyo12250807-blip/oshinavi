# -*- coding: utf-8 -*-
"""明日(7/15)発売開始の公演を抽出（修正版）。
旧版は startDate==date==7/15 の単日形だけ拾っており、
「7/15 11:00発売 〜7/21まで」のようなレンジ形（＝締切が別日）を全部落としていた。
条件は startDate==対象日 だけでよい。"""
import io, json, re

TARGET = '2026-07-15'
s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\]);', s, re.S)
ev = json.loads(m.group(1))

rows = []
for e in ev:
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if t.get('startDate') == TARGET and not t.get('soldout'):
            rows.append((e.get('genre'), e.get('name'), e.get('venue'),
                         e.get('prefecture'), e.get('dateLabel'), ty, t.get('date')))

rows.sort()
# 旧版（単日形のみ）との差分＝取りこぼしていた枠
missed = [r for r in rows if r[6] != TARGET]

with io.open('tmp/tomorrow2_0715.txt', 'w', encoding='utf-8') as f:
    f.write('7/15 発売開始 %d枠（うち旧抽出が落としていた=締切が別日 %d枠）\n\n' % (len(rows), len(missed)))
    f.write('=== 旧版が落としていた枠（X素材の取りこぼし）===\n')
    for g, n, v, p, dl, ty, d in missed:
        f.write('[%s] %s\n    %s (%s)\n    %s ／ 締切=%s\n    公演=%s\n' % (g, n, v, p, ty, d, dl))
print('done')
