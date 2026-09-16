# -*- coding: utf-8 -*-
"""id8079 福田こうへい 9/26 神奈川（混雑で落ちて単独で取り直した分）を、本体ツアー id734 に足す候補を作る。"""
import io, json
b = json.load(io.open('tmp/built_8079_0911.json', encoding='utf-8-sig'))[0]
url = b['links']['pia']
for t in b['tickets']:
    t['url'] = t.get('url') or url
b['id'] = 734
json.dump([b], io.open('tmp/built_merge8079_0911.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump([{'newid': 734, 'artist': b['artist'], 'urls': [url]}], io.open('tmp/cand_merge8079_0911.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok', url)
