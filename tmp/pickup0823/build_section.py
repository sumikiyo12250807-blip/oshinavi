# -*- coding: utf-8 -*-
"""「今週のピックアップ」（8/24〜8/30号）のセクションHTMLを組み立てる。

本文は Fable が書いた tmp/pickup0823/*.txt をそのまま流し込む（勝手に手を入れない）。
事実（発売日時・会場・公演日）はローカルデータとぴあ実ページで裏取り済み。
出力＝tmp/pickup0823/section.html （index.html への差し替えは別スクリプト）
"""
import io, html

D = 'tmp/pickup0823/'


def t(name):
    return io.open(D + name + '.txt', encoding='utf-8').read().strip()


def esc(s):
    return html.escape(s, quote=False)


def paras(txt):
    """空行で段落、行内改行は <br> にする"""
    out = []
    for blk in txt.split('\n\n'):
        blk = blk.strip()
        if blk:
            out.append('<p>' + esc(blk).replace('\n', '<br>') + '</p>')
    return '\n        '.join(out)


lede = [l for l in t('lede').split('\n') if l.strip()]

ACTS = [
    dict(cls='pk-act pk-top', name='EXILE', sale='8/29(土) 10:00 一般発売',
         search='EXILE', body=t('exile'), fig=None,
         shows='埼玉・ベルーナドーム　11/14(土)・11/15(日) の2公演'),
    dict(cls='pk-act pk-top', name='布袋寅泰', sale='8/29(土) 10:00 に5公演ぶん一斉',
         search='布袋寅泰', body=t('hotei'),
         fig=('img/hotei.jpg', 1280, 960,
              'ギターを抱えて客席に笑いかける布袋寅泰（2017年・オランダのPaaspopフェスティバル）',
              '2017年 Paaspop（オランダ）／Photo: <a href="https://commons.wikimedia.org/wiki/File:Tomoyasu_Hotei_Paaspop_2017.jpg" target="_blank" rel="noopener">Oecherbaer</a> (<a href="https://creativecommons.org/licenses/by-sa/4.0/deed.ja" target="_blank" rel="noopener">CC BY-SA 4.0</a>)'),
         shows='宮城 9/22・9/23 ／ 埼玉 10/16・10/17 ／ 東京 11/14'),
    dict(cls='pk-act pk-top', name='真心ブラザーズ<span class="pk-most">公演数が今週最多</span>',
         sale='8/29(土) 10:00 に9公演ぶん一気に',
         search='真心ブラザーズ', body=t('magokoro'), fig=None,
         shows='埼玉 11/23 ／ 岡山 12/5 ／ 香川 12/6 ／ 静岡 12/25 ／<br>愛知 2027/1/16 ／ 大阪 2027/1/17 ／ 岩手 2027/1/23 ／ 宮城 2027/1/24 ／ 東京 2027/1/30'),
    dict(cls='pk-act', name='モーニング娘。&#39;26', sale='8/25(火) 11:00 と 8/29(土) 10:00',
         search='モーニング娘', body=t('morningmusume'), fig=None,
         shows='8/25(火) 11:00 … 北海道 10/25（2次受付）<br>8/29(土) 10:00 … 大阪 9/21 ／ 愛知 9/23 ／ 茨城 9/26'),
    dict(cls='pk-act', name='シルク・ドゥ・ソレイユ「クーザ」', sale='8/29(土) 10:00 セブン-イレブン先行',
         search='クーザ', body=t('kooza'),
         fig=('img/kooza39.jpg', 1280, 853,
              '真っ赤な照明の中、宙づりの大きな輪の上を歩くパフォーマー（「クーザ」の演目デス・ホイール）',
              'シドニー公演より（演目「デス・ホイール」）／Photo: <a href="https://commons.wikimedia.org/wiki/File:Kooza_in_Sydney39.jpg" target="_blank" rel="noopener">Tibor Kovacs</a> (<a href="https://creativecommons.org/licenses/by/2.0/deed.ja" target="_blank" rel="noopener">CC BY 2.0</a>)'),
         shows='2027年 2/24-2/28 ／ 3/1-3/9 ／ 3/11-3/20 ／ 3/21-3/30 ／<br>4/2-4/10 ／ 4/11-4/20 ／ 4/21-4/25'),
]

TILES = [
    ('プロレスリング・ノア', 'プロレスリング・ノア', '<b>8/24(月)</b> 12:00・7公演'),
    ('新日本フィルハーモニー交響楽団', '新日本フィルハーモニー交響楽団「第九」特別演奏会2026', '8/29 10:00・5公演'),
    ('フラワーカンパニーズ', 'フラワーカンパニーズ', '8/29 10:00・4公演'),
    ('FTISLAND', 'FTISLAND', '8/29 10:00・4公演'),
    ('浜崎貴司', '浜崎貴司', '8/29 10:00・4公演'),
    ('ORANGE RANGE', 'ORANGE RANGE', '8/29 10:00・3公演'),
    ('凛として時雨', '凛として時雨', '8/29 10:00・3公演'),
    ('徳永英明', '徳永英明', '8/29 10:00・3公演'),
    ('ヒルクライム', 'ヒルクライム', '<b>8/24(月)</b> 11:00・3公演'),
    ('7ORDER', '7ORDER', '8/29 <b>12:00</b>・2公演'),
    ('coldrain', 'coldrain', '8/29 10:00'),
    ('大原櫻子', '大原櫻子', '8/29 10:00'),
    ('岩崎宏美', '岩崎宏美', '<b>8/28(金)</b> 10:00'),
    ('松平健', '松平健', '<b>8/28(金)</b> 10:00'),
]

