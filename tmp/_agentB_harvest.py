# -*- coding: utf-8 -*-
import io, os, re, sys, time
import urllib.request

SRC = 'C:/Users/user/oshinavi/tmp/_eplus35_0831.txt'
CACHE = 'C:/Users/user/oshinavi/tmp/_agentB_cache'
OUT = 'C:/Users/user/oshinavi/tmp/_agentB_extract.txt'

os.makedirs(CACHE, exist_ok=True)

rows = []
for line in io.open(SRC, encoding='utf-8'):
    line = line.strip()
    if not line:
        continue
    p = [x.strip() for x in line.split('|')]
    if len(p) < 5:
        continue
    rows.append(p)

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'


def fetch(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        return open(path, 'rb').read()
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ja'})
    try:
        b = urllib.request.urlopen(req, timeout=40).read()
    except Exception as e:
        return b'ERROR:' + str(e).encode('utf-8', 'replace')
    open(path, 'wb').write(b)
    time.sleep(1.2)
    return b


def strip(x):
    x = re.sub(r'(?s)<br\s*/?>', ' / ', x)
    x = re.sub(r'(?s)<[^>]+>', '', x)
    x = re.sub(r'&amp;', '&', x)
    x = re.sub(r'&nbsp;', ' ', x)
    return re.sub(r'\s+', ' ', x).strip()


out = io.open(OUT, 'w', encoding='utf-8')
for r in rows:
    rid, name, date, pref, url = r[0], r[1], r[2], r[3], r[4]
    path = os.path.join(CACHE, rid + '.html')
    b = fetch(url, path)
    s = b.decode('utf-8', 'replace')
    out.write('=== id %s | 登録名: %s | %s | %s\n' % (rid, name, date, pref))
    if s.startswith('ERROR:'):
        out.write('  FETCH FAILED: %s\n\n' % s[:200])
        continue
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    out.write('  TITLE: %s\n' % (strip(t.group(1)) if t else '?'))
    # breadcrumb names
    bc = re.findall(r'class="breadcrumb-list__name"[^>]*>(.*?)</span>', s, re.S)
    bc = [strip(x) for x in bc]
    out.write('  BREADCRUMB: %s\n' % ' > '.join(bc[:8]))
    # related genre section
    m = re.search(r'チケットの関連ジャンル(.*?)</section>', s, re.S)
    if m:
        g = re.findall(r'class="breadcrumb-list__name"[^>]*>(.*?)</span>', m.group(1), re.S)
        out.write('  RELGENRE: %s\n' % ' > '.join(strip(x) for x in g))
    # performers / description dl blocks
    for dt, dd in re.findall(r'<dt>(.*?)</dt>\s*<dd>(.*?)</dd>', s, re.S):
        k = strip(dt)
        v = strip(dd)
        if v:
            out.write('  %s: %s\n' % (k, v[:600]))
    # favorite words (artist names registered on the ticket)
    fw = re.findall(r'class="favorite-word[^"]*"[^>]*>(.*?)</', s, re.S)
    if fw:
        out.write('  FAVWORD: %s\n' % ' | '.join(strip(x) for x in fw[:20]))
    # any /sf/word/ links with labels
    wl = re.findall(r'href="/sf/word/\d+"[^>]*>(.*?)</a>', s, re.S)
    if wl:
        out.write('  WORDLINKS: %s\n' % ' | '.join(sorted(set(strip(x) for x in wl))[:20]))
    # venue
    ven = re.findall(r'class="ticket-item__venue[^"]*"[^>]*>(.*?)</', s, re.S)
    if ven:
        out.write('  VENUE: %s\n' % ' | '.join(sorted(set(strip(x) for x in ven))[:8]))
    out.write('\n')
out.close()
print('OK rows=%d' % len(rows))
