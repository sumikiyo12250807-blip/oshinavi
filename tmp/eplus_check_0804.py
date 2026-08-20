# -*- coding: utf-8 -*-
"""削除候補の他社チャネル確認: e+ 検索(/sf/search?keyword=)を複数キーワードで引いて
公演の有無と受付状態をUTF-8ファイルに出す。コンソールに日本語を出さない。
memory: feedback_delete_nonpia_blindspot / reference_eplus_keyword_search
"""
import io
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KWS = [
    ('1404', 'ETERNAL FIGHTER'),
    ('1774', '怪奇骨董'),
    ('2038', 'ハチエモン'),
    ('2663', '音の会'),
    ('2845', 'トビダスクール'),
    ('3485', '眞名子新'),
]


def fetch(kw):
    u = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')


def parse(h):
    objs, seen = [], set()
    for m in re.finditer(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h):
        blk = h[max(0, m.start() - 4000):min(len(h), m.end() + 4000)]

        def g(key):
            mm = re.search(r'"%s":"([^"]*)"' % key, blk)
            return mm.group(1).replace('\xa0', ' ') if mm else ''
        url = 'https://eplus.jp' + m.group(1)
        if url in seen:
            continue
        seen.add(url)
        objs.append({
            'url': url,
            'sub': g('kogyo_name_1') + ' ' + g('kogyo_name_2'),
            'koenbi': g('koenbi') or g('koen_start_datetime'),
            'venue': g('kaijo_name') or g('venue_name'),
            'status': g('uketsuke_name_pc'),
            'uke_end': g('uketsuke_end_datetime'),
        })
    objs.sort(key=lambda x: x['koenbi'])
    return objs


out = []
for eid, kw in KWS:
    out.append('=' * 70)
    out.append('id=%s  keyword=%s' % (eid, kw))
    try:
        rows = parse(fetch(kw))
    except Exception as ex:
        out.append('  FETCH ERROR %s %s' % (type(ex).__name__, str(ex)[:120]))
        time.sleep(3)
        continue
    if not rows:
        out.append('  e+ヒット0件')
    for o in rows:
        out.append('  %s | %s | %s | %s | 受付〜%s | %s'
                   % (o['koenbi'][:10], o['sub'][:40], o['venue'][:20],
                      o['status'][:14], o['uke_end'][:14], o['url']))
    time.sleep(3)

p = os.path.join(ROOT, 'tmp', 'eplus_check_0804.txt')
io.open(p, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/eplus_check_0804.txt lines=%d' % len(out))
