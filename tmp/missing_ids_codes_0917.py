import io, json, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
txt = io.open(sys.argv[1], encoding='utf-8').read()
ids = [int(x) for x in re.findall(r'^🚨 id=(\d+)', txt, re.M)]
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', io.open('index.html', encoding='utf-8').read(), re.S).group(1))}
codes = []
for i in ids:
    u = (ev[i].get('links') or {}).get('pia') or ''
    m = re.search(r'(eventCd=(\d+)|eventBundleCd=(b\d+))', u)
    codes.append((m.group(2) or m.group(3)) if m else '')
print(','.join(map(str, ids)))
print(' '.join(c for c in codes if c))
