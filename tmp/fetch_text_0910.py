# -*- coding: utf-8 -*-
"""URLの生HTMLをタグを剥いだ素のテキストにして出す（要約モデルを挟まない）。

[[feedback_no_fabricated_output]]＝WebFetchの小型モデルが会場名を作り替えた事故の受け皿。
"""
import html as _html
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/125.0 Safari/537.36')

for url in sys.argv[1:]:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    raw = urllib.request.urlopen(req, timeout=40).read()
    # 🚨ぴあ以外は Shift_JIS / EUC-JP のページがある。meta charset を見てから decode する
    # （化けたまま目視で読まない＝[[feedback_no_mojibake_japanese_read]]）
    best, best_bad = None, None
    for enc in ('utf-8', 'cp932', 'euc_jp', 'iso2022_jp'):
        try:
            s = raw.decode(enc, 'replace')
        except LookupError:
            continue
        bad = s.count('�')
        if best_bad is None or bad < best_bad:
            best, best_bad, best_enc = s, bad, enc
    h = best
    sys.stderr.write('  [decode] %s (置換文字 %d個)\n' % (best_enc, best_bad))
    h = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?i)<br[^>]*>|</(p|div|li|tr|h\d|td|th)>', '\n', h)
    t = _html.unescape(re.sub(r'<[^>]+>', ' ', h))
    t = re.sub(r'[ \t　]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    print('=== %s' % url)
    print(t.strip())
    print()
