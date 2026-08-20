# -*- coding: utf-8 -*-
"""Fable版のX投稿ドラフト（肉チョモランマ）の文字数と3点チェック"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

POST = '''OSHINAVIの"4日発売"ピックアップ🎫

明日8/4(火)19:00、肉チョモランマの配信ライブが一般発売スタートよ。

【配信｜Rakuten TV】肉チョモワンマン ONLINE LIVE『大決戦』- DAY1 大一番

7月4日にKアリーナ横浜で行われた本編が、8/29(土)19:00からあなたの画面に届くのよ。あの日会場に行けなかった子も、もう一度確かめたい子も、今度は特等席だわ。しかもアーカイブが9/2(水)23:59まで付くから、好きなだけ巻き戻せる。一度きりの大一番を、何度でも。これが配信の醍醐味なのよ。

一般3,500円(税込)、販売は9/2(水)20:00まで。あたしなら配信当日までに押さえておくわね。

https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#肉チョモランマ #大決戦'''

body = POST.split('https://oshinavi.jp')[0].rstrip()
print('総文字数(改行込み) %d字' % len(POST))
print('本文(URL/署名/タグ除く) %d字' % len(body))
for k, label in [('OSHINAVIの"4日発売"ピックアップ🎫', '冒頭'),
                 ('推しの"発売日"見逃さない｜OSHINAVI', '署名'),
                 ('#肉チョモランマ', 'タグ'),
                 ('https://oshinavi.jp', 'URL')]:
    print('%-4s %s' % (label, 'OK' if k in POST else '🚨無い'))
print('禁止語「浴び」 %s' % ('🚨あり' if '浴び' in POST else 'なし'))
for ng in ['YouTuber', 'Gero', 'めいちゃん', '休止', '再始動', '完売', '結成']:
    if ng in POST:
        print('🚨禁止事項「%s」が入ってる' % ng)
io.open('tmp/x_post_0804_fable.txt', 'w', encoding='utf-8').write(POST)
