# -*- coding: utf-8 -*-
"""投入前チェック：eventCd/eventBundleCd と 正規化名 で既存EVENTSと重複していないか。
（memory: feedback_harvest_dedup_check）"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,.:;!?"\'()（）\[\]【】~〜\-−–—/／]', '', s)

def cds(e):
    out = set()
    blob = json.dumps(e, ensure_ascii=False)
    out |= set(re.findall(r'eventCd=(\d+)', blob))
    out |= set(re.findall(r'eventBundleCd=(b?\d+)', blob))
    return out

h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = json.load(open('tmp/entries_0814.json', encoding='utf-8'))

old_cd = {}
for e in EV:
    for c in cds(e):
        old_cd.setdefault(c, []).append(e['id'])
old_nm = {}
for e in EV:
    old_nm.setdefault(norm(e.get('name') or e.get('artist')), []).append(e['id'])

hit_cd, hit_nm, hit_self = [], [], []
seen_cd = {}
for e in new:
    for c in cds(e):
        if c in old_cd:
            hit_cd.append((e['id'], e.get('name'), c, old_cd[c]))
        if c in seen_cd:
            hit_self.append((e['id'], seen_cd[c], c))
        seen_cd[c] = e['id']
    n = norm(e.get('name') or e.get('artist'))
    if n in old_nm:
        hit_nm.append((e['id'], e.get('name'), old_nm[n]))

print('新着', len(new), '件')
print('eventCd重複(既存と)', len(hit_cd))
for r in hit_cd:
    print('  ', r)
print('eventCd重複(新着同士)', len(hit_self))
for r in hit_self:
    print('  ', r)
print('正規化名重複(既存と)', len(hit_nm))
for r in hit_nm:
    print('  ', r)
print('id重複', [e['id'] for e in new if e['id'] in {x['id'] for x in EV}])
