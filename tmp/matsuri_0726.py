# -*- coding: utf-8 -*-
"""MATSURI(3224)の楽天ページを機械パースして公演/会場を取り直す"""
import sys, io, json, re
sys.path.insert(0, 'tools')
import rakuten_harvest as H
import build_rakuten_entries as B

URL = 'https://ticket.rakuten.co.jp/music/rtax088/'
out = {}
body = H.fetch(URL)
m = re.search(r'<title>(.*?)</title>', body, re.S)
out['title'] = H.strip_tags(m.group(1)).strip() if m else None
rec = H.parse_page(URL, body)
out['rec'] = rec
try:
    built, err = B.build([rec], 3224)
    out['built'] = built
    out['err'] = err
except Exception as ex:
    out['build_error'] = repr(ex)[:300]

with open('tmp/matsuri.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
