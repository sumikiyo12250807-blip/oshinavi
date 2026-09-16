# -*- coding: utf-8 -*-
"""ページごと抜けていた7ページのビルド結果を、同じツアーの既存エントリへ足す形にする（飛び先を先に焼き込む）。"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
MAP = {9101: 4227, 9102: 4228, 9103: 7518, 9104: 7518, 9105: 2203, 9106: 4236, 9107: 4397}
b = json.load(io.open('tmp/built_missB_0911.json', encoding='utf-8-sig'))
mb, mc = [], []
for e in b:
    u = e['links']['pia']
    for t in e['tickets']:
        t['url'] = t.get('url') or u
    src = e['id']
    e['id'] = MAP[src]
    mb.append(e)
    mc.append({'newid': e['id'], 'artist': e['artist'], 'urls': [u]})
json.dump(mb, io.open('tmp/built_mergeB_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mc, io.open('tmp/cand_mergeB_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('既存に足す %d件' % len(mb))
