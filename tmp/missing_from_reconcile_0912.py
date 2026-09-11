# -*- coding: utf-8 -*-
"""reconcile_pia の出力から「MISSING（ぴあに買える/発売前の枠があるのに登録に無い）」を持つidを取り出す（読むだけ）。
使い方: python tmp/missing_from_reconcile_0912.py tmp/reconcile_recheck_0912.txt
出力: 画面に一覧／tmp/missing_ids_0912.txt（カンマ区切り）
"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read().splitlines()
cur, rows = None, {}
for ln in txt:
    m = re.match(r'^(✅|🚨|❌|⚠️|⏭️?)\s*id=(\d+)\s+(.*)', ln)
    if m:
        cur = (int(m.group(2)), m.group(3)[:40])
        continue
    if cur and 'MISSING' in ln:
        rows.setdefault(cur, []).append(ln.strip()[:140])
for (i, n), ls in sorted(rows.items()):
    print('id%s %s' % (i, n))
    for l in ls[:4]:
        print('    ' + l)
open('tmp/missing_ids_0912.txt', 'w', encoding='utf-8').write(','.join(str(i) for (i, n) in sorted(rows)))
print('MISSINGを持つid %d件 → tmp/missing_ids_0912.txt' % len(rows))
