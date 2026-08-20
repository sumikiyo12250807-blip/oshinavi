# -*- coding: utf-8 -*-
"""7/6 アート2件(2034木梨憲武展/2035ゴジラ展)を新設genre:"art"に振り分け。
下書きフィールド除去・NEW_ORDERから外す。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
ART = {2034, 2035}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
done = []
for e in EVENTS:
    if e.get('id') in ART:
        e['genre'] = 'art'
        for k in ('_genre', '_extraGenres', '_piaSub'):
            e.pop(k, None)
        done.append(e['id'])
print('art振り分け:', done)

mo = re.search(r'const NEW_ORDER = (\[[0-9,\s]*\]);', h)
cur = json.loads(mo.group(1))
cur = [i for i in cur if i not in ART]
no = '[' + ', '.join(str(i) for i in cur) + ']'
h2 = h[:mo.start()] + 'const NEW_ORDER = ' + no + ';' + h[mo.end():]
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
print('NEW_ORDER残り', len(cur), '件')
if DRY:
    print('(DRY)')
else:
    open('index.html.bak_0706_art', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():])
    print('written (backup: index.html.bak_0706_art)')
