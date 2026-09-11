# -*- coding: utf-8 -*-
"""refresh_deadlines が「追加」する枠の飛び先（ticket.url）を並べる（読むだけ）。
build_pia_entries に複数URLを渡すと、2本目以降のページの枠に ticket.url が付かない
（memory feedback_build_pia_multiurl_loses_ticket_url）。url が無い枠はカードの links.pia に飛ぶので、
links.pia と別のページの枠なら飛び先が壊れる。url 無しの追加枠を目で確かめるために出す。
使い方: python tmp/check_added_urls_0912.py <built.json>
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = json.load(io.open(sys.argv[1], encoding='utf-8-sig'))
h = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}


def head(ty):
    m = re.match(r'^(.*?（[^（）]*公演）)', ty or '')
    return m.group(1) if m else (ty or '')


nourl = 0
for b in built:
    e = by.get(b['id'])
    if not e:
        continue
    have = {head(t.get('type')) for t in e.get('tickets') or []}
    lp = (e.get('links') or {}).get('pia') or ''
    for t in b.get('tickets') or []:
        if head(t.get('type')) in have:
            continue
        u = t.get('url') or ''
        mark = '✅' if u else '⚠️url無し'
        if not u:
            nourl += 1
        print('%s id%-5s %s\n        url=%s\n        links.pia=%s' % (mark, b['id'], t.get('type'), u or '-', lp))
print('\n追加枠のうち url 無し %d枠（links.pia に飛ぶ）' % nourl)
