# -*- coding: utf-8 -*-
"""7/1 新着50件 ジャンル振り分け(ユーザーOK「振り分けお願い」2026-07-01)。
_genre下書き＋目視補正で確定。genre確定・extraGenres付与・下書きフィールド(_genre/_extraGenres/_piaSub)除去・
NEW_ORDER空に・genre:new解消。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# id -> (genre, [extraGenres])
ASSIGN = {
    1701: ('jazz', []), 1702: ('owarai', []), 1703: ('musical', []),
    1704: ('classic', []), 1705: ('classic', []), 1706: ('classic', []),
    1707: ('classic', []), 1708: ('classic', []), 1709: ('enka', []),
    1710: ('owarai', []), 1711: ('owarai', []), 1712: ('owarai', []),
    1713: ('owarai', []), 1714: ('owarai', []), 1715: ('owarai', []),
    1716: ('classic', []), 1717: ('classic', []), 1718: ('classic', []),
    1719: ('classic', []), 1720: ('classic', []), 1721: ('classic', ['jazz']),
    1722: ('classic', []), 1723: ('classic', []), 1724: ('classic', []),
    1725: ('classic', []), 1726: ('classic', []), 1727: ('classic', []),
    1728: ('classic', []), 1729: ('classic', []), 1730: ('classic', []),
    1731: ('classic', []), 1732: ('jpop', []),
    1740: ('owarai', []), 1741: ('owarai', []), 1742: ('engeki', []),
    1743: ('engeki', []), 1744: ('owarai', []), 1745: ('owarai', []),
    1746: ('owarai', []), 1747: ('jpop', []), 1748: ('jpop', []),
    1749: ('jpop', []), 1750: ('jazz', []), 1751: ('rock', []),
    1752: ('anime', []), 1753: ('jazz', []), 1754: ('jazz', []),
    1755: ('jpop', []), 1756: ('enka', []), 1757: ('jpop', []),
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

miss = set(ASSIGN) - {e['id'] for e in EVENTS}
assert not miss, 'DB未在: %s' % miss
still_new = [e['id'] for e in EVENTS if e.get('genre') == 'new' and e['id'] not in ASSIGN]
assert not still_new, '未割当のnewが残る: %s' % still_new

from collections import Counter
tally = Counter()
for e in EVENTS:
    a = ASSIGN.get(e['id'])
    if not a:
        continue
    g, extra = a
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    tally[g + ('+' + '/'.join(extra) if extra else '')] += 1

# NEW_ORDER 空に
h_new = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', h, count=1)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h_new, re.S)
out = h_new[:m2.start()] + m2.group(1) + new_arr + m2.group(3) + h_new[m2.end():]

remaining_new = sum(1 for e in EVENTS if e.get('genre') == 'new')
open('index.html.bak_0701_assign', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(out)
print('振り分け %d件 / genre:new 残 %d件' % (len(ASSIGN), remaining_new))
print('内訳:', dict(sorted(tally.items(), key=lambda x: -x[1])))
print('backup: index.html.bak_0701_assign')
