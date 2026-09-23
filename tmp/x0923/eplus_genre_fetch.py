# -*- coding: utf-8 -*-
"""新着プールに残る e+ エントリのジャンルを、売り場の申告（/sf/live/<cat> リンク）から取る。
2026-09-23 夜。ユーザー「新着ふりわけOKよ」。

🚨[[feedback_genre_pia_asis_and_other]]＝売り場の言う通りに機械で写す。推測しない。
   このスクリプトは**取ってくるだけ**で、ジャンルの割り当てはしない（対応表は別スクリプト）。
実測（2026-09-23）＝個別ページの本文に出る `/sf/live/<cat>` はその公演のカテゴリを指す。
   モーニング娘。'26→idol／福田こうへい→enka／レキシ→j-pop が一致した。
   🚨1ページに2つ以上出たら「売り場が1つに決めていない」＝そのまま両方記録して、割り当て側で判断する。
使い方: python tmp/x0923/eplus_genre_fetch.py tmp/x0923/eplus_pool_urls.txt tmp/x0923/eplus_genre_raw.json
"""
import collections
import io
import json
import re
import sys
import time
import urllib.request

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/129.0 Safari/537.36'}
RX = re.compile(r'/sf/live/([a-z0-9_-]+)')

src, out_path = sys.argv[1], sys.argv[2]
rows = [l.split('\t') for l in io.open(src, encoding='utf-8').read().splitlines() if '\t' in l]
res = {}
err = 0
cnt = collections.Counter()
for n, (eid, url) in enumerate(rows, 1):
    try:
        html = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)\
            .read().decode('utf-8', 'replace')
    except Exception as e:
        res[eid] = {'url': url, 'error': '%s %s' % (type(e).__name__, getattr(e, 'code', ''))}
        err += 1
        continue
    seen, cats = set(), []
    for m in RX.finditer(html):
        c = m.group(1)
        if c not in seen:
            seen.add(c)
            cats.append(c)
    res[eid] = {'url': url, 'cats': cats}
    cnt[','.join(cats) or '(none)'] += 1
    if n % 25 == 0:
        sys.stdout.write('%d/%d\n' % (n, len(rows)))
        sys.stdout.flush()
    time.sleep(float(sys.argv[3]) if len(sys.argv) > 3 else 0.4)

io.open(out_path, 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
sys.stdout.write('DONE %d rows / err %d -> %s\n' % (len(rows), err, out_path))
for k, v in cnt.most_common():
    sys.stdout.write('  %-24s %4d\n' % (k, v))
