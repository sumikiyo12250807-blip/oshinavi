# -*- coding: utf-8 -*-
"""reconcileの出力から、問題のあったエントリのidを正しく拾う（直前のid行を親とみなす）。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

lines = io.open('tmp/reco_0817e.txt', encoding='utf-8').read().split('\n')
cur = None
prob = {}
for ln in lines:
    # 親の行＝行頭が「(絵文字) id=NNNN 名前 |」。💤/🚨 が頭に付く親行もあるので
    # 絵文字だけで弾かない（弾くと直前の別エントリに問題をぶら下げて誤報告する）。
    m = re.match(r'\s*(?:[^\sa-zA-Z0-9]+\s*)?id=(\d+)\s+(.*?)\s*\|', ln)
    if m:
        cur = (int(m.group(1)), m.group(2))
        continue
    s = ln.strip()
    if s.startswith(('❌FETCH', '💤STALE', '🚨MISSING', '⚠️DROP')) and cur:
        prob.setdefault(cur, []).append(s)

for (eid, name), rows in sorted(prob.items()):
    print('id%-5d %s' % (eid, name))
    for r in rows:
        print('    ' + r[:150])
    print()
print('問題のあったエントリ:', sorted(k[0] for k in prob))
