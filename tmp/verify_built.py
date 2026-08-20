# -*- coding: utf-8 -*-
"""built200_clean.json を独立再取得して照合（売切混入/取りこぼし/日付ズレ）。"""
import json, io, sys, re, urllib.request, html as _html, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ents = json.load(open('tmp/built200_clean.json', encoding='utf-8'))
def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
def clean(s): return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()
def cards(h):
    out = []
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)', h):
        if 'ticketSalesCard-2024__status' not in it: continue
        st = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        cls = st.group(1) if st else ''; stt = clean(st.group(2)) if st else ''
        m2 = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        when = clean(m2.group(1)) if m2 else ''
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|終了しました|結果発表)', stt): state = '終了'
        elif cls == 'is-active' or re.search(r'(販売期間中|受付中)', stt): state = '受付中'
        elif cls == 'is-before' or '発売前' in stt or 'まもなく' in stt: state = '発売前'
        else: state = '終了'
        out.append({'state': state, 'when': when})
    return out
def edate(w):
    m = re.search(r'～\s*(\d{4})/(\d{1,2})/(\d{1,2})', w); return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None
def sdate(w):
    m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', w); return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None
issues = []
for n, e in enumerate(ents, 1):
    urls = [(e.get('links') or {}).get('pia')]
    for t in e['tickets']:
        if t.get('url') and t['url'] not in urls: urls.append(t['url'])
    live = []
    for u in urls:
        if not u: continue
        try: live += cards(fetch(u)); time.sleep(0.18)
        except Exception as ex: issues.append((e['id'],'FETCH_ERR',str(ex)[:20]))
    buy = [c for c in live if c['state'] in ('受付中','発売前')]
    if not buy:
        issues.append((e['id'],'SOLD_OUT',e['name'][:24]));
        sys.stderr.write(f"[{n}/{len(ents)}] id{e['id']} SOLD_OUT\n"); continue
    live_dates = set()
    for c in buy:
        d = edate(c['when']) if c['state']=='受付中' else sdate(c['when'])
        if d: live_dates.add(d)
    inj = set(t['date'] for t in e['tickets'])
    miss = live_dates - inj
    if miss: issues.append((e['id'],'DROPPED',sorted(miss),e['name'][:18]))
    sys.stderr.write(f"[{n}/{len(ents)}] id{e['id']} ok\n"); sys.stderr.flush()
print(f"検証 {len(ents)}件 / 問題 {len(issues)}件")
for x in issues: print("  ", x)
json.dump(issues, open('tmp/verify200_issues.json','w',encoding='utf-8'), ensure_ascii=False)
