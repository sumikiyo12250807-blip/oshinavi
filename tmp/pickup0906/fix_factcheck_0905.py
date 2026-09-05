# -*- coding: utf-8 -*-
"""独立ファクトチェックの指摘を draft.md と section.html に反映する。

🚨 直すのは「出典で裏が取れないこと」と「読者が数を誤解すること」だけ。
   文体は変えない（Fableが書いた形を保つ）。
"""
import io, sys

FIX = [
    # ── ① MONO NO AWARE 深掘り：今週発売でない5会場を落とす（盛岡/仙台/広島/岡山/高松）
    ("会場のほうも、磔磔、Live House Anima、神戸VARIT.、NEVERLAND、LIVE HOUSE Hearts、千葉LOOK、Spotify O-EAST、Thunder Snake 厚木、the five morioka、仙台 darwin、yanagase ants、静岡UMBER、名古屋クラブクアトロ、四日市CLUB ROOTS、DIME、IMAGE、セカンド・クラッチ——街ごとの箱の名前を並べただけで、こうなるの。",
     "会場のほうも、磔磔、Live House Anima、NEVERLAND、神戸VARIT.、Spotify O-EAST、千葉LOOK、LIVE HOUSE Hearts、Thunder Snake 厚木、yanagase ants、静岡UMBER、名古屋クラブクアトロ、四日市CLUB ROOTS——街ごとの箱の名前を並べただけで、こうなるの。"),

    # ── ② リード：ASKAは年内15公演ある。「年内に訪ねる3つの街」は誤り
    ("ASKAが年内に訪ねる3つの街",
     "ASKAの愛知・石川・長野"),

    # ── ③ ASKA本文：同じ理由。年内は他にもある
    ("今回の枠は11月から12月の年内ぶんだから、年の暮れのASKAをどこで聴くか、ここで決まるのよ。",
     "今回出るのは、11月から12月にかけての3公演よ。"),

    # ── ④ 佐藤竹善：「ソロ活動を始めたのは1994年」は出典に無い
    ("ソロ活動を始めたのは1994年で、第1作は1995年1月14日のカバーアルバム『CORNERSTONES』。",
     "ソロの第1作は、1995年1月14日のカバーアルバム『CORNERSTONES』よ。"),

    # ── ⑦ スカパラ：「8人体制で初めてのホールツアー」は公式に記載が無い（断定を外す）
    ("まず押さえておきたいのは、これが8人体制になって初めてのホールツアーだってことよ。",
     "いまのスカパラは8人よ。"),
    ("その8人でホールを回る最初のツアーが、これなの。",
     "その8人でホールを回るツアーが、これなの。"),
    ("体制が変わった最初のホールツアーに、「A Whole New Paradise」という名前をつけてきたのね。",
     "体制が変わってからのホールツアーに、「A Whole New Paradise」という名前をつけてきたのね。"),
    ("新しい8人を最初に見るなら、この4つの街のどれかからよ。",
     "新しい8人を見るなら、この4つの街のどれかからよ。"),

    # ── ⑧ 佐藤竹善：ジャズトリオの帯同が確認できるのは11/25東京と12/1大阪の2公演だけ
    ("佐藤竹善がジャズトリオを連れて12/26の小樽まで回る『Your Christmas Night』",
     "佐藤竹善の『Your Christmas Night』が12/26の小樽まで続くこと"),
    ("ジャズトリオを連れて、クリスマスの夜を街から街へ回る企画って、まさにこの言葉そのものだと思うの。",
     "クリスマスの夜を街から街へ回る企画って、まさにこの言葉そのものだと思うの。"),

    # ── ⑩ 公式のツアー期間は2026/11/2〜2027/3/14＝4か月半
    ("MONO NO AWAREがアルバムとまったく同じ名前で4か月の旅に出る話",
     "MONO NO AWAREがアルバムとまったく同じ名前で4か月半の旅に出る話"),

    # ── ⑪「音楽旅行」は出典に無い語。公式のテーマは「旅行」まで
    ("公式が掲げるテーマは「旅行」——言い換えれば「音楽旅行」。",
     "公式が掲げるテーマは「旅行」よ。"),
    ("「音楽旅行」という言葉を、ほんとうに旅の形で出してきたバンドだわ。",
     "「旅行」という言葉を、ほんとうに旅の形で出してきたバンドだわ。"),
    ("公式が掲げたテーマは「旅行」。\n言い換えれば「音楽旅行」なの。\n",
     "公式が掲げたテーマは「旅行」なの。\n"),
    ("「音楽旅行」という言葉を、これだけ文字どおりに形にしたツアーだわ。",
     "「旅行」という言葉を、これだけ文字どおりに形にしたツアーだわ。"),

    # ── ⑫ 湖月わたる：スペシャルゲストが別にいるので「出演は」と書き切らない
    ("構成・演出は荻田浩一、出演は湖月わたるに彩凪翔、朴璐美。",
     "構成・演出は荻田浩一、出演に湖月わたる、彩凪翔、朴璐美。"),
]

# HTML だけの直し
FIX_HTML = [
    # ⑤ 「。」のあとに <br> が無い箇所（draftでは改行している）
    ("幸福感がある」\nジャズトリオを連れて、", "幸福感がある」<br>\nクリスマスの夜を街から街へ回る"),
    ("幸福感がある」ジャズトリオを連れて、", "幸福感がある」<br>クリスマスの夜を街から街へ回る"),
    # ⑥ ボタンの文言
    (">閉じるを閉じる<", ">東京スカパラダイスオーケストラを閉じる<"),
]


def apply(path, rules):
    s = io.open(path, encoding="utf-8").read()
    hit, miss = [], []
    for a, b in rules:
        if a in s:
            s = s.replace(a, b)
            hit.append(a[:40])
        else:
            miss.append(a[:40])
    io.open(path, "w", encoding="utf-8", newline="").write(s)
    return hit, miss


buf = []
for path, rules in (("tmp/pickup0906/draft.md", FIX),
                    ("tmp/pickup0906/section.html", FIX + FIX_HTML)):
    hit, miss = apply(path, rules)
    buf.append("■ %s   直した %d / 見つからなかった %d" % (path, len(hit), len(miss)))
    for m in miss:
        buf.append("    ⚠️見つからない: %s…" % m)
    buf.append("")

io.open("tmp/pickup0906/fix_factcheck_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("\n".join(x for x in buf if "⚠️" in x or x.startswith("■")))
