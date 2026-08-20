# -*- coding: utf-8 -*-
"""新着92件(genre:new)を下書き_genreで本ジャンルへ。下書きフィールド除去＋NEW_ORDER空。"""
import io, re, json, shutil

shutil.copy('index.html', 'index.html.bak_0714_assign')
src = io.open('index.html', encoding='utf-8').read()

pat = re.compile(
    r'"genre": "new",\n(\s*)"_genre": "([a-z0-9]+)",\n'
    r'(?:\s*"_extraGenres": \[\],\n)?'
    r'(?:\s*"_piaSub": "[^"]*",\n)?'
)

counts = {}


def rep(m):
    g = m.group(2)
    counts[g] = counts.get(g, 0) + 1
    return '"genre": "%s",\n' % g


src, n = pat.subn(rep, src)
src, k = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', src, count=1)
assert k == 1, 'NEW_ORDER not reset'

io.open('index.html', 'w', encoding='utf-8').write(src)

# 検証
m = re.search(r'const EVENTS = (\[.*?\n\]);', src, re.S)
ev = json.loads(m.group(1))
left_new = [e['id'] for e in ev if e.get('genre') == 'new']
left_draft = [e['id'] for e in ev if '_genre' in e or '_piaSub' in e or '_extraGenres' in e]

with io.open('tmp/assign_0714_result.txt', 'w', encoding='utf-8') as f:
    f.write('振り分け %d件\n' % n)
    for g, c in sorted(counts.items(), key=lambda x: -x[1]):
        f.write('  %-10s %d\n' % (g, c))
    f.write('残 genre:new = %d件 %s\n' % (len(left_new), left_new))
    f.write('残 下書きフィールド = %d件 %s\n' % (len(left_draft), left_draft))
    f.write('総エントリ数 %d\n' % len(ev))
print('done')
