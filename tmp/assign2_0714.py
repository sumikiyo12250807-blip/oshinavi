# -*- coding: utf-8 -*-
"""新着50件(2605-2654)を下書き_genreで本ジャンルへ。2648落合博満はengeki+sports両方式。"""
import io, re, json, shutil

EXTRA = {2648: ['sports']}  # 両方式

shutil.copy('index.html', 'index.html.bak_0714_assign2')
src = io.open('index.html', encoding='utf-8').read()

m = re.search(r'const EVENTS = (\[.*?\n\]);', src, re.S)
ev = json.loads(m.group(1))
draft = {e['id']: e.get('_genre') for e in ev if e.get('genre') == 'new'}

counts = {}
done = 0
for eid, g in draft.items():
    idx = src.find('"id": %d,' % eid)
    assert idx != -1, 'id%d not found' % eid
    gpos = src.find('"genre": "new",', idx)
    assert gpos != -1 and gpos - idx < 800, 'genre id%d' % eid
    ls = src.rfind('\n', 0, gpos) + 1
    indent = src[ls:gpos]
    if eid in EXTRA:
        ex = ', '.join('"%s"' % x for x in EXTRA[eid])
        new = '"genre": "%s",\n%s"extraGenres": [%s],' % (g, indent, ex)
    else:
        new = '"genre": "%s",' % g
    src = src[:gpos] + new + src[gpos + len('"genre": "new",'):]
    counts[g] = counts.get(g, 0) + 1
    done += 1

# 下書きフィールド除去
src, n1 = re.subn(r'\n\s*"_genre": "[a-z0-9]*",', '', src)
src, n2 = re.subn(r'\n\s*"_extraGenres": \[\],', '', src)
src, n3 = re.subn(r'\n\s*"_piaSub": "[^"]*",', '', src)
src, k = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', src, count=1)
assert k == 1

io.open('index.html', 'w', encoding='utf-8').write(src)

m = re.search(r'const EVENTS = (\[.*?\n\]);', src, re.S)
ev = json.loads(m.group(1))
left_new = [e['id'] for e in ev if e.get('genre') == 'new']
left_draft = [e['id'] for e in ev if '_genre' in e or '_piaSub' in e or '_extraGenres' in e]

with io.open('tmp/assign2_result.txt', 'w', encoding='utf-8') as f:
    f.write('振り分け %d件 / 下書き除去 _genre%d _extra%d _piaSub%d\n' % (done, n1, n2, n3))
    for g, c in sorted(counts.items(), key=lambda x: -x[1]):
        f.write('  %-10s %d\n' % (g, c))
    f.write('両方式: %s\n' % EXTRA)
    f.write('残 genre:new = %d %s\n' % (len(left_new), left_new))
    f.write('残 下書き = %d %s\n' % (len(left_draft), left_draft))
    f.write('総エントリ %d\n' % len(ev))
print('done')
