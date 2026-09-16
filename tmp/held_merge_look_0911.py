# -*- coding: utf-8 -*-
"""統合行きのうち相手が決まらなかった分を、既存エントリと並べて見る（読むだけ）。"""
import json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　]+', '', s).lower()


NAMES = ['川崎鷹也', 'OZアカデミー女子プロレス', '新日本プロレス', '島津亜矢', '西村由紀江', 'ズーカラデル', 'TSUKEMEN', '山内惠介']
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
merge = json.load(open('tmp/merge_0911.json', encoding='utf-8'))
for nm in NAMES:
    k = norm(nm)
    print('■', nm)
    for c in merge:
        if norm(c['artist']) == k:
            print('   候補 %s' % c['url'])
    for e in ev:
        if k in norm(e.get('artist')) or k in norm(e.get('name')):
            print('   既存 id%s [%s] %s ／ %s ／ %s' % (e['id'], e.get('genre'), (e.get('name') or '')[:40], e.get('dateLabel'), (e.get('venue') or '')[:30]))
