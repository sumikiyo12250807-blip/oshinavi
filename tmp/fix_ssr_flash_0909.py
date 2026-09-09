# -*- coding: utf-8 -*-
"""読み込み直後の数秒、AI向けのSSR一覧（.ai-ssr）が生のまま見える問題を直す。

ユーザー報告（2026-09-09）「最初の数秒、変な風に表示される」。
原因＝ index.html の #eventList の中に <div class="ai-ssr"> が約4,700行そのまま入っていて、
       .ai-ssr を隠すCSSが1つも無い。JSがカードを描くまで箇条書きが素で見える。

🚨単純に display:none にしない＝AIアプリは「非表示コンテンツ」を無視することがあり、
  そもそも <noscript> をやめてSSR埋め込みにした理由がそれ（build_ai_page.py の注記）。
✅ JSが動いた時だけ隠す＝<html> に js クラスを即つけて `.js .ai-ssr{display:none}`。
   JSを実行しないクローラーには今までどおり見えたまま。

CRLFを壊さないよう newline='' で読み書きする。
"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'index.html'
h = io.open(P, encoding='utf-8', newline='').read()
orig = h

SCRIPT = ('  <script>document.documentElement.classList.add("js");</script>\r\n'
          '\r\n')
CSS = ('  <style>\r\n'
       '    /* 🚨読み込み直後にAI向けのSSR一覧が生で見えるのを防ぐ。\r\n'
       '       JSが動いた時だけ隠す＝JSを実行しないクローラーには今までどおり見える。 */\r\n'
       '    .js .ai-ssr { display: none; }\r\n')

assert h.count('<style>') >= 1, '<style> が見つからない'
assert 'classList.add("js")' not in h, 'もう入っている。中止'

# 最初の <style> の直前にスクリプトを差し、その <style> の頭にCSSを足す
idx = h.index('  <style>\r\n')
h = h[:idx] + SCRIPT + CSS + h[idx + len('  <style>\r\n'):]

print('差分: %+d バイト' % (len(h) - len(orig)))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('書き込み完了')
