# -*- coding: utf-8 -*-
"""theater_dedup.json(204) から未投入分のみ抽出。eventCd＋正規化名で重複除外。"""
import json, io, sys, re, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
cand = json.load(open('tmp/theater_dedup.json', encoding='utf-8'))
idx = open('index.html', encoding='utf-8').read()
exist_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—~～]', '', s).lower()
ex_names = set()
ti = idx.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(idx, ti)
for e in arr:
    ex_names.add(norm(e.get('name'))); ex_names.add(norm(e.get('artist')))
def cds(c):
    out = []
    for u in c.get('urls', []):
        m = re.search(r'event(?:Bundle)?Cd=(\w+)', u)
        if m: out.append(m.group(1))
    return out
remain = []
nid = 1087
seen_cd = set()
for c in cand:
    cl = cds(c)
    nm = norm(c.get('artist'))
    if any(x in exist_cds for x in cl):   # eventCd一致=公開済み
        continue
    if nm and nm in ex_names:              # 名前一致=公開済み
        continue
    if any(x in seen_cd for x in cl):      # 候補内重複
        continue
    seen_cd.update(cl)
    remain.append({'newid': nid, 'artist': c['artist'], 'urls': c['urls']})
    nid += 1
json.dump(remain, open('tmp/cand_theater_remain.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('真の未投入:', len(remain), '件  id', remain[0]['newid'], '..', remain[-1]['newid'])
for r in remain:
    print(f"  {r['newid']} {r['artist'][:42]}")
