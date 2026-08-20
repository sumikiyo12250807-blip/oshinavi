# -*- coding: utf-8 -*-
"""削除候補のpia URLを機械抽出（捏造禁止・index.htmlから直取り）"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

past = [65, 154, 200, 437]
future = [167, 1404, 1572, 1664, 2196, 2646]

def url_of(ev):
    p = (ev.get('links') or {}).get('pia')
    if p:
        return p
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u:
            return u
    return '(URL無)'

print("=== 削除OK確定（公演終了済） ===")
for i in past:
    e = byid.get(i)
    if e:
        print(f"id={i} {e.get('artist','')} / {e.get('title','')} ({e.get('date','')})")
        print(f"   {url_of(e)}")

print("\n=== 未来公演・要WebFetch裏取り ===")
for i in future:
    e = byid.get(i)
    if e:
        print(f"id={i} {e.get('artist','')} / {e.get('title','')} ({e.get('date','')})")
        print(f"   {url_of(e)}")