o = []
o.append('<section class="pickup" id="pickup" hidden>')
o.append('  <span class="pk-label">📖 今週のピックアップ</span>')
o.append('  <h2 class="pk-title">EXILE・布袋寅泰・真心ブラザーズ、それにシルク・ドゥ・ソレイユも一斉発売！</h2>')
o.append('  <p class="pk-sub">8/24(月)〜8/30(日)にチケットの発売が始まるアーティスト紹介</p>')
o.append('  <div class="pk-lede">')
for i, l in enumerate(lede):
    cls = ' class="pk-tease"' if i == len(lede) - 1 else ''
    o.append('    <p%s>%s</p>' % (cls, esc(l)))
o.append('  </div>')
o.append('  <button class="pk-more" id="pickupMore" type="button" aria-expanded="false" aria-controls="pickupBody">今週の主役を読む</button>')
o.append('  <div class="pk-body" id="pickupBody" hidden>')
o.append('      <h3 class="pk-h2">今週の主役</h3>')

for a in ACTS:
    o.append('')
    o.append('      <div class="%s">' % a['cls'])
    o.append('        <button class="pk-open" type="button" aria-expanded="false">')
    o.append('          <span class="pk-name">%s</span>' % a['name'])
    o.append('          <span class="pk-sale">%s</span>' % a['sale'])
    o.append('        </button>')
    o.append('        <div class="pk-detail" hidden>')
    if a['fig']:
        src, w, h, alt, cap = a['fig']
        o.append('        <figure class="pk-fig">')
        o.append('          <img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">' % (src, alt, w, h))
        o.append('          <figcaption>%s</figcaption>' % cap)
        o.append('        </figure>')
    o.append('        ' + paras(a['body']))
    o.append('        <a class="pk-shows" href="#" data-pk-search="%s">' % a['search'])
    o.append('          <b>発売になる公演<span class="pk-go">タップで探す →</span></b>')
    o.append('          %s' % a['shows'])
    o.append('        </a>')
    o.append('        </div>')
    o.append('      </div>')

o.append('')
o.append('      <h3 class="pk-h2">今週はほかにも</h3>')
o.append('')
o.append('      <p class="pk-others-note">名前を押すと、そのアーティストのチケットを探せるわ。</p>')
o.append('')
o.append('      <div class="pk-others">')
for search, label, when in TILES:
    o.append('')
    o.append('        <a href="#" data-pk-search="%s"><span class="pk-o-name">%s</span><span class="pk-o-when">%s</span></a>'
             % (search, esc(label), when))
o.append('')
o.append('      </div>')
o.append('')
o.append('      <h3 class="pk-h2">深掘り：高嶋ちさ子 12人のヴァイオリニスト</h3>')
o.append('')
o.append('      <div class="pk-act">')
o.append('        <button class="pk-open" type="button" aria-expanded="false">')
o.append('          <span class="pk-name">結成20周年の記念ツアー</span>')
o.append('          <span class="pk-sale">8/29(土) 10:00 発売</span>')
o.append('        </button>')
o.append('        <div class="pk-detail" hidden>')
o.append('        <figure class="pk-fig pk-portrait">')
o.append('          <img src="img/takashima.jpg" alt="高嶋ちさ子（2024年12月24日・外務省にて）" width="416" height="520" loading="lazy" decoding="async">')
o.append('          <figcaption>2024年12月24日 撮影／Photo: <a href="https://commons.wikimedia.org/wiki/File:Chisako_Takashima_on_December_24,_2024_(cropped).jpg" target="_blank" rel="noopener">外務省</a> (<a href="https://creativecommons.org/licenses/by/4.0/deed.ja" target="_blank" rel="noopener">CC BY 4.0</a>)</figcaption>')
o.append('        </figure>')
o.append('        ' + paras(t('takashima')))
o.append('        <a class="pk-shows" href="#" data-pk-search="高嶋ちさ子">')
o.append('          <b>発売になる公演<span class="pk-go">タップで探す →</span></b>')
o.append('          富山・石川・福井・長野　10/29〜11/3公演<br>全席指定 8,000円（税込）')
o.append('        </a>')
o.append('        </div>')
o.append('      </div>')
o.append('')
o.append('      <p class="pk-others-note">この週にチケットの発売が始まる公演は、全部で325件あるわ。</p>')
o.append('      <a class="pk-tail" href="#" data-pk-status="urgent">%s<span class="pk-go">今週発売を見る →</span></a>' % esc(t('tail')))
# 🚨閉じるボタンは本文の一番下（2026-08-23 ユーザー「折りたたむボタンは普通、一番下にあるものよ」）
o.append('      <button class="pk-more pk-close" id="pickupClose" type="button">折りたたむ</button>')
o.append('  </div>')
o.append('</section>')

io.open(D + 'section.html', 'w', encoding='utf-8').write('\n'.join(o))
print('wrote %s (%d bytes)' % (D + 'section.html', len('\n'.join(o).encode('utf-8'))))
