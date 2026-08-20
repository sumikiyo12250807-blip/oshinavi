# -*- coding: utf-8 -*-
"""指定idのエントリを丸ごと表示（推測せず実データを見る）。
  python tmp/show_entry.py 829 1355
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
ids = [int(x) for x in sys.argv[1:]]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = {e['id']: e for e in json.loads(m.group(2))}
for i in ids:
    e = E.get(i)
    if not e:
        print(f'!! id={i} 無し'); continue
    print(json.dumps(e, ensure_ascii=False, indent=2))
    print('---')
