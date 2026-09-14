# -*- coding: utf-8 -*-
"""3019 山本達彦＝会場の公演（9/12・9/13 昼夜）は終わった。残るのは e+ の配信（Streaming+）の視聴券。
配信のページは公演ごとに分かれている（4530950001＝9/13 夜公演・〜9/19 20:00 は確認済み）。
同じアーティストの全公演ページを e+ の公開API（eplus_harvest.sibling_show_urls）で出し、
各ページの題・配信かどうか（Streaming+ の文字）・受付期間の窓と状態を並べる（読むだけ・1ページずつ1秒あける）。
使い方: python tmp/eplus_3019_siblings_0914.py
出力: tmp/eplus_3019_siblings_0914.txt
"""
import io
import re
import sys
import time

sys.path.insert(0, 'tools')
import eplus_harvest as eh

sys.stdout.reconfigure(encoding='utf-8')
BASE = 'https://eplus.jp/sf/detail/4530950001-P0030001P021001'
rows = []
h = eh.fetch(BASE)
urls = eh.sibling_show_urls(h, '山本達彦', eh.fetch)
if BASE not in urls:
    urls.insert(0, BASE)
rows.append('同じアーティストの公演ページ %d' % len(urls))
for u in urls:
    time.sleep(1.0)
    try:
        hh = eh.fetch(u)
    except Exception as ex:
        rows.append('=== %s\n  読めない: %s' % (u, ex))
        continue
    t = re.search(r'<title>(.*?)</title>', hh, re.S)
    stream = ('Streaming+' in hh) or ('ストリーミング' in hh)
    rows.append('=== %s\n  題: %s\n  配信の文字: %s' % (u, eh._flat(t.group(1))[:100] if t else '-', 'あり' if stream else 'なし'))
    secs = [s for s in re.split(r'(?=<section class="block-ticket">)', hh) if s.startswith('<section class="block-ticket">')]
    for sec in secs:
        body = sec.split('</section>', 1)[0]
        span = re.search(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', body)
        hm = re.search(r'block-ticket__header[^>]*>(.*?)</header>', body, re.S)
        rows.append('  窓: %s ｜状態: %s' % (eh._flat(hm.group(1) if hm else '')[:140], span.group(1).strip() if span else '-'))
io.open('tmp/eplus_3019_siblings_0914.txt', 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
print('\n'.join(rows))
