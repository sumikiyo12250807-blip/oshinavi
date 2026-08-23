# -*- coding: utf-8 -*-
"""記事セクションの見た目を確認するための「プレビュー用の複製」を作る（恒久ツール・2026-08-23 新設）。

🚨なぜ要るか:
  ユーザーは常にローカルの file://index.html を開いて見ている（feedback_user_checks_local_file）。
  そこであたしが確認のために index.html の hidden を外す→撮る→戻す をやったら、
  ユーザーがちょうど更新をかけたタイミングで**記事が消えた**ように見え、迷子にさせた（2026-08-23）。
  ＝**ユーザーが見ているファイルを一時的な状態にしてはいけない**。

やること:
  index.html をそのままコピーして、コピー側だけ hidden を外す。
  index.html には一切触らない。

使い方:
  python tools/preview_pickup.py            # tmp/preview_index.html を作る
  python tools/preview_pickup.py --open     # 作ってブラウザで開く
"""
import io, os, sys, subprocess

SRC = 'index.html'
OUT = 'tmp/preview_index.html'

h = io.open(SRC, encoding='utf-8').read()
n = 0
for a, b in (('<section class="pickup" id="pickup" hidden>', '<section class="pickup" id="pickup">'),
             ('<a href="#pickup" hidden>', '<a href="#pickup">')):
    if a in h:
        h = h.replace(a, b)
        n += 1
io.open(OUT, 'w', encoding='utf-8').write(h)
print('%s を作った（hiddenを外した箇所 %d ／ index.html は触っていない）' % (OUT, n))

if '--open' in sys.argv:
    subprocess.Popen(['cmd', '/c', 'start', '', 'file:///' + os.path.abspath(OUT).replace('\\', '/')])
    print('ブラウザで開いた')
