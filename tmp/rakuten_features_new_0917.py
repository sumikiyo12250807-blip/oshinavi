import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
html = open('index.html', encoding='utf-8').read().lower()
feat = json.load(open('tmp/rakuten_features.json', encoding='utf-8'))
harv = json.load(open('tmp/rakuten_presale.json', encoding='utf-8'))
seen = set()
for k, v in harv.items():
    for it in v:
        u = it.get('url') if isinstance(it, dict) else it
        m = re.search(r'/(rt[0-9a-z]+)/?', u or '')
        if m: seen.add(m.group(1).lower())
codes = {}
for p in feat['pages']:
    for u in p['events']:
        m = re.search(r'/(rt[0-9a-z]+)/?', u)
        if m: codes.setdefault(m.group(1).lower(), u)
only = {c: u for c, u in codes.items() if c not in seen}
unreg = {c: u for c, u in only.items() if c not in html}
print(f'特設から辿れる公演 {len(codes)} / 投稿サイトマップに無い {len(only)} / そのうち未登録 {len(unreg)}')
open('tmp/rakuten_features_unreg_0917.txt', 'w', encoding='utf-8').write('\n'.join(unreg.values()))
