# -*- coding: utf-8 -*-
"""削除候補の各エントリについて links.pia + 全ticket.url の全ぴあURLを開き、
受付中/発売前が1つでもあれば「買える(=削除NG)」と判定。pia_tickets.pyのパーサ流用。"""
import json, io, sys, re, urllib.request, html as _html, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
def clean(s): return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
def buyable(h):
    out=[]
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)', h):
        if 'ticketSalesCard-2024__status' not in it: continue
        m=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)', it, re.S)
        st=clean(m.group(2)) if m else ''
        m2=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        when=clean(m2.group(1)) if m2 else ''
        mt=re.search(r'__title">(.*?)</p>', it, re.S); ti=clean(mt.group(1)) if mt else ''
        if re.search(r'(販売期間中|受付中)', st): out.append(('受付中',ti[:30],when))
        elif '発売前' in st: out.append(('発売前',ti[:30],when))
    return out

cands=[416,441,515,542,547,640,679,691,816,899,951,968,974,228,258,393]
for eid in cands:
    e=byid[eid]
    urls=set()
    p=(e.get('links') or {}).get('pia')
    if p: urls.add(p)
    for t in e['tickets']:
        if t.get('url'): urls.add(t['url'])
    found=[]
    for u in urls:
        try:
            b=buyable(fetch(u))
            found += [(u[-18:],)+x for x in b]
        except Exception as ex:
            found.append((u[-18:],'ERR',str(ex)[:30],''))
        time.sleep(0.3)
    flag='★買える(削除NG)' if any(x[1] in ('受付中','発売前') for x in found) else '全終了(削除OK)'
    print(f"id{eid} {e['name'][:24]} [{len(urls)}URL] -> {flag}")
    for x in found: print("     ",x)
