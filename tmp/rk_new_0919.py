# 楽天の集め（tmp/rakuten_presale.json）のうち「まだ載っていない」ページを出す（rtコードで index.html を引く）
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('tmp/rakuten_presale.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
out = {}
for k in ('presale', 'onsale', 'soldout'):
    miss = []
    for x in d[k]:
        code = re.search(r'/(rt[0-9a-z]+)/?$', x['url'])
        code = code.group(1) if code else x['url']
        if code not in h:
            miss.append(x)
    out[k] = miss
    print(f'== {k}: {len(d[k])}件中 未登録 {len(miss)}件')
    for x in miss:
        print('  ', x['first'], x['name'][:50], x['url'])
json.dump(out, open('tmp/rk_missing_0919.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
