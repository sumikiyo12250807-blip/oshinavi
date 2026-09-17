import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
html = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'const EVENTS\s*=\s*(\[[\s\S]*?\]);', html).group(1))
rng = [(10763, 10855), (10903, 10904), (11048, 11048)]
rows = []
for e in EV:
    if any(a <= e['id'] <= b for a, b in rng) and e.get('genre') == 'new':
        urls = sorted({t.get('url') for t in e.get('tickets', []) if t.get('url')} | ({e['links']['pia']} if (e.get('links') or {}).get('pia') else set()))
        rows.append((e['id'], e.get('artist', ''), e.get('_genre', ''), len(e.get('tickets', [])), urls))
print(len(rows))
with open('tmp/recheck_list_0917.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t枠{r[3]}\t{' '.join(r[4])}\n")
print(','.join(str(r[0]) for r in rows))
