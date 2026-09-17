import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
html = open('index.html', encoding='utf-8').read()
data = json.load(open('tmp/rakuten_presale.json', encoding='utf-8'))
items = data if isinstance(data, list) else data.get('presale') or data.get('items') or data
if isinstance(items, dict):
    print('keys:', list(items.keys())[:20]); sys.exit()
for it in items:
    st = it.get('status') or it.get('state') or it.get('kind')
    if st not in (None, 'presale', '発売前', 'before'):
        continue
    url = it.get('url', '')
    m = re.search(r'/(rt[0-9a-z]+)/?', url)
    code = m.group(1) if m else url
    reg = code.lower() in html.lower()
    print(('登録済' if reg else '★未登録'), code, it.get('title') or it.get('name'), it.get('saleStart') or it.get('start') or '')
