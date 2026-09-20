# -*- coding: utf-8 -*-
"""e+のジャンル別スイープの結果を1本にまとめる（重複を外して件数を数える）。
  python tmp/x0921/eplus_merge_cands.py
出力: tmp/x0921/eplus_cands_all.json（eplus_harvest.py build に渡す形）
"""
import glob, io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

h = io.open('index.html', encoding='utf-8', newline='').read()
have = set(re.findall(r'eplus\.jp/sf/detail/(\d+)', h))

rows, per = {}, {}
for f in sorted(glob.glob('tmp/x0921/../eplus_presale_*_0921.json')) + \
        sorted(glob.glob('tmp/eplus_presale_*_0921.json')):
    g = re.search(r'eplus_presale_(.+?)_0921\.json', f).group(1)
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception as e:
        print('読めない %s (%s)' % (f, e))
        continue
    per[g] = len(d)
    for r in d:
        eid = str(r.get('eid') or '')
        if not eid or eid in have:
            continue
        if eid not in rows:
            rows[eid] = r
            r['_genres'] = [g]
        elif g not in rows[eid]['_genres']:
            rows[eid]['_genres'].append(g)

out = io.open('tmp/x0921/eplus_cands_report.txt', 'w', encoding='utf-8')
out.write('=== e+ 発売前スイープのまとめ（2026-09-21）===\n')
for g, n in sorted(per.items()):
    out.write('  %-18s %4d件\n' % (g, n))
out.write('\nユニーク（登録済みを外した）= %d件\n\n' % len(rows))
for eid, r in sorted(rows.items(), key=lambda x: x[1].get('date') or ''):
    out.write('  %s | %-12s | %-20s | %s\n'
              % (eid, r.get('date'), '/'.join(r['_genres']), (r.get('title') or '')[:46]))
out.close()
json.dump(list(rows.values()), io.open('tmp/x0921/eplus_cands_all.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('e+ 候補 %d件（ジャンル別 %s）→ tmp/x0921/eplus_cands_all.json'
      % (len(rows), per))
