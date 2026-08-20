# -*- coding: utf-8 -*-
"""楽天の生HTMLから販売枠の一次情報だけ抜いてUTF-8ファイルに出す。
（WebFetchは販売中を「販売終了」と誤読するので使わない＝reference_rakuten_harvest）
確認したいのは「同じ締切の枠が3つ並ぶ」のが実態なのか、パーサの埋めなのか。"""
import json
import re
import sys
import urllib.request

URLS = [
    ('岐阜', 'https://ticket.rakuten.co.jp/event/rtntutg/'),
    ('兵庫', 'https://ticket.rakuten.co.jp/event/rtntuth/'),
    ('仙台', 'https://ticket.rakuten.co.jp/event/rtntuti/'),
    ('千葉柏', 'https://ticket.rakuten.co.jp/event/rtntuts/'),
]
HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept-Language': 'ja'}

out = []
for tag, u in URLS:
    out.append(f'=== {tag}  {u} ===')
    try:
        req = urllib.request.Request(u, headers=HDR)
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    except Exception as e:
        out.append(f'  取得失敗 {e}')
        continue
    m = re.search(r'var\s+salesDisplayStatus\s*=\s*(\{.*?\}|false)\s*;', h, re.S)
    if m:
        raw = m.group(1)
        out.append('  salesDisplayStatus:')
        if raw == 'false':
            out.append('    false（枠1つのページ）')
        else:
            try:
                d = json.loads(raw)
                out.append('    ' + json.dumps(d, ensure_ascii=False, indent=2).replace('\n', '\n    '))
            except Exception as e:
                out.append(f'    JSON解析失敗 {e}: {raw[:600]}')
    else:
        out.append('  salesDisplayStatus 見つからない')
    for dd in re.findall(r"data-date='([^']*)'", h)[:6]:
        out.append(f'  data-date: {dd[:400]}')
    for blk in re.findall(r'販売期間[：:][^<]{0,200}', h)[:8]:
        out.append(f'  本文販売期間: {blk.strip()}')
    out.append('')

open('tmp/peek_rakuten_raw_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/peek_rakuten_raw_0730.txt')
