# -*- coding: utf-8 -*-
"""投入する11件を仕上げる（3件は既存へマージするので外す）。"""
import json, io

TODAY = '2026-09-05'
MERGE_OUT = {6940, 6945, 6947}   # 6103 / 6295+1218 / 6080 へマージ
GENRE = {
    'Sick2': 'rock', 'DAMILA／M.E.S.S／CHAOSS': 'rock', 'シンギュラリティ': 'rock',
}
# id(ビルド時) → (_genre, _piaSub)
G = {
    6935: ('jpop', None), 6936: ('rock', None), 6937: ('rock', None), 6938: ('rock', None),
    6939: ('rock', None), 6941: ('gakusai', None), 6942: ('gakusai', None), 6943: ('gakusai', None),
    6944: ('rock', None), 6946: ('jpop', '音楽/J-POP・ROCK'), 6948: ('rock', None),
}

built = json.load(io.open('tmp/eplus_built.json', encoding='utf-8'))
out, nid = [], 6935
for e in built:
    if e['id'] in MERGE_OUT:
        continue
    g, sub = G[e['id']]
    e['id'] = nid; nid += 1
    if 'Sick2 BOX 2026-EAST-' in e['name']:
        e['name'] = 'Sick2 presents 『Sick2 BOX 2026-EAST-／-WEST-』'
    if e['artist'] == 'サーカス／加藤実':
        e['links']['pia'] = 'https://t.pia.jp/pia/event/event.do?eventCd=2630866'
    e['_genre'] = g
    e['_extraGenres'] = []
    e['_piaSub'] = sub
    e['verifiedAt'] = TODAY
    e['verified'] = True
    out.append(e)

json.dump(out, io.open('tmp/eplus_new_0905.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
with io.open('tmp/eplus_new_0905.txt', 'w', encoding='utf-8') as f:
    for e in out:
        f.write('id%d [%s] %s ／ %s\n   %s\n   枠%d\n' % (e['id'], e['_genre'], e['artist'], e['name'], e['dateLabel'], len(e['tickets'])))
print('NEW=%d slots=%d' % (len(out), sum(len(e['tickets']) for e in out)))
