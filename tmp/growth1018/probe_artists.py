# -*- coding: utf-8 -*-
import re, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'


def get(url):
    t = time.time()
    r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60)
    b = r.read()
    return r.status, b.decode('utf-8', 'replace'), len(b), time.time() - t


st, h, n, sec = get('https://oshinavi.jp/')
print('トップ内 artists.html へのリンク:', re.findall(r'<a[^>]+href="[^"]*artists[^"]*"[^>]*>[^<]{0,30}', h)[:5])
st, h, n, sec = get('https://oshinavi.jp/artists.html')
links = re.findall(r'href="([^"]*artist/[^"]+)"', h)
print('artists.html', st, '%.2fMB' % (n / 1e6), '%.1fs' % sec, 'artist/へのリンク', len(links), links[:3])
if links:
    u = links[0] if links[0].startswith('http') else 'https://oshinavi.jp/' + links[0].lstrip('/')
    st, h2, n2, sec2 = get(u)
    print('例', u, st, '%.0fKB' % (n2 / 1e3), '%.1fs' % sec2)
    print('  title:', re.search(r'<title>(.*?)</title>', h2, re.S).group(1)[:80])
    print('  canonical:', re.findall(r'<link[^>]+rel="canonical"[^>]*>', h2)[:1], ' robots:', re.findall(r'<meta[^>]+name="robots"[^>]*>', h2)[:1])
    print('  Event JSON-LD:', h2.count('"@type": "Event"') + h2.count('"@type":"Event"'))
st, h, n, sec = get('https://oshinavi.jp/sitemap.xml')
print('sitemap', st, 'URL数', h.count('<loc>'), '%.1fMB' % (n / 1e6))
