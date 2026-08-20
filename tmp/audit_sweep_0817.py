# -*- coding: utf-8 -*-
"""受付中スイープが「在庫のどこまで」を見ているか確認する。
ぴあの一覧は名前順なので、途中で打ち切られていれば拾えるのは頭文字の若い所だけになる。"""
import io, re, sys, json, glob, os
sys.stdout.reconfigure(encoding='utf-8')

for f in sorted(glob.glob('tmp/open_*_0817.json')) + sorted(glob.glob('tmp/presale_*03_0817.json')):
    d = json.load(io.open(f, encoding='utf-8'))
    new = d.get('new', [])
    print('%-30s total=%-5d parsed=%-5d new=%-4d  カバー率 %.1f%%'
          % (os.path.basename(f), d.get('total', 0), d.get('parsed', 0), len(new),
             100.0 * d.get('parsed', 0) / d['total'] if d.get('total') else 0))
    if new:
        print('    最初の3件:', ' / '.join(x['artist'][:18] for x in new[:3]))
        print('    最後の3件:', ' / '.join(x['artist'][:18] for x in new[-3:]))
