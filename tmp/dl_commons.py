# -*- coding: utf-8 -*-
"""Commons の公式サムネイル（縮小版）を落として img/ に置く。
🚨 自分でトリミング/圧縮すると CC BY-SA の「改変」になり継承義務が生じるので、
   Wikimedia が配信する縮小版をそのまま保存する（サイズ違いは改変とみなさない運用）。
"""
import sys, json, urllib.parse, urllib.request, re, io, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

UA = "OSHINAVI/1.0 (https://oshinavi.jp; sumikiyo12250807@gmail.com)"
WANT = [
    ("File:Tomoyasu Hotei Paaspop 2017.jpg",                    "hotei.jpg",  1000),
    ("File:Chisako Takashima on December 24, 2024 (cropped).jpg","takashima.jpg", 416),
    ("File:Kooza in Sydney39.jpg",                              "kooza39.jpg", 1000),
    ("File:Kooza in Sydney25.jpg",                              "kooza25.jpg", 1000),
]

meta = {}
for title, out, w in WANT:
    url = ("https://commons.wikimedia.org/w/api.php?action=query&titles=%s"
           "&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=%d&format=json"
           % (urllib.parse.quote(title), w))
    d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=40))
    p = list(d['query']['pages'].values())[0]
    ii = p['imageinfo'][0]
    m = ii.get('extmetadata') or {}
    g = lambda k: re.sub(r'<[^>]+>', '', (m.get(k) or {}).get('value') or '').strip()
    thumb = ii.get('thumburl') or ii['url']
    req = urllib.request.Request(thumb, headers={"User-Agent": UA})
    data = urllib.request.urlopen(req, timeout=90).read()
    open(os.path.join('img', out), 'wb').write(data)
    meta[out] = {
        'file': title, 'license': g('LicenseShortName'), 'author': g('Artist'),
        'page': 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(title.replace(' ', '_')),
        'licurl': g('LicenseUrl'), 'bytes': len(data), 'thumb': thumb,
        'desc': g('ImageDescription')[:120], 'date': g('DateTimeOriginal')[:20],
    }
    print('%-14s %6.0fKB  %s / %s' % (out, len(data)/1024, meta[out]['license'], meta[out]['author'][:40]))
    print('               説明:', meta[out]['desc'] or '(なし)')

json.dump(meta, io.open('img/_credits.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n→ img/_credits.json に出典を保存')
