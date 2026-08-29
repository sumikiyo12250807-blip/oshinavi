# -*- coding: utf-8 -*-
"""bundle配下の個別eventCdページを開いて、まとめページに出ない枠が無いか確認する。"""
import io, json, sys, re, time
sys.path.insert(0, r'C:\Users\user\oshinavi\tmp')
import importlib.util
spec = importlib.util.spec_from_file_location('scan', r'C:\Users\user\oshinavi\tmp\agent2_scan_0827.py')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# scanモジュールは実行してしまうので、必要な関数だけ再定義
import urllib.request, html as _html, os
CACHE = r'C:\Users\user\oshinavi\tmp\agent2_cache'


class PiaSorry(Exception):
    pass


def _get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        final = r.geturl(); body = r.read().decode('utf-8', 'replace')
    if 'sorry.pia' in final or 'sorry.pia' in body[:4000]:
        raise PiaSorry('sorry')
    return body


def fetch(u, tries=5):
    key = re.sub(r'[^A-Za-z0-9]', '_', u)[-60:]
    p = os.path.join(CACHE, key + '.html')
    if os.path.exists(p) and os.path.getsize(p) > 5000:
        return io.open(p, encoding='utf-8').read()
    last = None
    for i in range(tries):
        try:
            b = _get(u)
            io.open(p, 'w', encoding='utf-8').write(b)
            return b
        except Exception as e:
            last = e; time.sleep(6 + i * 6)
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
        m_stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        m_sdate = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        stat_text = txt(m_stat.group(2)) if m_stat else ''
        rows.append((_dts[0] if _dts else '', _dts[-1] if _dts else '', stat_text,
                     txt(m_region.group(1)) if m_region else '',
                     txt(m_place.group(1)) if m_place else '',
                     txt(m_title.group(1)) if m_title else '',
                     txt(m_sdate.group(1)) if m_sdate else '',
                     m_url.group(1) if m_url else ''))
    seen = set(); out = []
    for r in rows:
        if r in seen:
            continue
        seen.add(r); out.append(r)
    return out


targets = {
    '9(JAL名人会10月)': ['2628656'],
    '10(ラ・カージュ)': ['2627408', '2612527'],
    '14(FOUR MINUTES)': ['2629289', '2631965', '2629034'],
    '15(清塚信也)': ['2617505', '2617016', '2617034', '2617037', '2617039', '2617542',
                 '2617040', '2613851', '2617041', '2617042', '2617043', '2617045', '2620427'],
    '31(トスカ)': ['2548147'],
    '13(グレンギャリー)': ['2623908'],
    '19(ロックンロール)': ['2631631'],
}
for label, cds in targets.items():
    print('##### ' + label)
    for cd in cds:
        u = 'https://t.pia.jp/pia/event/event.do?eventCd=' + cd
        try:
            h = fetch(u)
            m = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
            print(' -- %s %s' % (cd, txt(m.group(1)) if m else ''))
            for c in parse_cards(h):
                print('    [%s] %s | %s | %s~%s | %s %s | %s' % (c[2], c[5], c[6], c[0], c[1], c[3], c[4], c[7]))
        except Exception as e:
            print(' -- %s ERROR %s' % (cd, type(e).__name__))
        time.sleep(3)
