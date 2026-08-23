# -*- coding: utf-8 -*-
"""組み立てた記事セクションを index.html に差し替える（恒久ツール・2026-08-23 新設）。

🚨なぜ専用ツールが要るか:
  差し替えを毎回その場のスクリプトでやっていたら、**組み立て側が出す `hidden` をそのまま貼って
  記事が消える**事故を2回やった（ユーザー「更新したら記事が消えた」×2）。
  表示/非表示は「今 index.html がどうなっているか」を正として引き継ぐ。差し替えでは変えない。

やること:
  1. index.html の <section class="pickup" …> … </section> を差し替える
  2. 差し替え前の hidden 状態（section と ヘッダーの #pickup リンク）を**そのまま引き継ぐ**
  3. CRLF指紋・画像の参照・「。」の未改行を機械で確かめる

使い方:
  python tools/apply_pickup.py tmp/pickup0823/section.html
  python tools/apply_pickup.py tmp/pickup0823/section.html --show   # 表示状態にする
  python tools/apply_pickup.py tmp/pickup0823/section.html --hide   # 非表示にする
"""
import io, os, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else 'tmp/pickup0823/section.html'
h = io.open('index.html', encoding='utf-8').read()
new = io.open(SRC, encoding='utf-8').read().rstrip()

# ── 1. 今の表示状態を読む（これが正）
was_hidden = '<section class="pickup" id="pickup" hidden>' in h
nav_hidden = '<a href="#pickup" hidden>' in h
if '--show' in sys.argv:
    was_hidden = nav_hidden = False
if '--hide' in sys.argv:
    was_hidden = nav_hidden = True

# ── 2. 差し替え
i = h.index('<section class="pickup"')
j = h.index('</section>', i) + len('</section>')
io.open('index.html.bak_pickup', 'w', encoding='utf-8').write(h)
h2 = h[:i] + new + h[j:]

# ── 3. 状態を戻す
h2 = h2.replace('<section class="pickup" id="pickup" hidden>', '<section class="pickup" id="pickup">')
h2 = h2.replace('<a href="#pickup" hidden>', '<a href="#pickup">')
if was_hidden:
    h2 = h2.replace('<section class="pickup" id="pickup">', '<section class="pickup" id="pickup" hidden>')
if nav_hidden:
    h2 = h2.replace('<a href="#pickup">', '<a href="#pickup" hidden>')

io.open('index.html', 'w', encoding='utf-8').write(h2)

# ── 4. 機械チェック
d = io.open('index.html', 'rb').read()
bare = d.count(b'\n') - d.count(b'\r\n')
crcr = d.count(b'\r\r\n')
sec = h2[h2.index('<section class="pickup"'):h2.index('</section>', h2.index('<section class="pickup"'))]
imgs = [s.split('?')[0] for s in re.findall(r'<img[^>]+src="([^"]+)"', sec)]
miss = [s for s in imgs if not s.startswith(('http', 'data:')) and not os.path.exists(s)]
KEEP_OK = ('モーニング娘。', 'わよ。')       # 名前の中の。と 文末＋ボタン は割らない
kuten = [m.start() for m in re.finditer(r'。(?!<br>)(?!</p>)', sec)
         if not any(k in sec[max(0, m.start() - 12):m.start() + 1] for k in KEEP_OK)]

print('差し替えた: %s → index.html' % SRC)
print('表示状態: セクション=%s / ナビ=%s' % ('非表示' if was_hidden else '表示',
                                           '非表示' if nav_hidden else '表示'))
print('CRLF指紋: bareLF=%d CRCRLF=%d %s' % (bare, crcr, 'OK' if bare == 0 and crcr == 0 else '[NG]'))
print('画像: %d件 / 見つからない %d件 %s' % (len(imgs), len(miss), miss or 'OK'))
print('「。」の未改行: %d件 %s' % (len(kuten), 'OK' if not kuten else '[NG]'))
if miss or kuten or bare or crcr:
    sys.exit(2)
