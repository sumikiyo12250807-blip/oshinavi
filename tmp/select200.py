# -*- coding: utf-8 -*-
"""全候補からeventCd＋正規化名で重複除外、ジャンル別キャップで約200件選定。発売日が近い順優先。"""
import json, io, sys, re, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
idx = open('index.html', encoding='utf-8').read()
exist_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))
ti = idx.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(idx, ti)
def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—~～]', '', s).lower()
ex_names = set()
for e in arr:
    ex_names.add(norm(e.get('name'))); ex_names.add(norm(e.get('artist')))
def cd_of(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or ''); return m.group(1) if m else None
def rkey(it):
    r = (it.get('rls') or [it.get('rlsdate','')] )
    r = r[0] if isinstance(r, list) else r
    if r in ('', 'TODAY'): return '2026-00'
    m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', r or '')
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else '2099'

SRC = [('tmp/ps_classic.json','classic',85),('tmp/ps_music.json','music',55),
       ('tmp/ps_sports.json','sports',30),('tmp/ps_engeki.json','engeki',25),
       ('tmp/ps_event.json','event',20)]
nid = 1146
picked = []
seen_cd = set(); seen_nm = set()
for f, src, cap in SRC:
    items = json.load(open(f, encoding='utf-8'))['new']
    items.sort(key=rkey)   # 発売日が近い順
    cnt = 0
    for it in items:
        if cnt >= cap: break
        cd = cd_of(it.get('url') or (it.get('urls') or [''])[0])
        nm = norm(it['artist'])
        if not cd or cd in exist_cds or cd in seen_cd: continue
        if nm in ex_names or nm in seen_nm: continue
        seen_cd.add(cd); seen_nm.add(nm)
        url = it.get('url') or it['urls'][0]
        picked.append({'newid': nid, 'artist': it['artist'], 'urls': [url], '_src': src})
        nid += 1; cnt += 1
    print(f"{src}: {cnt}件")
json.dump([{'newid':p['newid'],'artist':p['artist'],'urls':p['urls']} for p in picked],
          open('tmp/candidates200.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n合計', len(picked), '件  id', picked[0]['newid'], '..', picked[-1]['newid'])
