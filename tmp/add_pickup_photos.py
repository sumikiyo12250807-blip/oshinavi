# -*- coding: utf-8 -*-
"""記事「今週のピックアップ」に、権利がクリアな写真を3枚入れる。

ユーザー指示（2026-08-20）＝「記事に上げるピックアップのアーティストの使える素材があったら使おうよ」
                            「最初からあきらめないで、調べてみて　使えるのだけ」

🚨使ってよい根拠（調査済み）＝Wikimedia Commons の**自由ライセンス**かつ
   **Restrictions（personality＝肖像権注意）タグが無い**ものだけを選んだ。
   ・布袋寅泰    CC BY-SA 4.0 / Oecherbaer（Paaspop 2017）
   ・高嶋ちさ子  CC BY 4.0    / 外務省（2024-12-24 任命式）
   ・クーザ      CC BY 2.0    / Tibor Kovacs（シドニー公演「デス・ホイール」）
   ✗モーニング娘。は personality タグ付き＋2009年の旧メンバー写真なので**使わない**。
   ✗EXILE本体・真心ブラザーズは Commons に素材が無い。

🚨条件を守るための実装上の決めごと:
   ・**加工しない**（CC BY-SA は改変すると継承義務が生じる）。Wikimedia が配信する
     公式縮小版をそのまま保存し、CSS でも object-fit で切り取らず実比率で出す。
   ・**クレジット必須**＝撮影者名＋ライセンス名＋ライセンス本文へのリンクを figcaption に置く。

🚨index.html は CRLF。バイナリで読み書きして改行を壊さない（feedback_index_html_crlf_preserve）。
"""
import io, re, sys, json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SRC = 'index.html'
raw = open(SRC, 'rb').read()
before_crlf = raw.count(b'\r\n')
before_lf = raw.count(b'\n') - before_crlf
assert before_lf == 0, 'LF-only 行がすでにある＝先に直すこと'
h = raw.decode('utf-8')

CC = {
    'by4':   ('CC BY 4.0',    'https://creativecommons.org/licenses/by/4.0/deed.ja'),
    'bysa4': ('CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/deed.ja'),
    'by2':   ('CC BY 2.0',    'https://creativecommons.org/licenses/by/2.0/deed.ja'),
}

# (pk-name の中身, 画像, alt, 幅, 高さ, 撮影者, ライセンスキー, 添え書き, Commonsのファイルページ, 縦長か)
PHOTOS = [
    ('布袋寅泰', 'img/hotei.jpg',
     'ギターを抱えて客席に笑いかける布袋寅泰（2017年・オランダのPaaspopフェスティバル）',
     1280, 960, 'Oecherbaer', 'bysa4', '2017年 Paaspop（オランダ）',
     'https://commons.wikimedia.org/wiki/File:Tomoyasu_Hotei_Paaspop_2017.jpg', False),

    ('シルク・ドゥ・ソレイユ「クーザ」', 'img/kooza39.jpg',
     '真っ赤な照明の中、宙づりの大きな輪の上を歩くパフォーマー（「クーザ」の演目デス・ホイール）',
     1280, 853, 'Tibor Kovacs', 'by2', 'シドニー公演より（演目「デス・ホイール」）',
     'https://commons.wikimedia.org/wiki/File:Kooza_in_Sydney39.jpg', False),

    ('結成20周年の記念ツアー', 'img/takashima.jpg',
     '高嶋ちさ子（2024年12月24日・外務省にて）',
     416, 520, '外務省', 'by4', '2024年12月24日 外務省',
     'https://commons.wikimedia.org/wiki/File:Chisako_Takashima_on_December_24,_2024_(cropped).jpg', True),
]

NL = '\r\n'


def figure(img, alt, w, hgt, author, lickey, note, page, portrait):
    lic, licurl = CC[lickey]
    cls = 'pk-fig pk-portrait' if portrait else 'pk-fig'
    return (
        '        <figure class="%s">' % cls + NL +
        '          <img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">' % (img, alt, w, hgt) + NL +
        '          <figcaption>%s／Photo: <a href="%s" target="_blank" rel="noopener">%s</a> '
        '(<a href="%s" target="_blank" rel="noopener">%s</a>)</figcaption>' % (note, page, author, licurl, lic) + NL +
        '        </figure>' + NL
    )


done = []
for name, img, alt, w, hgt, author, lickey, note, page, portrait in PHOTOS:
    # 「その名前の pk-name」から始めて、直後に出てくる最初の pk-detail 開始タグを探す
    i = h.find('<span class="pk-name">%s' % name)
    if i < 0:
        print('🚨 見出しが見つからない:', name)
        continue
    tag = '<div class="pk-detail" hidden>' + NL
    j = h.find(tag, i)
    if j < 0:
        print('🚨 pk-detail が見つからない:', name)
        continue
    ins = j + len(tag)
    h = h[:ins] + figure(img, alt, w, hgt, author, lickey, note, page, portrait) + h[ins:]
    done.append(name)

# ---- CSS（実比率のまま出す＝切り取らない）----
CSS_ANCHOR = '    .pickup .pk-act p {'
css = (
    '    .pickup .pk-fig { margin: 0 0 13px; }' + NL +
    '    .pickup .pk-fig img {' + NL +
    '      display: block; width: 100%; height: auto;' + NL +
    '      border: 1px solid var(--border); border-radius: 5px; background: var(--bg3);' + NL +
    '    }' + NL +
    '    .pickup .pk-portrait img { max-width: 190px; }' + NL +
    '    .pickup .pk-fig figcaption {' + NL +
    '      font-size: 10.5px; line-height: 1.65; color: var(--text-muted); margin-top: 6px;' + NL +
    '    }' + NL +
    '    .pickup .pk-fig figcaption a { color: var(--text-muted); text-decoration: underline; }' + NL
)
assert h.count(CSS_ANCHOR) == 1, 'CSSの挿入先が一意でない'
h = h.replace(CSS_ANCHOR, css + CSS_ANCHOR)

out = h.encode('utf-8')
after_crlf = out.count(b'\r\n')
after_lf = out.count(b'\n') - after_crlf
assert after_lf == 0, '🚨 LF が混ざった'
open(SRC, 'wb').write(out)

print('写真を入れた:', '／'.join(done))
print('CRLF %d → %d（LF-only %d）' % (before_crlf, after_crlf, after_lf))
print('図の数:', h.count('class="pk-fig'))
