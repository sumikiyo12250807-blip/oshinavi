# -*- coding: utf-8 -*-
"""本番トップを Googlebot と同じ名乗りで取り、Google に何が見えるかを調べる（読むだけ）。"""
import re, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'


def get(url):
    t = time.time()
    r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Encoding': 'identity'}), timeout=60)
    b = r.read()
    return r.status, b, time.time() - t, dict(r.headers)


st, b, sec, hd = get('https://oshinavi.jp/')
h = b.decode('utf-8', 'replace')
print('TOP', st, '%.2fMB' % (len(b) / 1e6), '%.1fs' % sec, hd.get('Content-Type'), 'x-robots=', hd.get('X-Robots-Tag'))
print('title:', re.search(r'<title>(.*?)</title>', h, re.S).group(1)[:80] if '<title>' in h else None)
print('robots meta:', re.findall(r'<meta[^>]+name="robots"[^>]*>', h)[:3])
print('canonical:', re.findall(r'<link[^>]+rel="canonical"[^>]*>', h)[:2])
scripts = re.findall(r'<script[^>]+src="([^"]+)"', h)
print('外部script', len(scripts))
for s in scripts:
    u = s if s.startswith('http') else 'https://oshinavi.jp/' + s.lstrip('/')
    try:
        s2, b2, sec2, _ = get(u)
        print('   ', s2, '%.2fMB' % (len(b2) / 1e6), '%.1fs' % sec2, s)
    except Exception as ex:
        print('    ERR', s, ex)
# JS なしで見える文字（script/style を除く）
body = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body))
print('JSなしの本文 %d字' % len(txt))
print('  先頭:', txt[:300])
links = re.findall(r'href="([^"]+)"', body)
print('JSなしのリンク', len(links), '（artist/ へ', sum('artist' in l for l in links), '）')
print('インラインscript 合計 %.2fMB' % (sum(len(x) for x in re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', h, re.S)) / 1e6))
st, b, sec, _ = get('https://oshinavi.jp/robots.txt')
print('robots.txt', st, b.decode('utf-8', 'replace')[:400])
