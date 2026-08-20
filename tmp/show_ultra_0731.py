# -*- coding: utf-8 -*-
"""id2544(ぴあ版) と id3515(楽天版) を丸ごと出す（統合の下調べ）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))

for eid in (2544, 3515, 3510):
    for e in EVENTS:
        if e['id'] == eid:
            print('=' * 78)
            print(json.dumps(e, ensure_ascii=False, indent=2))
            break
    else:
        print('id=%d 見つからない' % eid)
