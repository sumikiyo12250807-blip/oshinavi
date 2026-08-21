# -*- coding: utf-8 -*-
"""今夜のX投稿5本を機械検品する（2026-08-21）。

チェック項目（[[project_sns_promotion]]／[[feedback_x_kuten_kaigyo]]／[[feedback_x_cta_wording]]）:
 ①字数 250〜330（改行も1字）
 ②「。」の直後に文字が続いていないか
 ③冒頭「OSHINAVIの"明日発売"ピックアップ🎫」
 ④CTA「▼チケット情報はこちら」＋素の https://oshinavi.jp
 ⑤署名「推しの"発売日"見逃さない｜OSHINAVI」
 ⑥ハッシュタグ
 ⑦🚨**本文に書いた曜日が実カレンダーと合っているか**
"""
import io, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

POSTS = {}
POSTS['①ONE OK ROCK'] = '''OSHINAVIの"明日発売"ピックアップ🎫
8/22(土) 10:00発売！

ONE OK ROCK
「DETOX JAPAN TOUR FINAL 2026」

アルバム「DETOX」を掲げて世界を回った先の、日本凱旋ツアーよ。
愛知・福岡・宮城・千葉、4カ所8公演の締めくくりがZOZOマリン。
この結末、スタジアムで見届けなきゃ嘘だわ。

9/5(土)・9/6(日) ZOZOマリンスタジアム（千葉）
※両日それぞれ一般発売よ

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#ONEOKROCK #DETOXJAPANTOURFINAL2026'''

POSTS['②PEDRO'] = '''OSHINAVIの"明日発売"ピックアップ🎫
8/22(土) 発売！※時刻は公演別よ

PEDRO
PEDRO TOUR 2026-2027「This is PEDRO TOUR」

10月から全国22公演の大規模ワンマンよ。
ファイナルは2027年1月10日、Zepp DiverCity（東京）。
長い旅の切符、初日から握っておきなさいな。

10:00発売＝茨城10/28・千葉11/11
20:00発売＝広島10/17・岡山10/18・神奈川11/5・北海道12/15,12/17

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#PEDRO #ThisisPEDROTOUR'''

POSTS['③CUTIE STREET'] = '''OSHINAVIの"明日発売"ピックアップ🎫
8/22(土) 10:00発売！

CUTIE STREET
「CUTIE STREET 梅田みゆ 生誕祭 2026」

梅田みゆの誕生日を祝う生誕祭よ。
主役の名前がついた一夜なんて、行かない理由がないでしょ。
全席指定6,500円（税込）、席はちゃんと用意されてるわ。

9/14(月) SGC HALL ARIAKE（東京）
17:30開場／19:00開演

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#CUTIESTREET #きゅーすと #梅田みゆ'''

POSTS['④キュウソネコカミ'] = '''OSHINAVIの"明日発売"ピックアップ🎫
8/22(土) 10:00発売！

キュウソネコカミ
「DMCC REAL ONEMAN TOUR 2026-2027」

今回の解禁は北の街から九州まで5公演よ。
近くに来るこの機会、指をくわえて見送るんじゃないわよ。
土曜の10時、忘れずに構えてちょうだい。

新潟11/18／石川11/20／旭川11/23・札幌11/25／福岡2027年2/11

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#キュウソネコカミ #DMCC'''

POSTS['⑤まとめ'] = '''OSHINAVIの"明日発売"ピックアップ🎫
8/22(土)は発売ラッシュよ

ONE OK ROCK、PEDRO、キュウソネコカミだけじゃないの。
布袋寅泰に森高千里、沢田研二、hide with Spread Beaverまで、明日まとめて発売なのよ。
おいしくるメロンパンもつばきファクトリーも陰陽座も控えてるわ。
名前を挙げたらキリがない、そういう土曜なの。
推しの名前、確かめてから寝なさいな。

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#チケット発売 #OSHINAVI'''

WD = '月火水木金土日'
ng = 0
for name, body in POSTS.items():
    n = len(body)
    issues = []
    if not (250 <= n <= 330):
        issues.append('字数 %d（250〜330の外）' % n)
    if re.search(r'。(?=[^\s])', body):
        issues.append('「。」の直後に文字が続く')
    if not body.startswith('OSHINAVIの"明日発売"ピックアップ🎫'):
        issues.append('冒頭のピックアップが無い')
    if '▼チケット情報はこちら' not in body:
        issues.append('CTAが無い')
    if 'https://oshinavi.jp' not in body:
        issues.append('URLが無い')
    if re.search(r'oshinavi\.jp/?\?', body):
        issues.append('URLにパラメータが付いている')
    if '推しの"発売日"見逃さない｜OSHINAVI' not in body:
        issues.append('署名が無い')
    if not re.search(r'#\S', body):
        issues.append('ハッシュタグが無い')
    # 曜日照合（M/D(曜) 形）
    for mm, dd, w in re.findall(r'(\d{1,2})/(\d{1,2})\((.)\)', body):
        y = 2027 if (int(mm), int(dd)) in ((1, 10), (2, 11)) else 2026
        real = WD[datetime.date(y, int(mm), int(dd)).weekday()]
        if real != w:
            issues.append('曜日ズレ %s/%s(%s) ← 実際は(%s)' % (mm, dd, w, real))
    print('%-16s 字数%3d  %s' % (name, n, 'OK' if not issues else '🚨 ' + ' / '.join(issues)))
    ng += len(issues)
print()
print('=== 指摘 %d件 ===' % ng)
# 5本の重複語チェック
import collections
words = collections.Counter()
for b in POSTS.values():
    for w in re.findall(r'[ぁ-んァ-ヶ一-龠]{3,}', b):
        words[w] += 1
dup = [(w, c) for w, c in words.items() if c >= 3]
print('3本以上に出る語:', dup if dup else 'なし')
