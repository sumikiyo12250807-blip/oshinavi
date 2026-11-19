import json, re, time, urllib.request, html, os, hashlib
SP = r'C:\Users\user\AppData\Local\Temp\claude\ac08c5b2b244d5f8\6d0ac969-eb80-4bf7-86e5-551288d024a5\scratchpad\pages2'
os.makedirs(SP, exist_ok=True)
d = json.load(open(r'C:\Users\user\oshinavi\tmp\x1119\spot\sample_2.json', encoding='utf-8'))
urls = []
for e in d:
    for k, v in (e.get('links') or {}).items():
        if v and k != 'amazon' and v not in urls:
            urls.append(v)
    for t in e.get('tickets', []):
        u = t.get('url')
        if u and u not in urls:
            urls.append(u)
idx = []
for i, u in enumerate(urls):
    fn = '%02d' % i
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            st = r.status
            final = r.geturl()
            raw = r.read()
        cs = 'utf-8'
        m = re.search(rb'charset=["\']?([\w-]+)', raw[:3000])
        if m:
            cs = m.group(1).decode()
        txt = raw.decode(cs, errors='replace')
    except Exception as ex:
        st = getattr(ex, 'code', None) or str(ex)
        final = ''
        txt = ''
    open(os.path.join(SP, fn + '.html'), 'w', encoding='utf-8').write(txt)
    t2 = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', txt)
    t2 = re.sub(r'(?s)<br\s*/?>', '\n', t2)
    t2 = re.sub(r'(?s)<[^>]+>', '\n', t2)
    t2 = html.unescape(t2)
    t2 = '\n'.join(l.strip() for l in t2.splitlines() if l.strip())
    open(os.path.join(SP, fn + '.txt'), 'w', encoding='utf-8').write(t2)
    idx.append('%s\t%s\t%s\t%s\t%d' % (fn, st, u, final, len(t2)))
    time.sleep(1.2)
open(os.path.join(SP, 'index.txt'), 'w', encoding='utf-8').write('\n'.join(idx))
