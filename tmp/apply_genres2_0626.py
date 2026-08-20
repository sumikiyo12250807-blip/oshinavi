# -*- coding: utf-8 -*-
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = 'index.html'
src = open(path, encoding='utf-8').read()

mapping = {}
# 非jpop
for i in (1370,1371,1372,1373,1374,1375,1376,1377,1378,1379,1380,1381,1382):
    mapping[i] = ('classic', [])
mapping[1351] = ('jazz', [])
mapping[1368] = ('jazz', [])
mapping[1341] = ('engeki', [])
mapping[1369] = ('fes', [])
mapping[1347] = ('kids', [])
# jpop（残り32件）
for i in (1332,1333,1334,1335,1336,1338,1339,1340,1342,1343,1344,1345,1346,1348,1349,
          1350,1352,1353,1354,1355,1356,1357,1358,1359,1360,1361,1362,1363,1364,1365,1366,1367):
    mapping[i] = ('jpop', [])

def block_span(id):
    m = re.search(r'\{\s*"id":\s*%d,' % id, src)
    if not m: return None
    i = m.start(); d = 0; j = i
    while True:
        if src[j] == '{': d += 1
        elif src[j] == '}':
            d -= 1
            if d == 0: return (i, j+1)
        j += 1

draft_re = re.compile(
    r'"genre":\s*"new",\s*\n'
    r'\s*"_genre":[^\n]*\n'
    r'\s*"_extraGenres":\s*\[[^\]]*\],\s*\n'
    r'\s*"_piaSub":[^\n]*\n', re.S)

count = 0; issues = []
for id in sorted(mapping, reverse=True):
    sp = block_span(id)
    if not sp: issues.append(('no-block', id)); continue
    s, e = sp; blk = src[s:e]
    g, extra = mapping[id]
    if extra:
        repl = '"genre": "%s",\n    "extraGenres": [%s],\n' % (g, ', '.join('"%s"' % x for x in extra))
    else:
        repl = '"genre": "%s",\n' % g
    nb, n = draft_re.subn(repl, blk, count=1)
    if n != 1: issues.append(('no-draft', id)); continue
    src = src[:s] + nb + src[e:]
    count += 1

# NEW_ORDER 空に
src = re.sub(r'const NEW_ORDER = \[[^\]]*\];', 'const NEW_ORDER = [];', src, count=1)
open(path, 'w', encoding='utf-8').write(src)
print('適用:', count, '/ issues:', issues or 'なし')
print('genre:new 残:', src.count('"genre": "new"'))
print('_genre 残:', src.count('"_genre"'), '/ _piaSub 残:', src.count('"_piaSub"'))
