# -*- coding: utf-8 -*-
"""8/4発売 X投稿ドラフト（肉チョモランマ）＝文字数を機械カウントする。
memory: project_sns_promotion（約300字・おねえ言葉・冒頭/署名/タグの3点）
        feedback_x_no_link_spam（本文に素の https://oshinavi.jp を貼る）
"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

POST = '''OSHINAVIの"4日発売"ピックアップ🎫
8/4(火)19:00 一般発売スタート

【肉チョモランマ】
ワンマンライブ2026『大決戦』- DAY1 大一番
7/4のKアリーナ横浜。あの一番が、配信で帰ってくるわ。

行きたかったのに行けなかった人。会場にいたけど、もう一度あの瞬間を確かめたい人。どっちも救われる5日間よ。

8/29(土)19:00からライブ配信、そのあと9/2(水)23:59までアーカイブ付き。巻き戻して何度でも浸っていいの。一般3,500円(税込)、受付は9/2(水)20:00まで。

発売時刻を逃すのがいちばん惜しいわ。カウントダウンはあたしが見張っててあげる。
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#肉チョモランマ #大決戦 #肉チョモワンマン'''

print(POST)
print()
print('=' * 40)
print('総文字数(改行込み) %d字' % len(POST))
print('URL・タグ・署名を除いた本文 %d字' % len(POST.split('https://oshinavi.jp')[0].rstrip()))
for k, label in [('OSHINAVIの"4日発売"ピックアップ🎫', '冒頭'),
                 ('推しの"発売日"見逃さない｜OSHINAVI', '署名'),
                 ('#肉チョモランマ', 'タグ'),
                 ('https://oshinavi.jp', 'URL')]:
    print('%s: %s' % (label, 'OK' if k in POST else '🚨無い'))
io.open('tmp/x_post_0804_niku.txt', 'w', encoding='utf-8').write(POST)
