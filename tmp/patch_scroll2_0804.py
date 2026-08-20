# -*- coding: utf-8 -*-
"""自動スクロールは「Enter」と「サジェスト候補クリック」の時だけにする
（ユーザー 2026-08-04「早いよ エンターおすか候補を押したら動くようにして」）。
入力中(デバウンス350ms)のスクロールを外す。CRLF維持。"""
import io
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'index.html')
h = io.open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'

old = NL.join([
    '      showSuggest(searchQuery);',
    '      if (searchQuery) scrollToResults(350); else clearTimeout(scrollTimer);',
])
new = '      showSuggest(searchQuery);'
assert h.count(old) == 1, '入力ハンドラのアンカーが%d件' % h.count(old)
h = h.replace(old, new, 1)

# コメントも今の仕様に合わせる（打っている途中では動かさない）
oldc = NL.join([
    '    // 1文字ごとに飛ぶと読めないので、入力が止まってから動かす（デバウンス）。',
])
newc = NL.join([
    '    // 🚨打っている途中では動かさない（ユーザー 2026-08-04「早いよ」）。',
    '    // 動くのは「Enterを押した時」と「サジェスト候補を選んだ時」の2つだけ。',
])
assert h.count(oldc) == 1, 'コメントのアンカーが%d件' % h.count(oldc)
h = h.replace(oldc, newc, 1)

bak = os.path.join(ROOT, 'index.html.bak_0804_search_scroll2')
shutil.copyfile(P, bak)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
raw = open(P, 'rb').read()
print('patched. stray_lf=%d backup=%s'
      % (raw.count(b'\n') - raw.count(b'\r\n'), os.path.basename(bak)))
