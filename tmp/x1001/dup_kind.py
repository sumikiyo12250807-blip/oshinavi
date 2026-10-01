# -*- coding: utf-8 -*-
# dup_scan の組を「名前まで完全に同じ（二重登録）」と「名前が少し違う」に分けて数える
import io, json, re, sys, unicodedata
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
exec(open('C:/Users/user/oshinavi/tmp/x1001/dup_scan.py', encoding='utf-8').read().split("out = io.open")[0])
nz = lambda n: re.sub(r'[\s　]', '', unicodedata.normalize('NFKC', n or ''))
same, diff = [], []
for k, v in g.items():
    if len(v) < 2:
        continue
    (same if len({nz(e.get('name')) for e in v}) == 1 else diff).append(sorted(v, key=lambda e: e['id']))
out = io.open('C:/Users/user/oshinavi/tmp/x1001/dup_kind.txt', 'w', encoding='utf-8')
out.write(f'名前まで同じ {len(same)}組 / 名前が少し違う {len(diff)}組\n')
out.write(f"新着が混ざる組 {sum(1 for v in same + diff if any(e.get('genre') == 'new' for e in v))}\n")
out.write('--- 名前が少し違う組 ---\n')
for v in diff:
    out.write(' | '.join(f"{e['id']}:{e.get('name')[:40]}" for e in v) + '\n')
json.dump({'same': [[e['id'] for e in v] for v in same], 'diff': [[e['id'] for e in v] for v in diff]},
          io.open('C:/Users/user/oshinavi/tmp/x1001/dup_kind.json', 'w'))
