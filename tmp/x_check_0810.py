# -*- coding: utf-8 -*-
"""2026-08-10 X投稿3本の機械チェック（字数・「。」直後改行・3点セット・語の重複）。"""
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P1 = """OSHINAVIの"本日発売"ピックアップ🎫

平日の夜、仕事終わりにプロレスへ直行する。
それが叶うのが後楽園ホールのナイター興行なのよ。

「STARDOM NIGHTER in KORAKUEN 2026 Sep.」
9月29日(火)、東京・後楽園ホール。
一般発売は本日8/10(月)12:00からよ。

火曜の夜を推しの闘いで塗り替えるなんて、最高の贅沢だと思わない?
今日のお昼12時、忘れないでちょうだい。

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#スターダム #STARDOM #後楽園ホール"""

P2 = """OSHINAVIの"本日発売"ピックアップ🎫

会場はアリーナでもホールでもないの。
鹿児島国際大学の学園祭「第27回 遊華俚祭」、その特設ステージなのよ。

FUNKY MONKEY BΛBY'S
11月21日(土)、フィールドハウス内特設ステージで開催。
一般発売は本日8/10(月)10:00から。

学園祭の空気ごとファンモンを味わえるなんて、この日この場所だけの話だわ。
こんな機会、そうそうないわよ。

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#ファンモン #ファンキーモンキーベイビーズ #遊華俚祭"""

P3 = """OSHINAVIの"本日発売"ピックアップ🎫

『奥華子CONCERT TOUR 2026 -弾き語り-』。
タイトルに掲げるほどの"弾き語り"、これを聴かずに今年は締められないわよ。

9/6〜12/26の全13公演のうち、本日10:00に一般発売なのは8公演。
千葉9/12・愛知9/21・埼玉10/8・福岡10/12
秋田10/30・東京11/26・宮城11/28・神奈川12/12よ。

近くの街が入ってたら、それはもう行きなさいってことだわ。

▼チケット情報はこちら
https://oshinavi.jp

推しの"発売日"見逃さない｜OSHINAVI
#奥華子 #弾き語り"""

posts = [("①スターダム", P1), ("②ファンモン", P2), ("③奥華子", P3)]
ng = 0
for name, b in posts:
    print("--- %s ---" % name)
    print("  字数 %d（目安280〜330）" % len(b))
    if not 280 <= len(b) <= 330:
        print("  ⚠️字数が目安外"); ng += 1
    bad = re.findall(r"。(?=[^\s])", b)
    print("  「。」直後に文が続く箇所: %d" % len(bad))
    if bad:
        ng += 1
    for label, needle in (("冒頭", 'OSHINAVIの"本日発売"ピックアップ🎫'),
                          ("CTA", "▼チケット情報はこちら"),
                          ("URL", "https://oshinavi.jp"),
                          ("署名", '推しの"発売日"見逃さない｜OSHINAVI')):
        if needle not in b:
            print("  ⚠️%s が無い" % label); ng += 1
    tags = re.findall(r"#\S+", b)
    print("  タグ %d個: %s" % (len(tags), " ".join(tags)))
    if not tags:
        ng += 1
    for t in tags:
        if re.search(r"[^0-9A-Za-z぀-ヿ一-鿿＿_#ー]", t):
            print("  ⚠️タグに特殊文字（Xで途切れる恐れ）: %s" % t); ng += 1

# 3本の特徴語の使い回し
words = Counter()
for _, b in posts:
    body = re.sub(r"https?://\S+|#\S+", "", b)
    for w in set(re.findall(r"[ぁ-んァ-ヶ一-龥]{3,}", body)):
        words[w] += 1
dup = [w for w, c in words.items() if c >= 2]
print("\n2本以上に出た語: %s" % ("なし" if not dup else " / ".join(sorted(dup))))
print("=== 引っかかり %d件 ===" % ng)
