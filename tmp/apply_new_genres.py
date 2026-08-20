import re

TSV = 'tmp/genre_table_theater3_pia.tsv'
HTML = 'index.html'

# --- read genre table ---
genremap = {}
extramap = {}
with open(TSV, encoding='utf-8') as f:
    for line in f:
        line = line.rstrip('\n')
        if not line.strip():
            continue
        cols = line.split('\t')
        if len(cols) < 2 or not cols[0].strip().isdigit():
            continue
        eid = int(cols[0].strip())
        g = cols[1].strip()
        extra = cols[2].strip() if len(cols) > 2 else ''
        if not g:
            continue
        genremap[eid] = g
        if extra:
            extramap[eid] = extra

# --- user-confirmed overrides: kids+engeki 両方方式 ---
for eid in (1058, 1063):
    genremap[eid] = 'kids'
    extramap[eid] = 'engeki'
# 1037, 1083 already kids/engeki in table; sanity-keep
genremap[1037] = 'kids'; extramap[1037] = 'engeki'
genremap[1083] = 'kids'; extramap[1083] = 'engeki'

# --- read html ---
src = open(HTML, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
text = src.replace('\r\n', '\n')
lines = text.split('\n')

applied = []
skipped = []

def find_id_line(eid):
    pat = re.compile(r'^\s*"id":\s*' + str(eid) + r'\s*,\s*$')
    for i, l in enumerate(lines):
        if pat.match(l):
            return i
    return None

for eid in sorted(genremap, reverse=True):  # descending so insertions don't shift earlier entries
    idx = find_id_line(eid)
    if idx is None:
        skipped.append((eid, 'id行なし'))
        continue
    # find genre line within this object (search forward a bounded window)
    gi = None
    for j in range(idx, min(idx + 25, len(lines))):
        if re.match(r'^\s*"genre":\s*"new"\s*,\s*$', lines[j]):
            gi = j
            break
        # stop if we hit next object's id
        if j > idx and re.match(r'^\s*"id":\s*\d+', lines[j]):
            break
    if gi is None:
        skipped.append((eid, '"genre":"new"行なし(既に変更済?)'))
        continue
    indent = lines[gi][:len(lines[gi]) - len(lines[gi].lstrip())]
    g = genremap[eid]
    lines[gi] = f'{indent}"genre": "{g}",'
    # insert extraGenres after genre line if needed
    if eid in extramap:
        e = extramap[eid]
        block = [
            f'{indent}"extraGenres": [',
            f'{indent}  "{e}"',
            f'{indent}],',
        ]
        lines[gi + 1:gi + 1] = block
    applied.append((eid, g, extramap.get(eid, '')))

# --- empty NEW_ORDER ---
text = '\n'.join(lines)
text, n = re.subn(r'const NEW_ORDER = \[[0-9,\s]*\];', 'const NEW_ORDER = [];', text)

open(HTML, 'w', encoding='utf-8', newline='').write(text.replace('\n', nl))

print(f'適用: {len(applied)}件 / スキップ: {len(skipped)}件 / NEW_ORDER空化: {n}箇所')
print('--- ジャンル別集計 ---')
from collections import Counter
c = Counter(g for _, g, _ in applied)
for g, cnt in c.most_common():
    print(f'  {g}: {cnt}')
ex = [(i, g, e) for i, g, e in applied if e]
print(f'--- 両方方式(extraGenres付): {len(ex)}件 ---')
for i, g, e in sorted(ex):
    print(f'  id{i}: {g}+{e}')
if skipped:
    print('--- スキップ ---')
    for i, r in skipped:
        print(f'  id{i}: {r}')
