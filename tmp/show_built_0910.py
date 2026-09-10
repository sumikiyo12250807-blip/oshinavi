# -*- coding: utf-8 -*-
"""組み直した結果を、既存と並べて「増える枠だけ」を目で見える形にする。"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

# PowerShell の `>` はBOM付きUTF-8で書く。utf-8-sig で開かないと落ちる
built = {b['id']: b for b in json.load(io.open(sys.argv[1], encoding='utf-8-sig'))}
h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
by = {e['id']: e for e in EVENTS}


def norm(s):
    return unicodedata.normalize('NFKC', (s or '')).replace(' ', '')


for i, b in built.items():
    e = by.get(i) or {}
    old = {norm(t.get('type')) for t in (e.get('tickets') or [])}
    print('## id=%d %s' % (i, b.get('artist')))
    print('   既存 会期 : %s' % e.get('dateLabel'))
    print('   ビルド会期: %s（date=%s）' % (b.get('dateLabel'), b.get('date')))
    print('   既存 会場 : %s' % (e.get('venue') or '')[:100])
    print('   ビルド会場: %s' % (b.get('venue') or '')[:100])
    print('   既存枠 %d / ビルド枠 %d' % (len(e.get('tickets') or []), len(b.get('tickets') or [])))
    for t in b.get('tickets') or []:
        new = norm(t.get('type')) not in old
        print('     %s %s ／ 締切=%s' % ('🆕' if new else '  ', t.get('type'), t.get('date')))
    print()
