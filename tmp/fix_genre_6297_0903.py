# -*- coding: utf-8 -*-
"""id6297 ROCKY の下書きジャンルを yougaku → kpop に直す。
根拠＝ぴあのサブは「音楽/海外ROCK・POPS」だが、ROCKYは元ASTROのラキ＝韓国のアーティスト。
memory feedback_kpop_vs_yougaku＝「海外ROCK・POPS」で韓国のアーティストは kpop に読み替える
（読み替えるのはこの区分のときだけ）。
CRLF保持は assign_genres.py と同じ方式（newline='' で読み、改行を戻して書く）。
"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = 0
for e in events:
    if e.get('id') == 6297:
        print('before: _genre=%s _piaSub=%s' % (e.get('_genre'), e.get('_piaSub')))
        assert e.get('_piaSub') == '音楽/海外ROCK・POPS', '前提のぴあ区分が違う'
        e['_genre'] = 'kpop'
        hit += 1

if hit != 1:
    print('!! hit=%d なので書き戻さない' % hit)
    sys.exit(1)

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start()] + m.group(1) + dumped + m.group(3) + src[m.end():]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('id6297 の下書きジャンルを kpop にした')
