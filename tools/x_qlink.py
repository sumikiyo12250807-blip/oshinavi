# -*- coding: utf-8 -*-
"""X投稿に貼る「名前で絞り込むリンク」を、Xで最後までリンクになる形（英数字と%だけ）で出す。

2026-09-17 実測＝`oshinavi.jp/?q=世良公則` と書くと、Xは `oshinavi.jp/?q=` までしかリンクにせず、
名前が外れてトップページに着いていた（9/16 梶裕貴も同じ）。ユーザー「確実に行けるリンクにして」。
サイト側は URLSearchParams で読むので %エンコードでも名前に戻して絞り込める。

使い方: python tools/x_qlink.py 世良公則 角野隼斗 GLAY
     : python tools/x_qlink.py --check tmp/x0918/post*.txt   … 本文に日本語入りの ?q= が残っていないか見る（残っていれば exit 1）
"""
import glob
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')


def link(name):
    return 'oshinavi.jp/?q=' + urllib.parse.quote(name, safe='')


if len(sys.argv) > 1 and sys.argv[1] == '--check':
    bad = 0
    for pat in sys.argv[2:]:
        for f in sorted(glob.glob(pat)):
            for i, ln in enumerate(open(f, encoding='utf-8'), 1):
                for m in re.finditer(r'oshinavi\.jp/\?q=(\S+)', ln):
                    if re.search(r'[^A-Za-z0-9%._~-]', m.group(1)):
                        bad += 1
                        print('NG %s:%d  %s  → %s' % (f, i, m.group(0), link(urllib.parse.unquote(m.group(1)))))
    print('NG合計 %d' % bad)
    sys.exit(1 if bad else 0)

for n in sys.argv[1:]:
    print('%s\t%s' % (n, link(n)))
