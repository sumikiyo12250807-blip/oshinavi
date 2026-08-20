# -*- coding: utf-8 -*-
"""投入54件(genre:new)を独立再取得して照合。アンカリングせずぴあから再導出。"""
import json, io, sys, re, urllib.request, html as _html, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
new = [e for e in arr if e.get('genre') == 'new']

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
        when = clean((re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S) or [None,''])[1] if re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S) else '')
        m2 = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        when = clean(m2.group(1)) if m2 else ''
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|終了しました|結果発表)', stt): state = '終了'
        elif cls == 'is-active' or re.search(r'(販売期間中|受付中)', stt): state = '受付中'
        elif cls == 'is-before' or '発売前' in stt or 'まもなく' in stt: state = '発売前'
        else: state = '終了'
        out.append({'state': state, 'when': when})
    return out
def end_iso(w):  # 受付中: ～END
    m = re.search(r'～\s*(\d{4})/(\d{1,2})/(\d{1,2})', w); return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None
def start_iso(w):  # 発売前: START より発売 / START ～
    m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', w); return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None

issues = []
for e in new:
    urls = []
    p = (e.get('links') or {}).get('pia')
    if p: urls.append(p)
    for t in e['tickets']:
        if t.get('url') and t['url'] not in urls: urls.append(t['url'])
    live = []
    for u in urls:
        try: live += cards(fetch(u)); time.sleep(0.2)
        except Exception as ex: issues.append((e['id'], 'FETCH_ERR', str(ex)[:30]))
    buy = [c for c in live if c['state'] in ('受付中', '発売前')]
    # live sale-dates
    live_dates = set()
    for c in buy:
        d = end_iso(c['when']) if c['state'] == '受付中' else start_iso(c['when'])
        if d: live_dates.add(d)
    inj_dates = set(t['date'] for t in e['tickets'])
    # checks
    if not buy:
        issues.append((e['id'], 'SOLD_OUT', f"買える枠0なのに投入({len(e['tickets'])}枠) {e['name'][:20]}"))
        continue
    missing = live_dates - inj_dates
    extra = inj_dates - live_dates
    if missing:
        issues.append((e['id'], 'DROPPED', f"ぴあにあるが未投入の販売日{sorted(missing)} {e['name'][:18]}"))
    if extra:
        issues.append((e['id'], 'STALE', f"投入したがぴあに無い販売日{sorted(extra)} {e['name'][:18]}"))
    # 公演日が販売終了日より前(cap逆転)チェック
    perf = e.get('date')
    for t in e['tickets']:
        if not t.get('startDate') and t['date'] > perf:
            issues.append((e['id'], 'DATE_CAP', f"販売終了{t['date']}>公演{perf} {e['name'][:18]}"))

print(f"検証 {len(new)}件 / 問題 {len(issues)}件")
for x in issues: print("  ", x)
json.dump(issues, open('tmp/verify_issues.json','w',encoding='utf-8'), ensure_ascii=False)
