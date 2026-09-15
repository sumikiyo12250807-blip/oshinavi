# -*- coding: utf-8 -*-
"""うんこミュージアムのエントリを全部書き出す（2026-09-15 夜・ユーザー「うんこミュージアムひとつにまとめて」の下調べ）
使い方: python unko_list_0915.py → tmp/btn_tpl/unko_list.txt
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
text = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))
us = [e for e in ev if 'うんこミュージアム' in (e.get('name') or '') + (e.get('artist') or '')]
keys = set()
with open('tmp/btn_tpl/unko_list.txt', 'w', encoding='utf-8') as f:
    for e in us:
        keys |= set(e.keys())
        f.write('id%s｜%s\n  artist=%s｜date=%s｜dateLabel=%s\n  venue=%s｜pref=%s｜genre=%s｜extra=%s｜verified=%s\n  links=%s\n' % (
            e['id'], e.get('name'), e.get('artist'), e.get('date'), e.get('dateLabel'), e.get('venue'), e.get('prefecture'),
            e.get('genre'), e.get('extraGenres'), e.get('verified'), json.dumps({k: v for k, v in (e.get('links') or {}).items() if v}, ensure_ascii=False)))
        for t in e.get('tickets') or []:
            f.write('    - %s\n' % json.dumps(t, ensure_ascii=False))
    f.write('\nエントリ %d件／使っているキー: %s\n' % (len(us), sorted(keys)))
print('うんこミュージアム', len(us), '件 → tmp/btn_tpl/unko_list.txt')
