# -*- coding: utf-8 -*-
"""独立再導出: プールの各行についてぴあ実ページから
買える枠数/千秋楽/県/公演名/ジャンル を自力で読む。"""
import urllib.request, re, io, sys, json, os, time, html as _html
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = r'C:\Users\user\oshinavi\tmp\_poolgrp2_0831.txt'
OUT = r'C:\Users\user\oshinavi\tmp\_agentP2_result.json'
CACHE = r'C:\Users\user\oshinavi\tmp\_agentP2_cache'
os.makedirs(CACHE, exist_ok=True)


class PiaSorry(Exception):
    pass


def fetch(u, force=False):
    key = re.sub(r'[^\w]', '_', u)[-80:]
    p = os.path.join(CACHE, key + '.html')
    if not force and os.path.exists(p) and os.path.getsize(p) > 5000:
        return open(p, encoding='utf-8').read()
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        final = r.geturl()
        body = r.read().decode('utf-8', 'replace')
    if 'sorry.pia' in final or 'sorry.pia' in body[:4000]:
        raise PiaSorry('sorry page')
    open(p, 'w', encoding='utf-8').write(body)
    return body


def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()


def parse(h):
    items = re.split(r'(?=<li class="ticketSalesList-2024__item)', h)
    rows = []
    for it in items:
        if 'ticketSalesCard-2024__status' not in it:
            continue
        m_url = re.search(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"', it)
        m_title = re.search(r'__title">(.*?)</p>', it, re.S)
        m_place = re.search(r'__place"[^>]*>(.*?)</span>', it, re.S)
        m_region = re.search(r'__region">(.*?)</span>', it, re.S)
        _dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
        m_stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        m_sdate = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        stat_text = txt(m_stat.group(2)) if m_stat else ''
        cls = m_stat.group(1) if m_stat else ''
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|販売期間終了|終了しました|結果発表)', stat_text):
            state = '受付終了'
        elif cls == 'is-active' or re.search(r'(販売期間中|受付中|発売中|販売中|発売初日|本日発売)', stat_text):
            state = '受付中'
        elif cls == 'is-before' or '発売前' in stat_text or 'まもなく' in stat_text:
            state = '発売前'
        else:
            state = '受付終了'
        rows.append({
            'perfdate': _dts[0] if _dts else '',
            'perf_end': _dts[-1] if _dts else '',
            'statustext': stat_text, 'cls': cls,
            'venue': txt(m_place.group(1)) if m_place else '',
            'pref': txt(m_region.group(1)) if m_region else '',
            'title': txt(m_title.group(1)) if m_title else '',
            'state': state,
            'when': txt(m_sdate.group(1)) if m_sdate else '',
            'url': m_url.group(1) if m_url else '',
        })
    seen = set(); uniq = []
    for r in rows:
        k = (r['perfdate'], r['perf_end'], r['venue'], r['title'], r['state'], r['when'], r['url'])
        if k in seen:
            continue
        seen.add(k); uniq.append(r)
    return uniq


def meta(h):
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    t = _html.unescape(re.sub(r'\s+', ' ', t.group(1))).strip() if t else ''
    g = ''
    mg = re.search(r'\[(.*?)のチケット購入・予約\]', t)
    if mg:
        g = mg.group(1)
    name = t.split('|')[0].strip()
    crumbs = re.findall(r'breadCrumb-2024__item[^>]*>(?:<a[^>]*>)?(.*?)(?:</a>)?</li>', h, re.S)
    crumbs = [txt(c) for c in crumbs]
    return {'pagetitle': t, 'genre': g, 'name': name, 'crumbs': crumbs}


lines = [l.rstrip('\n') for l in open(SRC, encoding='utf-8') if l.strip()]
res = []
for i, l in enumerate(lines, 1):
    parts = l.split('|')
    if len(parts) < 6:
        continue
    eid, nm, dt, pref, cnt, url = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
    rec = {'id': eid, 'reg_name': nm, 'reg_date': dt, 'reg_pref': pref, 'reg_count': int(cnt), 'url': url}
    try:
        h = fetch(url)
        rows = parse(h)
        buy = [r for r in rows if r['state'] in ('受付中', '発売前')]
        if not buy:
            time.sleep(4)
            h = fetch(url, force=True)
            rows = parse(h)
            buy = [r for r in rows if r['state'] in ('受付中', '発売前')]
        rec.update(meta(h))
        rec['rows'] = rows
        rec['buyable'] = len(buy)
        rec['active'] = len([r for r in rows if r['state'] == '受付中'])
        rec['before'] = len([r for r in rows if r['state'] == '発売前'])
        rec['ended'] = len([r for r in rows if r['state'] == '受付終了'])
        alld = [r['perf_end'] or r['perfdate'] for r in rows if (r['perf_end'] or r['perfdate'])]
        buyd = [r['perf_end'] or r['perfdate'] for r in buy if (r['perf_end'] or r['perfdate'])]
        rec['maxdate_all'] = max(alld) if alld else ''
        rec['maxdate_buy'] = max(buyd) if buyd else ''
        rec['prefs_all'] = sorted(set(r['pref'] for r in rows if r['pref']))
        rec['prefs_buy'] = sorted(set(r['pref'] for r in buy if r['pref']))
        rec['ok'] = True
    except Exception as e:
        rec['ok'] = False
        rec['err'] = type(e).__name__ + ': ' + str(e)[:120]
    res.append(rec)
    print(f"{i}/{len(lines)} {eid} ok={rec['ok']} buy={rec.get('buyable')}")
    sys.stdout.flush()
    time.sleep(1.2)

json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('DONE', len(res))
