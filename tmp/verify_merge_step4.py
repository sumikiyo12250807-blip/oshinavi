# -*- coding: utf-8 -*-
"""畳んだら買える枠/飛び先が壊れるかを機械で数える"""
import re, json, unicodedata, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = r'C:\Users\user\oshinavi\index.html'
TODAY = '2026-09-04'
src = open(PATH, encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);', src, re.S).group(1))
def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[^0-9a-z\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f]', '', s)
def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'): return True
    sd, d = t.get('startDate'), (t.get('date') or '')
    return not ((not sd or sd <= TODAY) and d < TODAY)
ORDER = ['rakuten','pia','eplus','lawson','fany','yoshimoto','tvasahi']
def cardlink(e):
    L = e.get('links') or {}
    for k in ORDER:
        if L.get(k): return L[k]
    return None
def eff(e, t):  # 実際の飛び先
    return t.get('url') or cardlink(e)

groups = collections.defaultdict(list)
for e in EVENTS: groups[norm(e.get('name',''))].append(e)
dg = {k: sorted(v, key=lambda x:x.get('id')) for k,v in groups.items() if len(v)>=2 and k}

print('=== 畳むと飛び先が壊れる/枠が消えるグループ ===')
broke, ok, exactdup = [], [], []
tot_vis = 0; tot_union = 0
for k,g in dg.items():
    vis = [(e, t) for e in g for t in (e.get('tickets') or []) if visible(t)]
    tot_vis += len(vis)
    # 表示上ユニークな枠 = (type, 実効URL)
    ukeys = set((t.get('type'), eff(e,t)) for e,t in vis)
    tot_union += len(ukeys)
    # カード共通リンクが2種類以上 かつ url=None の可視枠を持つエントリが2つ以上 → 畳むと飛び先が変わる
    inheritors = [e for e in g if any(visible(t) and not t.get('url') for t in (e.get('tickets') or []))]
    cl = set(cardlink(e) for e in inheritors)
    # type だけ見た時の衝突（畳むと同名枠に見える）
    tkeys = collections.Counter(t.get('type') for e,t in vis)
    collide = {kk:c for kk,c in tkeys.items() if c>1}
    # 完全同一エントリ（可視枠のtype集合が一致し、片方が他方の部分集合でなく同一）
    setsig = [tuple(sorted(t.get('type') for t in (e.get('tickets') or []) if visible(t))) for e in g]
    if len(g)==2 and setsig[0]==setsig[1] and setsig[0]:
        exactdup.append((g[0].get('name'), [e.get('id') for e in g], len(setsig[0])))
    if len(cl) > 1 and len(inheritors) > 1:
        broke.append((g[0].get('name'), [e.get('id') for e in g],
                      [(e.get('id'), cardlink(e)) for e in inheritors], collide))
for name, ids, inh, collide in sorted(broke, key=lambda x:x[0]):
    print('\n■ %s %s' % (name, ids))
    for i,u in inh: print('    id=%s のカード共通リンク: %s' % (i,u))
    if collide: print('    ★ 券種名が衝突（畳むと見分けがつかない）: %s' % (list(collide.items()),))
print('\n飛び先が変わりうるグループ数: %d / %d' % (len(broke), len(dg)))
print('可視枠 合計=%d / (type,実効URL) ユニーク=%d  → 畳むと消える見かけ上の枠=%d' % (tot_vis, tot_union, tot_vis-tot_union))

print('\n=== 可視枠が完全一致する2エントリ（真の重複登録） ===')
for n,ids,c in exactdup: print('  %s %s (可視枠%d本が同一)' % (n, ids, c))

print('\n=== 同名グループ内での (type,date,url) 完全重複 ===')
sm = collections.defaultdict(list)
for k,g in dg.items():
    for e in g:
        for t in (e.get('tickets') or []):
            sm[(k, t.get('type'), t.get('date'), t.get('url'))].append(e.get('id'))
d2 = {kk:v for kk,v in sm.items() if len(set(v))>=2}
print('  重複キー数: %d / 重複行数: %d' % (len(d2), sum(len(v) for v in d2.values())))
for kk,v in sorted(d2.items()):
    print('    ids=%s type=%s' % (sorted(set(v)), kk[1]))

print('\n=== 全体（同名かどうかに関係なく） (type,date,url) 重複 ===')
sm2 = collections.defaultdict(list)
for e in EVENTS:
    for t in (e.get('tickets') or []):
        sm2[(t.get('type'), t.get('date'), t.get('url'))].append(e.get('id'))
d3 = {kk:v for kk,v in sm2.items() if len(set(v))>=2}
print('  キー数: %d / 行数: %d' % (len(d3), sum(len(v) for v in d3.values())))
# url が None のせいで衝突しているだけのものを除く
d4 = {kk:v for kk,v in d3.items() if kk[2]}
print('  うち url が実在するもの: キー数=%d / 行数=%d' % (len(d4), sum(len(v) for v in d4.values())))
for kk,v in sorted(d4.items())[:30]:
    print('    ids=%s type=%s url=%s' % (sorted(set(v)), kk[0], kk[2]))
