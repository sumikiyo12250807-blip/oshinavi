# -*- coding: utf-8 -*-
"""grow_from_audit のドライラン結果を集計して、規模と大物を出す。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

txt = io.open('tmp/grow_dry_full_0818.txt', encoding='utf-8').read()
blocks = re.split(r'\n=+\n', txt)

rows = []
for b in blocks:
    m = re.search(r'^id=(\d+)\s+(.*?)\s+ぴあURL\s+(\d+)本', b, re.M)
    if not m:
        continue
    eid, name, nurl = int(m.group(1)), m.group(2).strip(), int(m.group(3))
    mk = re.search(r'枠 (\d+) → (\d+)', b)
    if not mk:
        continue
    old, new = int(mk.group(1)), int(mk.group(2))
    md = re.search(r'千秋楽 (\S+) → (\S+)', b)
    d_old, d_new = (md.group(1), md.group(2)) if md else ('', '')
    rows.append((eid, name, old, new, d_old, d_new))

grow = [r for r in rows if r[3] > r[2]]
same = [r for r in rows if r[3] == r[2]]
shrink = [r for r in rows if r[3] < r[2]]

print('=== 育成ドライランの集計 ===')
print('  差分が出たエントリ %d件' % len(rows))
print('  枠が増える   %d件（合計 %d枠 → %d枠 ／ +%d枠）'
      % (len(grow), sum(r[2] for r in grow), sum(r[3] for r in grow),
         sum(r[3] - r[2] for r in grow)))
print('  枠数は同じ   %d件（千秋楽や会場だけ動く）' % len(same))
print('  🚨枠が減る   %d件（要確認＝消える枠がある）' % len(shrink))
print('  千秋楽が伸びる %d件' % len([r for r in rows if r[4] and r[5] and r[5] > r[4]]))
print()
print('--- 増え幅の大きい上位25件 ---')
for eid, name, old, new, d_old, d_new in sorted(grow, key=lambda r: r[2] - r[3])[:25]:
    ext = ('  千秋楽 %s→%s' % (d_old, d_new)) if d_old != d_new else ''
    print('  id%-5d %-26s %2d→%2d枠%s' % (eid, name[:24], old, new, ext))
print()
if shrink:
    print('--- 🚨枠が減るもの（適用前に必ず中身を見る）---')
    for eid, name, old, new, d_old, d_new in shrink:
        print('  id%-5d %-26s %2d→%2d枠  千秋楽 %s→%s' % (eid, name[:24], old, new, d_old, d_new))
