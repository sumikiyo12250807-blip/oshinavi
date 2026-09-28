import sys, json, re, time, os, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/user/oshinavi/'
pick = json.load(open(R + 'tmp/x0928e/sc_pick.json', encoding='utf-8'))
html = open(R + 'index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'\n  const EVENTS = (\[.*?\]);\r?\n', html, re.S).group(1))
byid = {str(e.get('id')): e for e in ev}
built = json.load(open(R + 'tmp/x0928e/built_livepocket.json', encoding='utf-8'))['entries']
sel = []
for p in pick:
    e = byid[p['id']] if p['src'] == 'IDX' else built[int(p['id'][1:])]
    sel.append({'src': p['src'], 'key': p['id'], 'entry': e})
json.dump(sel, open(R + 'tmp/x0928e/sc_sel.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
urls = []
for s in sel:
    e = s['entry']
    for u in [e['links']['livepocket']] + [t.get('url') for t in e.get('tickets', [])]:
        if u and 'livepocket.jp/e/' in u and u not in urls: urls.append(u)
d = R + 'tmp/x0928e/sc_html/'
os.makedirs(d, exist_ok=True)
print(len(urls), 'urls')
for u in urls:
    slug = u.rstrip('/').split('/e/')[1].split('?')[0]
    fn = d + slug + '.html'
    if os.path.exists(fn) and os.path.getsize(fn) > 20000: continue
    for attempt in range(3):
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36', 'Accept-Language': 'ja'})
        try:
            r = urllib.request.urlopen(req, timeout=30); code = r.status; body = r.read().decode('utf-8', 'replace')
        except Exception as ex:
            code = getattr(ex, 'code', 0); body = ''
        time.sleep(3.5)
        if code == 200 and len(body) > 20000:
            open(fn, 'w', encoding='utf-8').write(body); print('OK', slug, len(body)); break
        print('NG', slug, code, len(body)); time.sleep(60)
