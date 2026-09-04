# -*- coding: utf-8 -*-
"""素朴に畳んだ場合（代表エントリのlinksを残しticketsを連結）の被害を数える"""
import re, json, unicodedata, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = r'C:\Users\user\oshinavi\index.html'
TODAY = '2026-09-04'
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);',
        open(PATH, encoding='utf-8', newline='').read(), re.S).group(1))
def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[^0-9a-z\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]', '', s)
def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'): return True
    sd, d = t.get('startDate'), (t.get('date') or '')
    return not ((not sd or sd <= TODAY) and d < TODAY)
ORDER=['rakuten','pia','eplus','lawson','fany','yoshimoto','tvasahi']
def cl(e):
    L=e.get('links') or {}
    for k in ORDER:
        if L.get(k): return L[k]
groups=collections.defaultdict(list)
for e in EVENTS: groups[norm(e.get('name',''))].append(e)
dg={k:sorted(v,key=lambda x:x.get('id')) for k,v in groups.items() if len(v)>=2 and k}

bad=0; badg=[]; tot=0
for k,g in dg.items():
    rep = cl(g[0])
    n=0
    for e in g:
        for t in (e.get('tickets') or []):
            if not visible(t): continue
            tot+=1
            before = t.get('url') or cl(e)
            after  = t.get('url') or rep
            if before != after: n+=1; bad+=1
    if n: badg.append((g[0].get('name'), [x.get('id') for x in g], n))
print('素朴に畳んだ場合：飛び先が変わってしまう可視枠 = %d 本 / 同名グループの可視枠 %d 本' % (bad, tot))
print('影響グループ数 = %d / %d' % (len(badg), len(dg)))
for n,ids,c in sorted(badg,key=lambda x:-x[2])[:20]:
    print('  %s %s → %d本が別の売り場に飛ぶ' % (n, ids, c))

# 会場・公演日がバラバラなグループ（＝別公演の集合）を数える
diff_date=0; same_all=0
for k,g in dg.items():
    ds=set(str(e.get('date')) for e in g)
    if len(ds)==len(g): diff_date+=1
    if len(ds)==1 and len(set(str(e.get('venue')) for e in g))==1: same_all+=1
print('\n公演日が全部バラバラなグループ（別公演の可能性大）: %d' % diff_date)
print('会場も公演日も完全一致のグループ（重複登録の疑い）: %d' % same_all)
