# -*- coding: utf-8 -*-
"""指定した楽天チケットのURLだけを rakuten_harvest のパーサで読み直して、
build_rakuten_entries が食える形（perfs が配列の形）にする。

なぜ要るか＝rakuten_presale_harvest.py の出力は perfs が「件数(int)」なので
build_rakuten_entries.py に渡すと TypeError になる（2026-09-13 に踏んだ）。

使い方: python tmp/rakuten_fetch_urls_0913.py <入力json(urlを持つ配列)> <出力json>
"""
import io
import json
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R  # noqa: E402

src = json.load(io.open(sys.argv[1], encoding='utf-8'))
out = []
for i, r in enumerate(src, 1):
    u = r.get('url')
    try:
        body = R.fetch(u)
        rec = R.parse_page(u, body)
    except Exception as e:
        print('  %d/%d ❌ 読めなかった %s … %s' % (i, len(src), u, str(e)[:60]))
        continue
    if not rec:
        print('  %d/%d ⏭ 解析できない形式 %s' % (i, len(src), u))
        continue
    out.append(rec)
    print('  %d/%d ✅ %-34s 公演%d件 / 枠%d本' % (
        i, len(src), (rec.get('name') or '')[:34], len(rec.get('perfs') or []), len(rec.get('windows') or [])))
    time.sleep(1.5)

json.dump(out, io.open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('読めた %d/%d 件 → %s' % (len(out), len(src), sys.argv[2]))
