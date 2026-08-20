# -*- coding: utf-8 -*-
"""育成ドライランから【安全に適用できるid】だけを選ぶ。
除外＝①枠が減るもの（生きた枠が消える恐れ・1件ずつ人が見る）
      ②id153 "US"（2文字の検索語でぴあの部分一致が暴発。無関係の公演58枠を拾っている）
"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

JUNK = {153}
txt = io.open('tmp/grow_dry_full_0818.txt', encoding='utf-8').read()

ok, shrink = [], []
for b in re.split(r'\n=+\n', txt):
    m = re.search(r'^id=(\d+)\s+(.*?)\s+ぴあURL', b, re.M)
    mk = re.search(r'枠 (\d+) → (\d+)', b)
    if not m or not mk:
        continue
    eid, old, new = int(m.group(1)), int(mk.group(1)), int(mk.group(2))
    if eid in JUNK:
        continue
    (ok if new >= old else shrink).append(eid)

print('適用する %d件' % len(ok))
print('ids=' + ','.join(str(i) for i in ok))
print()
print('保留（枠が減る）%d件: %s' % (len(shrink), ','.join(str(i) for i in shrink)))
io.open('tmp/grow_apply_ids_0818.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in ok))
