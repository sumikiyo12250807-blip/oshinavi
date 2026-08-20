# -*- coding: utf-8 -*-
"""Commons の画像ファイルのライセンス・作者・帰属要件を取る。
商用利用可か／改変可か／クレジット表記が要るかを機械で判定する。"""
import sys, json, urllib.parse, urllib.request, io
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

FILES = [
    "File:Tomoyasu Hotei Paaspop 2017.jpg",
    "File:Tomoyasu Hotei - 11142013 - 092 (10878026056).jpg",
    "File:Chisako Takashima on December 24, 2024 (cropped).jpg",
    "File:Cirque du Soleil Kooza tent - Portland, Oregon.JPG",
    "File:Kooza in Sydney39.jpg",
    "File:Kooza in Sydney25.jpg",
]

UA = "OSHINAVI/1.0 (https://oshinavi.jp; sumikiyo12250807@gmail.com)"
titles = urllib.parse.quote("|".join(FILES))
url = ("https://commons.wikimedia.org/w/api.php?action=query&titles=%s"
       "&prop=imageinfo&iiprop=url|extmetadata|size&format=json" % titles)
req = urllib.request.Request(url, headers={"User-Agent": UA})
d = json.load(urllib.request.urlopen(req, timeout=40))

out = []
for pid, p in (d.get('query', {}).get('pages') or {}).items():
    ii = (p.get('imageinfo') or [{}])[0]
    m = ii.get('extmetadata') or {}
    def g(k):
        v = (m.get(k) or {}).get('value') or ''
        import re
        return re.sub(r'<[^>]+>', '', v).strip()
    out.append({
        'title': p.get('title'),
        'license': g('LicenseShortName'),
        'restrictions': g('Restrictions'),
        'usage': g('UsageTerms'),
        'author': g('Artist')[:80],
        'credit': g('Credit')[:60],
        'size': '%sx%s' % (ii.get('width'), ii.get('height')),
        'url': ii.get('url'),
    })

for o in sorted(out, key=lambda x: x['title'] or ''):
    print('■', o['title'])
    print('   ライセンス :', o['license'], '／', o['usage'])
    print('   作者       :', o['author'])
    print('   制限       :', o['restrictions'] or '(なし)')
    print('   サイズ     :', o['size'])
    print('   直URL      :', o['url'])
    print()
