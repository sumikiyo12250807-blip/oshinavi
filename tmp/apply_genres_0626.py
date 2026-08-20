# -*- coding: utf-8 -*-
import re, io

path = 'index.html'
src = open(path, encoding='utf-8').read()

# id -> (genre, [extraGenres])
single_jpop = [1283,1285,1286,1287,1288,1289,1290,1291,1292,1293,1295,1296,1297,
               1299,1300,1301,1302,1303,1305,1306,1307,1309,1311,1312,1313,1314,
               1315,1316,1317,1320,1321,1322,1323,1324,1325,1326,1328,1329]
mapping = {}
for i in single_jpop:
    mapping[i] = ('jpop', [])
mapping.update({
    1282: ('jpop', ['classic']),
    1284: ('dento', []),
    1294: ('jazz', []),
    1298: ('classic', []),
    1308: ('owarai', []),
    1310: ('fes', []),
    1318: ('enka', []),
    1319: ('fes', []),
    1327: ('hiphop', []),
    1330: ('rock', ['jpop']),
    1331: ('rock', []),
})

def block_span(id):
    m = re.search(r'\{\s*"id":\s*%d,' % id, src)
    if not m: return None
    i = m.start(); depth = 0; j = i
    while True:
        if src[j] == '{': depth += 1
        elif src[j] == '}':
            depth -= 1
            if depth == 0: return (i, j+1)
        j += 1

# draft block pattern (genre:new + _genre + _extraGenres + _piaSub)
draft_re = re.compile(
    r'"genre":\s*"new",\s*\n'
    r'\s*"_genre":[^\n]*\n'
    r'\s*"_extraGenres":\s*\[[^\]]*\],\s*\n'
    r'\s*"_piaSub":[^\n]*\n', re.S)

count = 0
missing = []
# process from highest id to lowest so spans stay valid
for id in sorted(mapping, reverse=True):
    span = block_span(id)
    if not span:
        missing.append(id); continue
    s, e = span
    blk = src[s:e]
    genre, extra = mapping[id]
    if extra:
        repl = '"genre": "%s",\n    "extraGenres": [%s],\n' % (
            genre, ', '.join('"%s"' % g for g in extra))
    else:
        repl = '"genre": "%s",\n' % genre
    newblk, n = draft_re.subn(repl, blk, count=1)
    if n != 1:
        missing.append(('no-draft', id)); continue
    src = src[:s] + newblk + src[e:]
    count += 1

open(path, 'w', encoding='utf-8').write(src)
print('applied:', count)
print('missing/issues:', missing)
# leftover checks
print('genre:new remaining:', src.count('"genre": "new"'))
print('_genre remaining:', src.count('"_genre"'))
print('_piaSub remaining:', src.count('"_piaSub"'))
