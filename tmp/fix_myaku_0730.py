# -*- coding: utf-8 -*-
"""3467/3468 ミャクミャクくじ券の下書きジャンルを engeki→anime+kids に（振り分け時に要確認）"""
import io, json, re, datetime

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

log = []
for ev in EVENTS:
    if ev['id'] not in (3467, 3468):
        continue
    log.append('id=%d %s' % (ev['id'], ev['name']))
    log.append('   _genre %s→anime  _extraGenres %s→["kids"]  (_piaSub=%s)'
               % (ev.get('_genre'), ev.get('_extraGenres'), ev.get('_piaSub')))
    ev['_genre'] = 'anime'
    ev['_extraGenres'] = ['kids']

bak = 'index.html.bak_%s_myaku' % datetime.date.today().strftime('%m%d')
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
io.open('tmp/out_myaku_0730.txt', 'w', encoding='utf-8').write('\n'.join(log))
print('更新 2件 (backup %s)' % bak)
