# -*- coding: utf-8 -*-
"""記事セクションの見た目を確認するための「プレビュー用の複製」を作る（恒久ツール・2026-08-23 新設）。

🚨なぜ要るか:
  ユーザーは常にローカルの file://index.html を開いて見ている（feedback_user_checks_local_file）。
  確認のために index.html の hidden を外す→撮る→戻す をやると、
  ちょうど更新をかけたタイミングで記事が消えたように見えて迷子にさせる（2026-08-23 実際にやった）。

🚨🚨置き場所は「リポジトリのルート」でなければならない（2026-08-23 の失敗）:
  最初 tmp/preview_index.html に出したら、`img/hotei.jpg` のような**相対パスが tmp/img/ を探しに行き、
  画像が1枚も出なかった**。ユーザーに「画像がない　全部」と指摘された。
  → index.html と**同じ階層**に置く。これで img/ も p/ も同じように解決する。

やること:
  index.html をそのままコピーして、コピー側だけ hidden を外す。index.html には一切触らない。

使い方:
  python tools/preview_pickup.py            # _preview.html を作る
  python tools/preview_pickup.py --open     # 作ってブラウザで開く
  python tools/preview_pickup.py --clean    # 後片付け（消す）

🆕--section <path>（2026-08-30 追加）:
  まだ index.html に入れていない次号のセクションを、コピー側にだけ差し込んで見せる。
  「差し替える前に見てもらう」のが毎号の手順なのに、この口が無くて毎回その場のスクリプトを書いていた。
  python tools/preview_pickup.py --section tmp/pickup0830/section.html --open
"""
import io, os, re, sys, subprocess

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC = 'index.html'
OUT = '_preview.html'          # 🚨ルート直下（img/ の相対パスを壊さないため）

if '--clean' in sys.argv:
    for p in (OUT, 'tmp/preview_index.html'):
        if os.path.exists(p):
            os.remove(p)
            print('消した: %s' % p)
    sys.exit(0)

h = io.open(SRC, encoding='utf-8').read()

# 🆕未適用の次号セクションを、コピー側にだけ差し込む（index.html は触らない）
if '--section' in sys.argv:
    sec_path = sys.argv[sys.argv.index('--section') + 1]
    new_sec = io.open(sec_path, encoding='utf-8').read().rstrip()
    i = h.index('<section class="pickup"')
    j = h.index('</section>', i) + len('</section>')
    h = h[:i] + new_sec + h[j:]
    print('差し込んだ（コピー側だけ）: %s' % sec_path)

n = 0
for a, b in (('<section class="pickup" id="pickup" hidden>', '<section class="pickup" id="pickup">'),
             ('<a href="#pickup" hidden>', '<a href="#pickup">')):
    if a in h:
        h = h.replace(a, b)
        n += 1
io.open(OUT, 'w', encoding='utf-8').write(h)

# 画像が本当に引けるかを機械で確かめる（相対パスの壊れを二度と見逃さない）
# ?v=5 のようなクエリは落としてから存在を見る
def _path(u):
    return u.split('?')[0].split('#')[0]
miss = [s for s in sorted(set(re.findall(r'<img[^>]+src="([^"]+)"', h)))
        if not s.startswith(('http', 'data:')) and not os.path.exists(_path(s))]
print('%s を作った（hiddenを外した箇所 %d ／ index.html は触っていない）' % (OUT, n))
if miss:
    print('[NG] 参照できない画像 %d件: %s' % (len(miss), miss[:5]))
    sys.exit(2)
print('画像の参照 OK（欠けなし）')

if '--open' in sys.argv:
    subprocess.Popen(['cmd', '/c', 'start', '', 'file:///' + os.path.abspath(OUT).replace('\\', '/')])
    print('ブラウザで開いた')
