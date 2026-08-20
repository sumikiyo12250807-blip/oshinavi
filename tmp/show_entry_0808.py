# -*- coding: utf-8 -*-
"""指定idのエントリを丸ごと表示する（救済作業の現状確認用）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

ids = sys.argv[1].split(',')
raw = open(r'C:\Users\user\oshinavi\index.html', 'rb').read().decode('utf-8')
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', raw, re.S)
events = json.loads(m.group(2))
by_id = {str(e.get('id')): e for e in events}
for i in ids:
    e = by_id.get(i)
    if not e:
        print('id=%s 見つからない' % i)
        continue
    print(json.dumps(e, ensure_ascii=False, indent=2))
    print()
