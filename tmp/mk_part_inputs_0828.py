# -*- coding: utf-8 -*-
"""部分一致20件の仕分け結果から、①統合用のbuild入力 ②新規用のbuild入力 を作る。
統合＝既存の名前がぴあ公演名の頭に来るもの＋「PARCO PRODUCE 2026 髪結いの亭主」（同一公演）。
新規＝別主体（新日本フィル/NHK交響楽団/都民音楽フェスの各楽団/THE MATSURI SESSION）。
　　　🚨オーケストラは既存実装が「1公演＝1エントリ」なので、そこに揃える。"""
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
FORCE_MERGE_URL = {'https://ticket.pia.jp/pia/event.do?eventBundleCd=b2670167'}  # PARCO 髪結いの亭主
d = json.load(io.open('tmp/part_reclass_0828.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}
nextid = max(EV) + 1

def pn(u):
    return u.replace('http://', 'https://').replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')

merge = {}
for x in d['same']:
    merge.setdefault(x['eid'], []).append(x['it'])
newr = []
for x in d['diff']:
    if x['it']['url'] in FORCE_MERGE_URL:
        merge.setdefault(x['eid'], []).append(x['it'])
    else:
        newr.append(x['it'])

mi = []
for eid, items in merge.items():
    e = EV[eid]
    urls = []
    p = (e.get('links') or {}).get('pia')
    if p:
        urls.append(pn(p))
    for t in (e.get('tickets') or []):
        if t.get('url'):
            u = pn(t['url'])
            if u not in urls:
                urls.append(u)
    for it in items:
        u = pn(it['url'])
        if u not in urls:
            urls.append(u)
    mi.append({'newid': eid, 'artist': e.get('artist', ''), 'urls': urls})
io.open('tmp/merge_in_part_0828.json', 'w', encoding='utf-8').write(json.dumps(mi, ensure_ascii=False, indent=1))

bi = []
for it in newr:
    bi.append({'newid': nextid, 'artist': it['artist'], 'urls': [pn(it['url'])]})
    nextid += 1
io.open('tmp/build_in_part_0828.json', 'w', encoding='utf-8').write(json.dumps(bi, ensure_ascii=False, indent=1))
print('統合 %d エントリ / 新規 %d エントリ（id %s〜）' % (len(mi), len(bi), bi[0]['newid'] if bi else '-'))
for b in bi:
    print('   新規 id%-5s %s' % (b['newid'], b['artist'][:50]))
