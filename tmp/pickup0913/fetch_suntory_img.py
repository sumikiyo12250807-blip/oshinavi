# -*- coding: utf-8 -*-
"""9/13号の深掘り（サントリーホールの年末年始）の写真を Wikimedia Commons から落とす。
ユーザー採用＝候補1「File:Suntory_Hall_2018.jpg」（2026-09-12 昼「1枚目でいいよ」）。
🚨加工しない＝Wikimedia が配信する公式の縮小版（iiurlwidth=1280）をそのまま保存する（CC BY-SA は改変すると同ライセンス義務）。
🚨Restrictions に personality があれば落とさずに止める（memory reference_image_rights_and_sources）。
ライセンス・撮影者・ページ・ライセンス本文URLは tmp/pickup0913/suntory_meta.json に残す（img/_credits.json に写す元）。
使い方: python tmp/pickup0913/fetch_suntory_img.py
"""
import io
import json
import re
import sys
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
FILE = 'File:Suntory_Hall_2018.jpg'
OUT = 'img/suntory_hall.jpg'
META = 'tmp/pickup0913/suntory_meta.json'
UA = {'User-Agent': 'OSHINAVI/1.0 (https://oshinavi.jp; image credit check)'}

q = urllib.parse.urlencode({'action': 'query', 'titles': FILE, 'prop': 'imageinfo',
                            'iiprop': 'url|size|extmetadata', 'iiurlwidth': 1280, 'format': 'json'})
d = json.load(urllib.request.urlopen(
    urllib.request.Request('https://commons.wikimedia.org/w/api.php?' + q, headers=UA), timeout=60))
page = next(iter(d['query']['pages'].values()))
ii = page['imageinfo'][0]
md = {k: (v.get('value') if isinstance(v, dict) else v) for k, v in ii['extmetadata'].items()}


def plain(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


meta = {
    'file': FILE,
    'license': md.get('LicenseShortName'),
    'licurl': md.get('LicenseUrl'),
    'author': plain(md.get('Artist')),
    'author_html': md.get('Artist'),
    'restrictions': md.get('Restrictions') or '',
    'date': md.get('DateTimeOriginal'),
    'desc': plain(md.get('ImageDescription')),
    'credit': plain(md.get('Credit')),
    'page': ii.get('descriptionurl'),
    'orig_size': [ii.get('width'), ii.get('height')],
    'thumb': ii.get('thumburl'),
    'thumb_size': [ii.get('thumbwidth'), ii.get('thumbheight')],
}
io.open(META, 'w', encoding='utf-8').write(json.dumps(meta, ensure_ascii=False, indent=1))
for k in ('license', 'licurl', 'author', 'restrictions', 'date', 'desc', 'credit', 'page', 'orig_size', 'thumb_size'):
    print('%-12s %s' % (k, meta[k]))
if 'personality' in meta['restrictions'].lower():
    print('🚨 Restrictions に personality ＝ 使わない。落とさずに止める')
    sys.exit(3)
if not re.match(r'^(CC BY(-SA)? [\d.]+|Public domain|CC0)', meta['license'] or ''):
    print('🚨 ライセンスが想定外 ＝ 落とさずに止める')
    sys.exit(4)
b = urllib.request.urlopen(urllib.request.Request(meta['thumb'], headers=UA), timeout=60).read()
io.open(OUT, 'wb').write(b)
print('保存 %s (%d bytes・加工なし＝Wikimedia配信の縮小版そのまま)' % (OUT, len(b)))
