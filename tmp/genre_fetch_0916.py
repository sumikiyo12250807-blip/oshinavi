# -*- coding: utf-8 -*-
"""ジャンルを確かめ切れなかった新着について、ぴあのページのジャンル番号（隠し input の genreCd / ntSgenreCd）を引いて
_piaSub の分類名と突き合わせる（読むだけ・2026-09-16）。1ページごとに2秒あける。混雑ページは30秒おいて2回まで取り直す。
使い方: python tmp/genre_fetch_0916.py 9891,9897,...
"""
import io
import json
import re
import sys
import time
import unicodedata
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')
from build_pia_entries import PIA_GENRE_CD  # noqa: E402

ids = [int(x) for x in sys.argv[1].split(',') if x.strip()]
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
GC = re.compile(r'(?:genreCd|ntSgenreCd)["\']?\s*(?:value=|[:=])\s*["\']?(\d{7})')


def n(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or ''))


def get(u):
    for k in range(3):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
        except Exception as ex:  # noqa: BLE001
            h = 'ERR %s' % ex
        if len(h) > 5000 and 'sorry' not in h[:3000].lower():
            return h
        time.sleep(30)
    return ''


ok, bad, none = [], [], []
for i in ids:
    e = by[i]
    u = (e.get('links') or {}).get('pia') or next((t.get('url') for t in e.get('tickets') or [] if 'pia.jp' in (t.get('url') or '')), '')
    h = get(u) if u else ''
    time.sleep(2)
    got = {n(PIA_GENRE_CD.get(c, '?' + c)) for c in GC.findall(h)}
    leaf = n((e.get('_piaSub') or '').split('/')[-1])
    if not got:
        none.append(i)
    elif leaf in got:
        ok.append(i)
    else:
        bad.append((i, e.get('_piaSub'), got))
print('一致 %d / 食い違い %d / 番号が取れない %d' % (len(ok), len(bad), len(none)))
print('一致:', ','.join(str(i) for i in ok))
for i, s, g in bad:
    print('  ✗ id%d 登録「%s」 ページ「%s」' % (i, s, '・'.join(sorted(g))))
print('取れない:', ','.join(str(i) for i in none))
