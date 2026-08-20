# -*- coding: utf-8 -*-
"""旧bundle(verifiedAt<6/19)218件を機械監査。
ぴあbundleの買える公演数(受付中+発売前の distinct perfdate) vs 登録ticket数を比較。
取りこぼし疑い(ぴあの方がずっと多い)を炙り出す。"""
import json, io, sys, re, urllib.request, html as _html, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8','replace')
def clean(s): return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
def buyable_perfs(h):
    perfs=set()
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)', h):
        if 'ticketSalesCard-2024__status' not in it: continue
        m=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)', it, re.S); st=clean(m.group(2)) if m else ''
        dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
        mp=re.search(r'__place"[^>]*>(.*?)</span>', it, re.S); ven=clean(mp.group(1)) if mp else ''
        if re.search(r'(販売期間中|受付中)',st) or '発売前' in st:
            perfs.add((dts[0] if dts else '', ven))
    return perfs

cands=[]
for e in arr:
    pia=(e.get('links') or {}).get('pia') or ''
    if 'eventBundleCd' in pia and e.get('verifiedAt','')<'2026-06-19':
        cands.append(e)

out=[]
for n,e in enumerate(cands,1):
    pia=e['links']['pia']
    try:
        bp=buyable_perfs(fetch(pia))
    except Exception as ex:
        out.append((e['id'],-1,len(e['tickets']),e['name'][:30],'ERR'));
        sys.stderr.write(f"[{n}/{len(cands)}] id{e['id']} ERR\n"); time.sleep(0.2); continue
    nt=len(e['tickets'])
    out.append((e['id'], len(bp), nt, e['name'][:30], ''))
    sys.stderr.write(f"[{n}/{len(cands)}] id{e['id']} bundle買える公演{len(bp)} vs 枠{nt}\n"); sys.stderr.flush()
    time.sleep(0.25)

# flag: bundle買える公演 >= 枠+3 かつ bundle>=4
flagged=[o for o in out if o[1]>=4 and o[1]-o[2]>=3]
flagged.sort(key=lambda o:o[1]-o[2], reverse=True)
res={'flagged':flagged,'all':out}
json.dump(res, open('tmp/old_tour_audit.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"\n==== 取りこぼし疑い {len(flagged)}件 (ぴあ買える公演 ≫ 登録枠) ====")
for eid,bp,nt,nm,err in flagged:
    print(f"  id{eid} ぴあ{bp}公演 vs 枠{nt} (差{bp-nt}) | {nm}")
errs=[o for o in out if o[1]==-1]
print(f"\nERR {len(errs)}件:", [o[0] for o in errs])
