# -*- coding: utf-8 -*-
# 11/24 記事の候補：11/25〜11/28 に発売が始まる枠を持つ振り分け済みカード → 最後の締切が 12/12 以降（長く買える）
# → 前に書いた記事の組（台帳＋OK 待ちの 11/21・11/23 の下書き）を外す → フォロワー（11/18 の調べ）の多い順
import io, json, sys, re, glob, os
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
arts = json.load(io.open(root + 'tools/pickup_articles.json', encoding='utf-8'))['articles']
done_names = [a.get('name') or '' for a in arts]
done_ids = set()
for a in arts:
    done_ids.update(a.get('watch') or [])
# OK 待ちの下書き（11/21・11/23）の先頭行＝名前
for f in glob.glob(root + 'tmp/x112*/art*/*.md'):
    b = os.path.basename(f)
    if b.endswith('_material.md') or b in ('brief.md', 'fc.md', 'fc_brief.md', 'sources.md'):
        continue
    first = io.open(f, encoding='utf-8').read().strip().splitlines()[:1]
    if first:
        done_names.append(re.sub(r'^#+\s*', '', first[0]).strip())
done_ids.update([31897, 29543, 6157] + list(range(56878, 56900)))
fol = {}
for f in ('followers_A.json', 'followers_B.json'):
    for r in json.load(io.open(root + 'tmp/x1118/x/' + f, encoding='utf-8')):
        if r.get('followers'):
            fol[r['name']] = r['followers']
def fnum(v):
    if isinstance(v, (int, float)):
        return v
    m = re.search(r'([\d.]+)\s*(万)?', str(v))
    if not m:
        return 0
    return float(m.group(1)) * (10000 if m.group(2) else 1)
rows = []
for e in E:
    if e.get('genre') == 'new' or e['id'] in done_ids:
        continue
    T = e.get('tickets') or []
    st = [t for t in T if '2026-11-25' <= (t.get('startDate') or '') <= '2026-11-28']
    if not st:
        continue
    last = max((t.get('date') or '') for t in st)
    if last < '2026-12-12':
        continue
    nm = e.get('artist') or e.get('name') or ''
    if any(nm and (nm in d or d in nm) for d in done_names if d and len(d) > 1):
        continue
    f = max([fnum(v) for k, v in fol.items() if nm and (nm in k or k in nm)] or [0])
    rows.append((f, e['id'], nm, e.get('name'), e.get('date'), e.get('genre'), min(t.get('startDate') for t in st), last, len(T)))
rows.sort(key=lambda r: -r[0])
out = io.open(root + 'tmp/x1124/art24/cands.txt', 'w', encoding='utf-8')
out.write('候補 %d 件（前に書いた %d 組＋下書きを外した）\n' % (len(rows), len(arts)))
for r in rows[:90]:
    out.write('%s\t%s\t%s\t%s\t公演%s\t%s\t発売%s\t締切%s\t枠%s\n' % r)
print(len(rows))
