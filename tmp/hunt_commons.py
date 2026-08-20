# -*- coding: utf-8 -*-
"""記事に出るアーティストの「使ってよい画像」を Wikimedia Commons から総ざらいする。

🚨判定は2段（[[reference_image_rights_and_sources]]）:
   ① LicenseShortName が CC/PD 系＝著作権はクリア
   ② **Restrictions に personality が無い**＝肖像権の注意タグが立っていない
   両方を満たすものだけ「使える」と出す。

🚨1つの検索語で諦めない（[[feedback_verify_before_saying_impossible]]）。
   グループ名・英語表記・メンバー個人名・関連ワードを最低3ルート当てる。
"""
import sys, json, time, re, io
import urllib.parse, urllib.request

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
UA = "OSHINAVI/1.0 (https://oshinavi.jp; sumikiyo12250807@gmail.com)"

TARGETS = [
    # (記事での呼び名, [検索語を複数ルート])
    ('EXILE',            ['EXILE Japanese band', 'EXILE ATSUSHI', 'EXILE TAKAHIRO', 'Exile TRIBE live']),
    ('真心ブラザーズ',    ['Magokoro Brothers band', 'YO-KING musician', '桜井秀俊', 'Yo-King Japanese singer']),
    ('モーニング娘。',    ['Morning Musume 2023', 'Morning Musume 2024', 'Morning Musume concert', 'Hello! Project 2024']),
    ('凛として時雨',      ['Ling tosite sigure', 'TK from Ling tosite sigure']),
    ('徳永英明',          ['Hideaki Tokunaga']),
    ('ORANGE RANGE',      ['Orange Range band']),
    ('加藤ミリヤ',        ['Miliyah Kato']),
    ('岩崎宏美',          ['Hiromi Iwasaki']),
    ('松平健',            ['Ken Matsudaira']),
    ('coldrain',          ['Coldrain band']),
    ('大原櫻子',          ['Sakurako Ohara']),
    ('プロレスリング・ノア', ['Pro Wrestling Noah', 'Pro Wrestling Noah 2024']),
    ('7ORDER',            ['7 Order band Japan']),
    ('フラワーカンパニーズ', ['Flower Companyz']),
    ('浜崎貴司',          ['Takashi Hamasaki FLYING KIDS', 'Flying Kids band']),
]


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(req, timeout=40))


def strip(v):
    return re.sub(r'<[^>]+>', '', v or '').strip()


BAD_LIC = re.compile(r'(fair use|non-?free|Attribution.*NoDerив|ND\b|NonCommercial|NC\b)', re.I)

results = {}
for name, queries in TARGETS:
    found = []
    seen = set()
    for q in queries:
        try:
            d = api({'action': 'query', 'list': 'search', 'srsearch': q,
                     'srnamespace': 6, 'srlimit': 8, 'format': 'json'})
        except Exception as e:
            print('  検索失敗', q, e)
            continue
        titles = [r['title'] for r in d.get('query', {}).get('search', []) if r['title'] not in seen]
        for t in titles:
            seen.add(t)
        if not titles:
            continue
        # まとめてライセンスを引く
        for i in range(0, len(titles), 5):
            chunk = titles[i:i + 5]
            try:
                dd = api({'action': 'query', 'titles': '|'.join(chunk), 'prop': 'imageinfo',
                          'iiprop': 'url|extmetadata|size', 'format': 'json'})
            except Exception as e:
                print('  情報取得失敗', e)
                continue
            for pid, p in (dd.get('query', {}).get('pages') or {}).items():
                ii = (p.get('imageinfo') or [{}])[0]
                if not ii:
                    continue
                m = ii.get('extmetadata') or {}
                g = lambda k: strip((m.get(k) or {}).get('value'))
                lic, restr = g('LicenseShortName'), g('Restrictions')
                w, hgt = ii.get('width') or 0, ii.get('height') or 0
                ok = bool(lic) and not BAD_LIC.search(lic) and 'personality' not in (restr or '').lower()
                found.append({
                    'title': p.get('title'), 'lic': lic, 'restr': restr or '',
                    'author': g('Artist')[:44], 'date': g('DateTimeOriginal')[:10],
                    'desc': g('ImageDescription')[:70], 'wh': '%dx%d' % (w, hgt),
                    'px': w * hgt, 'ok': ok, 'q': q,
                })
            time.sleep(0.4)
    results[name] = found

out = []
P = out.append
for name, fs in results.items():
    usable = [f for f in fs if f['ok'] and f['px'] > 200 * 200]
    usable.sort(key=lambda f: -f['px'])
    P('■ %s  … 候補%d件 / **使える%d件**' % (name, len(fs), len(usable)))
    for f in usable[:5]:
        P('   ✅ %s' % f['title'])
        P('      %s / %s / %s / 撮影%s' % (f['lic'], f['author'], f['wh'], f['date'] or '不明'))
        P('      説明: %s' % (f['desc'] or '(なし)'))
    ng = [f for f in fs if not f['ok']]
    if ng:
        P('   ✗除外 %d件（%s）' % (len(ng), '／'.join(sorted({(f['restr'] or f['lic'])[:22] for f in ng}))[:90]))
    P('')

io.open('tmp/commons_hunt.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
