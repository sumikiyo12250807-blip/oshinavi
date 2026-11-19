import json, sys, time, re, os, hashlib, urllib.request, html
sys.stdout.reconfigure(encoding='utf-8')
OUT = r'C:\Users\user\AppData\Local\Temp\claude\ac08c5b2b244d5f8\6d0ac969-eb80-4bf7-86e5-551288d024a5\scratchpad\spot1'
os.makedirs(OUT, exist_ok=True)
d = json.load(open(r'C:\Users\user\oshinavi\tmp\x1119\spot\sample_1.json', encoding='utf-8'))
urls = []
for e in d:
    for k, v in (e.get('links') or {}).items():
        if v and k != 'amazon' and v not in urls:
            urls.append(v)
    for t in e.get('tickets', []):
        u = t.get('url')
        if u and u not in urls:
            urls.append(u)
idx = {}
for u in urls:
    name = hashlib.md5(u.encode()).hexdigest()[:10]
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            b = r.read(); code = r.status; final = r.geturl()
    except urllib.error.HTTPError as ex:
        b = ex.read(); code = ex.code; final = u
    except Exception as ex:
        b = b''; code = str(ex); final = u
    raw = None
    for enc in ('utf-8', 'cp932', 'euc-jp'):
        try:
            raw = b.decode(enc); break
        except Exception:
            pass
    if raw is None:
        raw = b.decode('utf-8', 'replace')
    open(os.path.join(OUT, name + '.html'), 'w', encoding='utf-8').write(raw)
    t = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', raw)
    t = re.sub(r'(?s)<[^>]+>', '\n', t)
    t = html.unescape(t)
    t = '\n'.join(x.strip() for x in t.splitlines() if x.strip())
    open(os.path.join(OUT, name + '.txt'), 'w', encoding='utf-8').write(t)
    idx[u] = {'file': name, 'code': code, 'final': final, 'len': len(b)}
    print(code, len(b), name, u, final if final != u else '')
    time.sleep(1.2)
json.dump(idx, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
