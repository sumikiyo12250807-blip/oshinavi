# -*- coding: utf-8 -*-
import re, sys, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')
UA = 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'


class NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


op = urllib.request.build_opener(NoRedir)


def get(u):
    try:
        r = op.open(urllib.request.Request(u, headers={'User-Agent': UA}), timeout=60)
        return r.status, r.headers, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.headers, ''


for u in ['https://oshinavi.jp/artist/4234.html', 'https://oshinavi.jp/artist/4234', 'https://oshinavi.jp/ai_316', 'https://oshinavi.jp/ai_316.html']:
    st, hd, h = get(u)
    print('==', u, st, 'Location=', hd.get('Location'))
    if not h:
        continue
    print('  title:', (re.search(r'<title>(.*?)</title>', h, re.S) or [None, None])[1])
    print('  canonical:', re.findall(r'<link[^>]+rel=.canonical.[^>]*>', h))
    print('  robots:', re.findall(r'<meta[^>]+name=.robots.[^>]*>', h))
    body = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S)
    txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body)).strip()
    print('  本文 %d字 / HTML %dKB' % (len(txt), len(h) // 1000))
    print('  本文:', txt[:700])
s = urllib.request.urlopen(urllib.request.Request('https://oshinavi.jp/sitemap.xml', headers={'User-Agent': UA})).read().decode()
locs = re.findall(r'<loc>(.*?)</loc>', s)
print('sitemap 例', [l for l in locs if 'artist/' in l][:2], ' ai_ の数', sum('ai_' in l for l in locs))
