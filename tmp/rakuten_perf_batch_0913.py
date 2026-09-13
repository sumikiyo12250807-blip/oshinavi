# -*- coding: utf-8 -*-
"""生HTMLに販売枠が出ない楽天ページを、購入ボタンのAJAX（rakuten_perf_status）で読み直す。

なぜ＝楽天の売り状態は生HTMLに1文字も無く、AJAXにしかない（memory reference_rakuten_harvest）。
build_rakuten_entries は生HTMLの販売枠を見るので、この形のページは「販売枠なし」で落ちる。

使い方: python tmp/rakuten_perf_batch_0913.py <入力json(urlとnameを持つ配列)> <出力json>
"""
import io
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

src = json.load(io.open(sys.argv[1], encoding='utf-8'))
out = []
for i, r in enumerate(src, 1):
    u = r.get('url')
    tmpf = 'tmp/rk_perf_%d.json' % i
    p = subprocess.run([sys.executable, 'tools/rakuten_perf_status.py', u, '--json', tmpf],
                       capture_output=True)
    try:
        d = json.load(io.open(tmpf, encoding='utf-8'))
    except Exception as e:
        print('%d/%d ❌ %s … %s' % (i, len(src), (r.get('name') or '')[:30], str(e)[:50]))
        continue
    rows = d.get('rows') or []
    buy = [x for x in rows if x.get('status') == 'buyable']
    d['_name'] = r.get('name')
    out.append(d)
    print('%d/%d %-34s 公演%d件 / 買える%d件' % (i, len(src), (r.get('name') or '')[:34], len(rows), len(buy)))
    for x in buy[:6]:
        print('      %s %s %s %s ｜締切 %s' % (x.get('date'), x.get('time') or '', x.get('pref'), x.get('venue'), x.get('sale_end')))
    time.sleep(1.5)

json.dump(out, io.open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ %s' % sys.argv[2])
