# -*- coding: utf-8 -*-
import urllib.request, re, json, io, sys, time, os
import html as H
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml',
      'Accept-Language': 'ja,en;q=0.8'}
CACHE = r'C:\Users\user\oshinavi\tmp\vfy_html_0905'

URLS = [
    (6940, 'https://eplus.jp/sf/detail/4579740001-P0030001P021001'),
    (6943, 'https://eplus.jp/sf/detail/4588480001-P0030001P021001'),
    (6295, 'https://eplus.jp/sf/detail/0314250001-P0030050P021001'),
]

def flat(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(x))).strip()

PERIOD = re.compile(r'受付期間:(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})'
                    r'～(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})')

lines = []
for eid, u in URLS:
    h = None
    err = ''
    for i in range(6):
        try:
            req = urllib.request.Request(u, headers=UA)
            h = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
            break
        except Exception as e:
            err = str(e)
            time.sleep(4 + 4 * i)
    lines.append('##### id=%s %s' % (eid, u))
    if h is None:
        lines.append('  !! 取得失敗: %s' % err)
        lines.append('')
        continue
    fn = os.path.join(CACHE, re.sub(r'[^A-Za-z0-9]', '_', u)[-120:] + '.html')
    io.open(fn, 'w', encoding='utf-8').write(h)
    ti = re.search(r'<title>(.*?)</title>', h, re.S)
    lines.append('  <title>: %s' % (flat(ti.group(1)) if ti else ''))
    for blob in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try:
            d = json.loads(blob)
        except Exception:
            continue
        for it in (d if isinstance(d, list) else [d]):
            if not isinstance(it, dict) or it.get('@type') != 'Event':
                continue
            loc = it.get('location') or {}
            addr = loc.get('address') if isinstance(loc, dict) else {}
            lines.append('  LD: name=%s | start=%s | venue=%s | region=%s' % (
                it.get('name'), it.get('startDate'),
                (loc.get('name') if isinstance(loc, dict) else ''),
                (addr.get('addressRegion') if isinstance(addr, dict) else '')))
    secs = [s for s in re.split(r'(?=<section class="block-ticket">)', h) if s.startswith('<section class="block-ticket">')]
    for sec in secs:
        body = sec.split('</section>', 1)[0]
        span = re.search(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', body)
        hm = re.search(r'block-ticket__header[^>]*>(.*?)</header>', body, re.S)
        t = flat(hm.group(1) if hm else body)
        m = PERIOD.search(t)
        per = ('%s/%s/%s %s:%s ～ %s/%s/%s %s:%s' % m.groups()) if m else '(なし)'
        lines.append('  WIN[%s]: %s | %s' % (span.group(1).strip() if span else '', per, t[:170]))
    for m in re.finditer(r'(出演|出演者)\s*</[^>]+>(.{0,800}?)</(?:dd|td|div|p)>', h, re.S):
        lines.append('  出演欄: %s' % flat(m.group(2))[:250])
    md = re.search(r'<meta name="description" content="([^"]*)"', h)
    lines.append('  meta: %s' % (H.unescape(md.group(1))[:280] if md else ''))
    lines.append('')
    time.sleep(2)

io.open(r'C:\Users\user\oshinavi\tmp\vfy_retry_0905.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')
