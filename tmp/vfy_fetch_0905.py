# -*- coding: utf-8 -*-
"""独立検証: 対象エントリの e+ 個別ページを生HTMLで取得し、JSON-LD と 受付期間を自力で抜く。"""
import urllib.request, re, json, io, sys, time, os
import html as H

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

UA = {'User-Agent': 'Mozilla/5.0'}
CACHE = r'C:\Users\user\oshinavi\tmp\vfy_html_0905'
os.makedirs(CACHE, exist_ok=True)

URLS = json.load(open(r'C:\Users\user\oshinavi\tmp\vfy_urls_0905.json', encoding='utf-8'))

targets = []
seen = set()
for eid, u in URLS:
    if u.startswith('LINK:'):
        kind = u.split(':', 1)[1]
        if kind.startswith('eplus:'):
            u2 = kind[len('eplus:'):]
        else:
            continue
    else:
        u2 = u
    if 'eplus.jp' not in u2:
        continue
    if (eid, u2) in seen:
        continue
    seen.add((eid, u2))
    targets.append((eid, u2))


def fetch(url, tries=3):
    fn = os.path.join(CACHE, re.sub(r'[^A-Za-z0-9]', '_', url)[-120:] + '.html')
    if os.path.exists(fn):
        return io.open(fn, encoding='utf-8').read()
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
            io.open(fn, 'w', encoding='utf-8').write(h)
            time.sleep(0.8)
            return h
        except Exception as e:
            last = e
            time.sleep(2 * (i + 1))
    raise last


def parse_ld(html):
    evs = []
    for blob in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(blob)
        except Exception:
            continue
        items = d if isinstance(d, list) else [d]
        for it in items:
            if not isinstance(it, dict) or it.get('@type') != 'Event':
                continue
            full = it.get('startDate') or ''
            loc = it.get('location') or {}
            venue = loc.get('name') if isinstance(loc, dict) else ''
            pref = ''
            if isinstance(loc, dict) and isinstance(loc.get('address'), dict):
                pref = loc['address'].get('addressRegion') or ''
                pref2 = loc['address'].get('addressLocality') or ''
            else:
                pref2 = ''
            evs.append({'name': H.unescape(it.get('name') or '').strip(),
                        'date': full[:10], 'time': full[11:16] if 'T' in full else '',
                        'venue': H.unescape(venue or '').strip(),
                        'pref': pref, 'locality': pref2,
                        'url': (it.get('url') or '').strip(),
                        'perf': it.get('performer')})
    uniq = {}
    for e in evs:
        uniq[(e['date'], e['time'], e['venue'])] = e
    return list(uniq.values())


def flat(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(x))).strip()


PERIOD = re.compile(r'受付期間:(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})'
                    r'～(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})')


def parse_windows(html):
    out = []
    secs = [s for s in re.split(r'(?=<section class="block-ticket">)', html)
            if s.startswith('<section class="block-ticket">')]
    if not secs:
        for inner in re.findall(r'block-ticket__header[^>]*>(.*?)</header>', html, re.S):
            t = flat(inner)
            m = PERIOD.search(t)
            if m:
                out.append({'raw': t, 'status': '(section無)', 'm': m.groups()})
        return out
    for sec in secs:
        body = sec.split('</section>', 1)[0]
        span = re.search(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', body)
        stxt = span.group(1).strip() if span else ''
        hm = re.search(r'block-ticket__header[^>]*>(.*?)</header>', body, re.S)
        t = flat(hm.group(1) if hm else body)
        m = PERIOD.search(t)
        out.append({'raw': t[:220], 'status': stxt, 'm': (m.groups() if m else None)})
    return out


def perf_block(html):
    # 出演 欄
    res = []
    for m in re.finditer(r'(出演|出演者|出演アーティスト)\s*</[^>]+>(.{0,900}?)</(?:dd|td|div|p)>', html, re.S):
        res.append(flat(m.group(2))[:300])
    # meta description も参考に
    md = re.search(r'<meta name="description" content="([^"]*)"', html)
    return res, (H.unescape(md.group(1)) if md else '')


lines = []
for eid, u in targets:
    lines.append('##### id=%s  %s' % (eid, u))
    try:
        h = fetch(u)
    except Exception as e:
        lines.append('  !! 取得失敗: %s' % e)
        lines.append('')
        continue
    ti = re.search(r'<title>(.*?)</title>', h, re.S)
    lines.append('  <title>: %s' % (flat(ti.group(1)) if ti else ''))
    lds = parse_ld(h)
    if not lds:
        lines.append('  !! JSON-LD Event なし')
    for e in lds:
        lines.append('  LD: name=%s | date=%s %s | venue=%s | region=%s | locality=%s' % (
            e['name'], e['date'], e['time'], e['venue'], e['pref'], e['locality']))
        if e.get('perf'):
            lines.append('      performer=%s' % json.dumps(e['perf'], ensure_ascii=False)[:300])
    for w in parse_windows(h):
        g = w['m']
        if g:
            per = '%s/%s/%s %s:%s ～ %s/%s/%s %s:%s' % (g[0], g[1], g[2], g[3], g[4], g[5], g[6], g[7], g[8], g[9])
        else:
            per = '(受付期間なし)'
        lines.append('  WIN[%s]: %s | %s' % (w['status'], per, w['raw'][:160]))
    pb, desc = perf_block(h)
    for p in pb[:3]:
        lines.append('  出演欄: %s' % p)
    lines.append('  meta desc: %s' % desc[:300])
    lines.append('')

io.open(r'C:\Users\user\oshinavi\tmp\vfy_pages_0905.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done %d urls' % len(targets))
