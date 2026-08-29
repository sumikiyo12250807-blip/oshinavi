# -*- coding: utf-8 -*-
"""agentlist_2_0827 の50URLをぴあから機械抽出。pia_tickets.py と同一のカード解析ロジック。
1件ごとにsleepし、sorry.pia/429は再試行する。結果はJSONで保存。"""
import urllib.request, re, io, sys, html as _html, json, time, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

LIST = r'C:\Users\user\oshinavi\tmp\agentlist_2_0827.txt'
OUT = r'C:\Users\user\oshinavi\tmp\agent2_result_0827.json'
CACHE = r'C:\Users\user\oshinavi\tmp\agent2_cache'
os.makedirs(CACHE, exist_ok=True)


class PiaSorry(Exception):
    pass


def _get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        final = r.geturl()
        body = r.read().decode('utf-8', 'replace')
    if 'sorry.pia' in final or 'sorry.pia' in body[:4000]:
        raise PiaSorry('sorry')
    return body


def fetch(u, tries=5):
    key = re.sub(r'[^A-Za-z0-9]', '_', u)[-60:]
    p = os.path.join(CACHE, key + '.html')
    if os.path.exists(p) and os.path.getsize(p) > 5000:
        with io.open(p, encoding='utf-8') as f:
            return f.read()
    last = None
    for i in range(tries):
        try:
            b = _get(u)
            with io.open(p, 'w', encoding='utf-8') as f:
                f.write(b)
            return b
        except Exception as e:
            last = e
            time.sleep(6 + i * 6)
    raise last


def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()


def parse_cards(h):
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
        perf_start = _dts[0] if _dts else ''
        perf_end = _dts[-1] if _dts else ''
        m_stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        m_sdate = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        stat_text = txt(m_stat.group(2)) if m_stat else ''
        cls = m_stat.group(1) if m_stat else ''
        sdate = txt(m_sdate.group(1)) if m_sdate else ''
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|販売期間終了|終了しました|結果発表)', stat_text):
            state = '受付終了'
        elif cls == 'is-active' or re.search(r'(販売期間中|受付中|発売中|販売中|発売初日|本日発売)', stat_text):
            state = '受付中'
        elif cls == 'is-before' or '発売前' in stat_text or 'まもなく' in stat_text:
            state = '発売前'
        else:
            state = '受付終了'
        rows.append({
            'perfdate': perf_start, 'perf_end': perf_end, 'statustext': stat_text,
            'venue': txt(m_place.group(1)) if m_place else '',
            'pref': txt(m_region.group(1)) if m_region else '',
            'title': txt(m_title.group(1)) if m_title else '',
            'state': state, 'when': sdate,
            'url': m_url.group(1) if m_url else '',
        })
    seen = set(); uniq = []
    for r in rows:
        k = (r['perfdate'], r['perf_end'], r['venue'], r['title'], r['state'], r['when'], r['url'])
        if k in seen:
            continue
        seen.add(k); uniq.append(r)
    return uniq


def page_title(h):
    m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    if m:
        t = txt(m.group(1))
        if t:
            return t
    m = re.search(r'<title>(.*?)</title>', h, re.S)
    return txt(m.group(1)) if m else ''


def confirm_msg(h):
    # 「ご確認ください」系のぴあ側メッセージ
    hits = []
    for m in re.finditer(r'ご確認ください', h):
        s = max(0, m.start() - 200)
        hits.append(txt(h[s:m.end() + 60]))
    return hits[:2]


def child_links(h):
    out = []
    for m in re.finditer(r'href="([^"]*event\.do\?eventCd=\d+[^"]*)"', h):
        u = _html.unescape(m.group(1))
        if u.startswith('/'):
            u = 'https://t.pia.jp' + u
        cd = re.search(r'eventCd=(\d+)', u).group(1)
        u = 'https://t.pia.jp/pia/event/event.do?eventCd=' + cd
        if u not in out:
            out.append(u)
    return out


urls = []
with io.open(LIST, encoding='utf-8') as f:
    for line in f:
        m = re.match(r'\s*(\d+)\.\s*(https?://\S+)', line)
        if m:
            urls.append((int(m.group(1)), m.group(2)))

results = []
for no, u in urls:
    rec = {'no': no, 'url': u, 'error': '', 'title': '', 'cards': [], 'children': [], 'confirm': []}
    try:
        h = fetch(u)
        rec['title'] = page_title(h)
        rec['cards'] = parse_cards(h)
        rec['confirm'] = confirm_msg(h)
        if 'eventBundleCd' in u:
            kids = child_links(h)
            for k in kids:
                kr = {'url': k, 'error': '', 'title': '', 'cards': []}
                try:
                    hk = fetch(k)
                    kr['title'] = page_title(hk)
                    kr['cards'] = parse_cards(hk)
                except Exception as e:
                    kr['error'] = type(e).__name__ + ':' + str(e)[:120]
                rec['children'].append(kr)
                time.sleep(3)
    except Exception as e:
        rec['error'] = type(e).__name__ + ':' + str(e)[:160]
    results.append(rec)
    print('%d done cards=%d kids=%d err=%s' % (no, len(rec['cards']), len(rec['children']), rec['error']))
    sys.stdout.flush()
    time.sleep(3)

with io.open(OUT, 'w', encoding='utf-8') as f:
    f.write(json.dumps(results, ensure_ascii=False, indent=1))
print('SAVED', OUT)
