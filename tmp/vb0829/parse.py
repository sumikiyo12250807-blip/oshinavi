# -*- coding: utf-8 -*-
import json, os, re, sys, html as H
sys.path.insert(0, 'tmp/vb0829')
sys.stdout.reconfigure(encoding='utf-8')
from fetch import get

def txt(s):
    s = re.sub(r'(?s)<script.*?</script>', ' ', s)
    s = re.sub(r'(?s)<style.*?</style>', ' ', s)
    s = re.sub(r'(?s)<[^>]+>', '\x01', s)
    s = H.unescape(s).replace(' ', ' ')
    s = re.sub(r'[\x01\s]*\x01[\x01\s]*', '\x01', s)
    return s.strip('\x01 ')

def flat(s):
    return re.sub(r'\s+', ' ', txt(s).replace('\x01', ' ')).strip()

START = re.compile(r'<li class="ticketSalesList-2024__item vevent"')
ANY = re.compile(r'<li class="ticketSalesList-2024__item')

def _blocks(h):
    for m in START.finditer(h):
        nx = ANY.search(h, m.end())
        yield h[m.start(): nx.start() if nx else min(len(h), m.start() + 6000)]

def cards(h):
    out, seen = [], set()
    for c in _blocks(h):
        url = re.search(r'href="([^"]+)"', c)
        title = re.search(r'(?s)ticketSalesCard-2024__title">(.*?)</p>', c)
        sd = re.findall(r'itemprop="(startDate|endDate)" datetime="([^"]+)"', c)
        place = re.search(r'(?s)ticketSalesCard-2024__place"[^>]*>(.*?)</span>', c)
        region = re.search(r'(?s)ticketSalesCard-2024__region">(.*?)</span>', c)
        st = re.search(r'(?s)ticketSalesCard-2024__status ([\w-]*)">(.*?)</p>', c)
        tags = [flat(x) for x in re.findall(r'(?s)<span class="tag\w+-2024">(.*?)</span>', c)]
        d = dict(url=H.unescape(url.group(1)) if url else '',
                 title=flat(title.group(1)) if title else '',
                 pdates=[v[:10] for k, v in sd],
                 place=flat(place.group(1)) if place else '',
                 region=flat(region.group(1)) if region else '',
                 stcls=st.group(1) if st else '', sttxt=flat(st.group(2)) if st else '',
                 tags=tags)
        k = (d['url'], d['title'])
        if k in seen: continue
        seen.add(k); out.append(d)
    return out

DATE = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})\s*\(\s*([日月火水木金土](?:\s*・\s*祝)?)\s*\)')

def ti_detail(h):
    d = {}
    ttl = re.search(r'(?s)<title>(.*?)</title>', h)
    d['title'] = H.unescape(ttl.group(1)).strip() if ttl else ''
    body = h[h.find('<body'):]
    # --- 販売枠の頭（h1 〜 リセール/その他のチケット販売情報） ---
    i = body.find('<h1')
    j = body.find('その他のチケット販売情報')
    head = txt(body[i:j if j > i else i + 20000])
    head = head.split('\x01@import')[0]
    d['head'] = [re.sub(r'\s+', ' ', x).strip() for x in head.split('\x01') if x.strip()][:14]
    # --- 公演日時・座席 一覧 ---
    k = body.find('公演日時・座席')
    m = body.find('利用可能な決済方法')
    seg = re.sub(r'\s+', ' ', txt(body[k:m if m > k else k + 80000]).replace('\x01', ' '))
    perf, seen = [], set()
    ms = list(DATE.finditer(seg))
    for n, dm in enumerate(ms):
        end = ms[n + 1].start() if n + 1 < len(ms) else min(len(seg), dm.end() + 600)
        blk = seg[dm.end():end]
        tm = re.search(r'(\d{1,2}:\d{2})\s*開演', blk)
        vm = re.search(r'会場：\s*(.+?)\s*\(\s*(北海道|東京都|大阪府|京都府|[^\s()（）]{2,4}県|海外)\s*\)', blk)
        cur = dict(date='%s/%s/%s(%s)' % dm.groups(), time=tm.group(1) if tm else '',
                   venue=vm.group(1).strip() if vm else '', pref=vm.group(2) if vm else '')
        kk = (cur['date'], cur['time'], cur['venue'])
        if kk in seen or not cur['venue']: continue
        seen.add(kk); perf.append(cur)
    d['perf'] = perf
    # 席種・価格
    d['seats'] = sorted(set(re.findall(r'((?:全席|[SA-DＳＡ-Ｄ]席|指定席|自由席|立見|当日券)[^ ]{0,14} ?\d{3,6}円)', seg)))[:14]
    return d

items = json.load(open('tmp/verify_in_b_0829.json', encoding='utf-8'))
res = []
for it in items:
    u = it['urls'][0]
    h = get(u)
    if not h:
        res.append(dict(id=it['id'], url=u, fail=True)); print('FAIL', it['id'], file=sys.stderr); continue
    ttl = H.unescape(re.search(r'(?s)<title>(.*?)</title>', h).group(1)).strip()
    h1 = re.search(r'(?s)<h1[^>]*>(.*?)</h1>', h)
    gm = re.search(r'\[([^\]\s]+)\s+(.+?)のチケット', ttl)
    gcd = re.search(r'(?:ntSgenreCd|genreCd)"\s*value="(\d{7})"', h)
    cs = cards(h)
    ent = dict(id=it['id'], url=u, page_title=ttl,
               h1=flat(h1.group(1)) if h1 else '',
               genre=(gm.group(1) + '/' + gm.group(2)) if gm else '',
               genreCd=gcd.group(1) if gcd else '', slots=[])
    for c in cs:
        th = get(c['url'])
        ent['slots'].append(dict(card=c, detail=ti_detail(th) if th else None, ok=bool(th)))
    res.append(ent)
    print('done', it['id'], len(cs), sum(1 for s in ent['slots'] if not s['ok']), file=sys.stderr)
json.dump(res, open('tmp/vb0829/parsed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('OK', len(res))
