import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
root = 'C:/Users/user/oshinavi/'
html = open(root + 'index.html', encoding='utf-8').read()
m = re.search(r'\n  const EVENTS = (\[.*?\]);\r?\n', html, re.S)
ev = json.loads(m.group(1))
lp = [e for e in ev if (e.get('links') or {}).get('livepocket')]
built = json.load(open(root + 'tmp/x0928e/built_livepocket.json', encoding='utf-8'))['entries']
out = open(root + 'tmp/x0928e/sc_list.txt', 'w', encoding='utf-8')
def row(src, e):
    urls = sorted({t.get('url') for t in e.get('tickets', []) if t.get('url')})
    st = []
    for t in e.get('tickets', []):
        f = ''
        if t.get('startDate'): f += 'S'
        if t.get('soldout'): f += 'X'
        if t.get('saleEnded'): f += 'E'
        st.append(f or '-')
    out.write(f"{src}\t{e.get('id','')}\t{e['links']['livepocket']}\t{e.get('date')}\t{e.get('dateLabel')}\t{e.get('venue')}\t{e.get('prefecture')}\tn={len(e.get('tickets',[]))}\turls={len(urls)}\t{''.join(x[0] for x in st)}\t{e.get('artist')}|{e.get('name')}\n")
for e in lp: row('IDX', e)
for i, e in enumerate(built): e.setdefault('id', f'b{i}'); row('BLT', e)
print(len(lp), len(built))
