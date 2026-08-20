# -*- coding: utf-8 -*-
"""_piaSub が空の新着エントリについて、ぴあの実カテゴリを取り直す。
bundleページはカテゴリを出さないので、中の個別 eventCd ページを1つ引いて読む。
走査と重なるので間隔を長め（既定6秒）に取る。"""
import re
import sys
import time

sys.path.insert(0, 'tools')
sys.path.insert(0, '.')
from check_expired import extract_events_array
import build_pia_entries as B

IDS = [4130, 4142, 4144, 4152, 4159, 4163, 4167]
SLEEP = 6.0

byid = {e['id']: e for e in extract_events_array('index.html')}

for i in IDS:
    e = byid.get(i)
    if not e:
        print('%-5s 見つからない' % i)
        continue
    url = (e.get('links') or {}).get('pia')
    name = e.get('name') or ''
    sub = None
    tried = []
    try:
        h = B.fetch(url)
        tried.append(url)
        sub = B.pia_subcat(h)
        if not sub:
            # bundle の中から個別公演ページを1つ拾う
            m = re.findall(r'event\.do\?eventCd=(\d+)', h)
            if m:
                u2 = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % m[0]
                time.sleep(SLEEP)
                h2 = B.fetch(u2)
                tried.append(u2)
                sub = B.pia_subcat(h2)
    except Exception as ex:
        print('%-5s %-26s ERR %s' % (i, name[:26], str(ex)[:60]))
        time.sleep(SLEEP)
        continue

    if sub:
        g = B.genre_from_subcat(sub[0], sub[1], name)
        print('%-5s %-26s ぴあ=[%s %s] → %s  (下書き %s)'
              % (i, name[:26], sub[0], sub[1], g, e.get('_genre')))
    else:
        print('%-5s %-26s ぴあカテゴリ取得できず (下書き %s / 試したURL %d本)'
              % (i, name[:26], e.get('_genre'), len(tried)))
    time.sleep(SLEEP)
