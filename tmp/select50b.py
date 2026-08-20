# -*- coding: utf-8 -*-
"""同一アーティスト(正規化名)はURLを統合して1候補に。50件(別アーティスト)選定。"""
import json, io, sys, re, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
idx = open('index.html', encoding='utf-8').read()
exist_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
def cd_of(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or ''); return m.group(1) if m else None
def norm(s):
    s = unicodedata.normalize('NFKC', s)
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—~～]', '', s).lower()
def load(f): return json.load(open(f, encoding='utf-8'))['new']

quota = [('tmp/ps_engeki.json', 'engeki', 18), ('tmp/ps_music.json', 'music', 18), ('tmp/ps_classic.json', 'classic', 14)]
picked = []          # list of dicts (merged)
by_key = {}          # norm-artist -> picked dict
used_cds = set()
nid = 1087
for f, src, q in quota:
    cnt = 0
    for it in load(f):
        cd = cd_of(it['url'])
        if not cd or cd in exist_cds:
            continue
        key = norm(it['artist'])
        if key in by_key:
            # 同一アーティスト → URL統合(別eventCdのみ)
            if cd not in used_cds:
                by_key[key]['urls'].append(it['url']); used_cds.add(cd)
            continue
        if cnt >= q:
            continue
        if cd in used_cds:
            continue
        used_cds.add(cd)
        d = {'newid': nid, 'artist': it['artist'], 'urls': [it['url']], '_src': src}
        by_key[key] = d; picked.append(d); nid += 1; cnt += 1
    print(f"{src}: 選定{cnt}件")
json.dump([{k:v for k,v in p.items() if not k.startswith('_') or k=='_src'} for p in picked],
          open('tmp/candidates50.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n合計', len(picked), '件  id', picked[0]['newid'], '..', picked[-1]['newid'])
multi=[p for p in picked if len(p['urls'])>1]
print('複数URL統合:', [(p['newid'],p['artist'][:18],len(p['urls'])) for p in multi])
PY=None
