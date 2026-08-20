# -*- coding: utf-8 -*-
"""8/3発売告知X投稿6本の検算（字数・4点セット・特徴語重複）"""
import collections, re

POSTS = {}

POSTS['1 XMF 2026'] = """OSHINAVIの"8/3発売"ピックアップ🎫
8/3(月) 14:00発売！
Xnterstellar Music Festival 2026
オフィシャル1次先行／10/3(土)・4(日) 韓国・仁川広域市
日韓合同クロスオーバー音楽フェス、これが記念すべき初開催なのよ
Day1にAdo、coldrain、YOUNHA、Day2にAぇ! group、Saucy Dog、平手友梨奈ほか。この顔ぶれでまだ第1弾、追加発表も控えてるの
「歴史はここから始まった」って、いつか語れる側になりなさいな
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#XMF2026 #Xnterstellar"""

POSTS['2 マカロニえんぴつ'] = """OSHINAVIの"8/3発売"ピックアップ🎫
8/3(月) 11:00発売！
マカロニえんぴつ
マカロックツアーvol.22 〜いま、きみがすき！篇〜
5次プレリザーブ／10/31(土) 真駒内セキスイハイムアイスアリーナ
全国7都市11公演のアリーナツアー、これは北海道公演の枠よ
「いま、きみがすき！」——タイトルだけで胸を撃ち抜いてくるんだから、本番がどうなるかなんて聞くだけ野暮だわね
あたしなら11時ぴったり、迷わず飛び込むわ
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#マカロニえんぴつ #マカロックツアー"""

POSTS['3 Little Glee Monster'] = """OSHINAVIの"8/3発売"ピックアップ🎫
8/3(月) 12:00発売！
Little Glee Monster
Live Tour 2026-2027 "BREATH"
プレリザーブ／宮城・秋田11/1〜11/3、石川・長野11/21〜11/22、北海道2027/1/15
茨城10/25（水戸市民会館 グロービスホール）は同日19:00発売よ
オリジナルアルバム『BREATH』を携えた全15都市16公演のホールツアーなの
あのハーモニーを息づかいごと感じられる距離、それがホールの醍醐味なのよ
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#リトグリ #BREATH"""

POSTS['4 のん'] = """OSHINAVIの"8/3発売"ピックアップ🎫
8/3(月) 10:00発売！
のん
のん自由（10）ツアー2026 in 久慈
一般発売／10/18(日) 15:00開演 岩手・十文字チキンアンバーホール 大ホール（久慈市文化会館）
久慈市で初めての、のんの単独ライブなのよ
「初めて」って、その街には一度しか降りてこないのよ。地元の人も遠征組も、その一度に立ち会える切符が月曜の朝10時に開くの
この日を待ってた人は、アラーム必須。朝イチで決めてちょうだい
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#のん #のん自由ツアー"""

POSTS['5 May’n'] = """OSHINAVIの"8/3発売"ピックアップ🎫
8/3(月) 11:00発売！
May'n
All Requests Live Tour 2026「ひらがな はんぐじゃむ」
プレリザーブ／12/6 札幌 ペニーレーン24　※岡山11/6 CRAZYMAMA KINGDOM分は先行【CANDY ROOM】が同日12:00発売よ
客席のリクエストで、その場でセットリストが組み上がっていくライブなの
つまり、あなたの一声が本編を動かすかもしれないってこと。当事者になれる公演って、なかなか無いわよ
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#Mayn #ひらがなはんぐじゃむ"""

POSTS['6 KNOCK OUT.68'] = """OSHINAVIの"8/3発売"ピックアップ🎫
8/3(月) 10:00発売！
REMY presents KNOCK OUT.68
一般発売／9/5(土) 神奈川・横浜武道館
REDスーパーフェザー級王座決定戦＝ゲーオガンワーン vs 龍聖、BLACK女子アトム級タイトルマッチ＝山田真子 vs 平岡琴、木村"フィリップ"ミノル vs 宮原穣、鈴木悠斗 vs スパイク・カーライル、さらに日本vsカンボジア「クンクメール」3対3対抗戦
ベルトの行方は、その目で見届けるものよ
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#KNOCKOUT #横浜武道館"""

HEAD = 'OSHINAVIの"8/3発売"ピックアップ🎫'
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'
URL = 'https://oshinavi.jp'

L = ['=== X投稿6本 検算（8/3発売告知）===', '']
ng = 0
for k, v in POSTS.items():
    n = len(v)
    ok_head = v.startswith(HEAD)
    ok_sign = SIGN in v
    ok_url = URL in v
    ok_tag = bool(re.search(r'^#\S', v.splitlines()[-1]))
    ok_len = 280 <= n <= 330
    bad = [name for name, ok in [('冒頭', ok_head), ('署名', ok_sign), ('URL', ok_url),
                                 ('タグ', ok_tag), ('字数', ok_len)] if not ok]
    if bad:
        ng += 1
    L.append('【%s】 %d字  %s' % (k, n, 'OK' if not bad else 'NG:' + '/'.join(bad)))

# 特徴語の重複（2字以上の漢字カタカナ語）
words = collections.Counter()
for v in POSTS.values():
    seen = set(re.findall(r'[一-龥ぁ-んァ-ヴー]{2,}', v))
    for w in seen:
        words[w] += 1
dup = [(w, c) for w, c in words.most_common() if c >= 3 and len(w) >= 2]
L.append('')
L.append('=== 3本以上で使われた語（テンプレ由来を除いて確認）===')
for w, c in dup[:25]:
    L.append('%s: %d本' % (w, c))
L.append('')
L.append('NG本数: %d' % ng)

open(r'C:\Users\user\oshinavi\tmp\x_posts_20260803_check.txt', 'w', encoding='utf-8').write('\n'.join(L))
open(r'C:\Users\user\oshinavi\tmp\x_posts_20260803.txt', 'w', encoding='utf-8').write(
    '\n\n' + ('\n\n' + '-' * 40 + '\n\n').join('【%s】\n%s' % (k, v) for k, v in POSTS.items()))
print('NG=%d' % ng)
