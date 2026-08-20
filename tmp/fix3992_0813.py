# -*- coding: utf-8 -*-
"""id3992 ボイスシネマ声優口演ライブ(大阪) を engeki → seiyuu に直す。
同シリーズの id2883(有楽町) が seiyuu なので、そちらに合わせる（ユーザー指摘 2026-08-13）。
index.html は CRLF 維持（memory: feedback_index_html_crlf_preserve）。
"""
import re, json, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
e = [x for x in EVENTS if x['id'] == 3992][0]
print('BEFORE genre=%s extra=%s' % (e.get('genre'), e.get('extraGenres')))
e['genre'] = 'seiyuu'
# 主ジャンルが seiyuu になったので extraGenres の seiyuu は重複＝外す
if e.get('extraGenres'):
    e['extraGenres'] = [g for g in e['extraGenres'] if g != 'seiyuu']
    if not e['extraGenres']:
        del e['extraGenres']
print('AFTER  genre=%s extra=%s' % (e.get('genre'), e.get('extraGenres')))

bak = 'index.html.bak_%s_fix3992' % datetime.date.today().strftime('%m%d')
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('適用完了 (backup %s)' % bak)
