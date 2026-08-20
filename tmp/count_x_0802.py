# -*- coding: utf-8 -*-
"""8/2発売告知X投稿5本の機械チェック：字数・4点セット・語の使い回し。"""
import io
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P1 = """OSHINAVIの"明日発売"ピックアップ🎫
明日8/2(日)0:00発売よ！
THE FACT MUSIC AWARDS EXHIBITION - VISION FESTA(DIVE INTO THE STARS)
ステージをVRで体験する展示。画面越しじゃなく、視界まるごと持っていかれるの。天神開業90周年の記念企画よ。
8/2〜8/30 岩田屋本店 大催事場(福岡・天神)
⚠️8/2のみ時間指定券が必要・8/3以降は予約不要
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#BTS #SEVENTEEN #TOMORROWXTOGETHER #ENHYPEN #BOYNEXTDOOR #VISIONFESTA"""

P2 = """OSHINAVIの"明日発売"ピックアップ🎫
明日8/2(日)10:00発売よ！
山里亮太の140 愛知公演〜逃げ上手の不如帰〜
サブタイトルは「逃げ上手の不如帰」。もう気になって仕方ないでしょ、タイトルで笑わせにくる人の本編が面白くないわけないのよ。この引っかかりの答え合わせは、御園座の客席でしかできないんだから。全席指定4,000円、この値段なら迷う理由がないわ。9月の名古屋、予定空けときなさい。
9/21(月)15:00開場/16:00開演 御園座(愛知・名古屋)
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#山里亮太 #山里亮太の140 #御園座"""

P3 = """OSHINAVIの"明日発売"ピックアップ🎫
明日8/2(日)10:00発売よ！
アインシュタイン結成15周年記念ツアー
15周年だから15ヶ所。「単独シュタイン」と「ゲストシュタイン」の2形式で全国をまわるのよ。河井ゆずる本人も「初めてライブをさせて頂く所もあるので楽しみです」ですって。この回り方は記念の年ならではだわ。
愛知は11/29(日)18:00開演・御園座で「ゲストシュタイン in 名古屋」＝ゲストを迎えたネタとコーナーのライブよ。
明日発売は東京・石川・愛媛・熊本・沖縄(8/29〜11/7)と愛知のぶん。
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#アインシュタイン #ゲストシュタイン #御園座"""

P4 = """OSHINAVIの"明日発売"ピックアップ🎫
明日8/2(日)10:00発売よ！
Omotenashi Stage『18TRIP』-R1ze&Ev3ns-
ゲーム『18TRIP』の舞台化よ。近未来の日本、衰退した「HAMA18区」の観光を立て直す物語なの。朝組「R1ze」と夜組「Ev3ns」の2班制で、それぞれが主役。どっちを観るかじゃないわ、どっちも観たくなるでしょ。
KAAT神奈川芸術劇場ホール 8/25〜8/30／AiiA 2.5 Theater Kobe 9/4〜9/13
全席指定・サイドシート 12,500円(税込)
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#18TRIP #R1ze #Ev3ns"""

P5 = """OSHINAVIの"明日発売"ピックアップ🎫
明日8/2(日)10:00発売よ！
天才ピアニスト×ヨネダ2000 ツーマンライブ「あっちこっちカンパニ〜 愛知公演」
東西の若手女性芸人がガチでぶつかるツーマンなのよ。ますみと竹内知咲、誠と愛——この4人が同じ板に乗るの、想像しただけで口角上がるでしょ。ネタもコーナーも全部載せ、どんな化学反応が起きるか見届けてちょうだい。
11/28(土) 御園座(愛知・名古屋)
https://oshinavi.jp
推しの"発売日"見逃さない｜OSHINAVI
#天才ピアニスト #ヨネダ2000 #あっちこっちカンパニ"""

POSTS = [
    ("1 VISION FESTA", P1),
    ("2 山里亮太の140", P2),
    ("3 アインシュタイン", P3),
    ("4 18TRIP", P4),
    ("5 天才ピアニスト×ヨネダ2000", P5),
]

HEAD = 'OSHINAVIの"明日発売"ピックアップ🎫'
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'
URL = "https://oshinavi.jp"

print("=== 字数と4点セット ===")
ng = 0
for name, p in POSTS:
    n = len(p)
    ok_head = p.startswith(HEAD)
    ok_sign = SIGN in p
    ok_url = URL in p
    ok_tag = "#" in p
    tags = re.findall(r"#\S+", p)
    # URLに ?x= が付いていないか
    bad_url = "oshinavi.jp/?" in p or "?x=" in p
    flag = "OK " if (ok_head and ok_sign and ok_url and ok_tag and not bad_url and 260 <= n <= 340) else "NG "
    if flag == "NG ":
        ng += 1
    print("%s %-28s %3d字  冒頭%s 署名%s URL%s タグ%d個%s" % (
        flag, name, n,
        "○" if ok_head else "×",
        "○" if ok_sign else "×",
        "○" if ok_url else "×",
        len(tags),
        "  ⚠️URLにパラメータ" if bad_url else ""))

print("\n=== 5本横断・特徴語の重複チェック ===")
# 事実側の語・定型を除外して、比喩/動詞の使い回しを見る
STOP = set("""明日 発売 公演 会場 全席 指定 円 税込 開演 開場 御園座 愛知 名古屋 神奈川 福岡 天神
東京 石川 愛媛 熊本 沖縄 兵庫 OSHINAVI ピックアップ 推し 見逃さない""".split())
words = {}
for name, p in POSTS:
    body = p.split("\n")
    body = "\n".join(body[2:-3])  # 見出し/日時/URL/署名/タグを除いた本文コア
    ws = re.findall(r"[ぁ-んァ-ヶ一-龠]{2,}", body)
    for w in set(ws):
        if w in STOP:
            continue
        words.setdefault(w, set()).add(name)

dup = {w: s for w, s in words.items() if len(s) >= 2}
if not dup:
    print("  2本以上に出る語: なし")
else:
    for w in sorted(dup, key=lambda x: -len(dup[x])):
        print("  %-8s %d本: %s" % (w, len(dup[w]), " / ".join(sorted(dup[w]))))

print("\n判定: %s" % ("全項目OK" if ng == 0 else "NG %d本" % ng))
