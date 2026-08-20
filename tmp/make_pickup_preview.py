# -*- coding: utf-8 -*-
"""記事セクションだけを抜き出した軽いプレビューを作る（確認用・公開しない）。

4.8MB の index.html を丸ごと開くとスクロール位置を探すのに時間がかかるので、
<style> と <section class="pickup"> だけを取り出して小さな HTML にする。
折りたたみは確認しやすいよう**最初から開いた状態**で出す。
画像の相対パス img/... を活かすため、出力はリポジトリのルートに置く。
"""
import io, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

h = io.open('index.html', encoding='utf-8').read()

style = re.search(r'<style>.*?</style>', h, re.S)
assert style, 'style が見つからない'

i = h.find('<section class="pickup"')
j = h.find('</section>', i)
assert i > 0 and j > i, 'pickup セクションが見つからない'
sec = h[i:j + len('</section>')]

# 確認用: hidden を外して全部開いた状態にする
sec = sec.replace('<section class="pickup" id="pickup" hidden>', '<section class="pickup" id="pickup">')
sec = sec.replace('<div class="pk-detail" hidden>', '<div class="pk-detail">')
sec = sec.replace('<div class="pk-body" hidden>', '<div class="pk-body">')
sec = sec.replace('aria-expanded="false"', 'aria-expanded="true"')

out = (
    '<!doctype html><html lang="ja"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1">'
    '<title>記事プレビュー</title>' + style.group(0) +
    '<style>body{background:var(--bg);padding:10px}</style></head><body>' +
    sec + '</body></html>'
)
io.open('_pickup_preview.html', 'w', encoding='utf-8', newline='\r\n').write(out)
print('プレビュー生成 %.0fKB / 図 %d枚 / 開いた状態' % (len(out) / 1024, sec.count('class="pk-fig')))
