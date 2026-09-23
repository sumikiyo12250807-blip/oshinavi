# -*- coding: utf-8 -*-
"""指定idのエントリの公演日・会場・枠（券種名・締切）を出す（読むだけ）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ids = {int(x) for x in sys.argv[1:]}
h = io.open('index.html', encoding='utf-8', newline='').read()
for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1)):
    if e['id'] in ids:
        print(e['id'], e.get('genre'), e.get('name'), e.get('date'), e.get('dateLabel'), e.get('venue'))
        print('   links', {k: v for k, v in (e.get('links') or {}).items() if v})
        for t in e.get('tickets') or []:
            print('   ', t.get('type'), t.get('date'), (t.get('url') or '')[:60])
