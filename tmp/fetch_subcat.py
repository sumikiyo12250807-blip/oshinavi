# -*- coding: utf-8 -*-
import sys, re, json, time
sys.path.insert(0, 'tools')
import build_pia_entries as bpe

IDS = [1549,1552,1560,1566,1572,1581,1597,1598,1600,1622]
ev = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', open('index.html',encoding='utf-8').read(), re.S).group(1))
byid = {e['id']: e for e in ev}
out = {}
for i in IDS:
    e = byid[i]
    urls = [e['links']['pia']] + [t.get('url') for t in e['tickets'] if t.get('url')]
    found = None
    for u in urls:
        try:
            h = bpe.fetch(u)
        except Exception:
            continue
        sc = bpe.pia_subcat(h)
        if sc:
            found = sc; break
        # bundleなら個別eventCdカードを1つ引く
        for r in bpe.parse_cards(h):
            eu = bpe.ecd_url(r.get('url'))
            if eu:
                try:
                    sc2 = bpe.pia_subcat(bpe.fetch(eu)); time.sleep(0.2)
                except Exception:
                    sc2 = None
                if sc2: found = sc2; break
        if found: break
        time.sleep(0.2)
    g = bpe.genre_from_subcat(*found, e['artist']) if found else None
    out[i] = {'artist': e['artist'][:30], 'subcat': found, 'genre_guess': g}
    print(i, e['artist'][:24], '|', found, '->', g)
json.dump(out, open('tmp/subcat_0630.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
