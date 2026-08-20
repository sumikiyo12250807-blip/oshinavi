# -*- coding: utf-8 -*-
"""milet投稿の修正版（ツアー名を訂正）。

🚨 訂正の経緯:
  誤「milet Hall Tour 2026」＝WebSearch結果の"ページタイトル"を鵜呑みにしたもの。一次ソース未確認。
  正「milet live tour 2026「Made of Glass」」＝milet本人の公式X「ツアータイトル決定！」で確認。
  ぴあには「9月より、全国ホールツアー開催決定」としか書かれていない（ユーザーが実物で確認）。
  → ツアー名はぴあに無い場合、必ず公式で裏取りする（memory: project_sns_promotion）。

裏取り済みの事実:
  - ツアー名 = milet live tour 2026「Made of Glass」（本人公式X）
  - 4thアルバム「Made of Glass」2026/8/19リリース、それを引っ提げた"2年ぶり"の全国ホールツアー（同上）
  - 全国17都市19公演・9/12(千葉)〜11/22(大分)（ソニーミュージック公式で全日程を確認）
  - 札幌 11/13(金) 札幌文化芸術劇場hitaru / 6次プレリザーブ 7/21 11:00〜7/27 11:00（ぴあ実ページ）
  - 🚨 OSHINAVI掲載は札幌1件のみ。他18公演は未掲載＝「他の日程も」とは書けない。
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')

BODY = '''OSHINAVIの"明日発売"ピックアップ🎫
7/21(火)11:00〜 6次プレリザーブ

milet live tour 2026「Made of Glass」
新作を引っ提げた、2年ぶりの全国ホールツアー
11/13(金) 札幌文化芸術劇場hitaru

あの声を、ホールいっぱいに浴びる夜。
受付〜7/27
推しの"発売日"見逃さない｜OSHINAVI
#milet #MadeofGlass'''

# 少し短い版（会場を落として気持ちを厚く）
BODY_S = '''OSHINAVIの"明日発売"ピックアップ🎫
7/21(火)11:00〜 6次プレリザーブ

milet live tour 2026「Made of Glass」
新作を引っ提げた、2年ぶりの全国ホールツアー
11/13(金) 札幌hitaru

あの声を、浴びに行く秋。
受付〜7/27
推しの"発売日"見逃さない｜OSHINAVI
#milet #MadeofGlass'''

REPLY = '''先行が6次まで来ていると気づかないまま、当日を迎えてしまうことがあります。
miletの札幌公演、受付は7/27(月)11:00まで。

そういう"気づかないうちに終わってた"を無くしたくて作りました
https://oshinavi.jp'''

for label, t in (('本文(会場フル)', BODY), ('本文(短縮版)', BODY_S), ('セルフリプ', REPLY)):
    print(f'=== {label} {len(t)}字 ===')
    print(t)
    print()
