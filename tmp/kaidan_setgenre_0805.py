# -*- coding: utf-8 -*-
"""投入前に、構築した14件の下書きジャンル(_genre/_extraGenres)を怪談用に当てる。

ぴあには「怪談」カテゴリが無いので自動では付かない（下書きは engeki/art に落ちる）。
新ジャンル kaidan は今日OSHINAVIに新設したので、ここで手当てする。
落語・展示は「元のジャンルに残して怪談からも辿れる」両方方式（[[feedback_genre_both_when_unclear]]）。
"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
P = r"C:\Users\user\oshinavi\tmp\kaidan_built.json"

PLAN = {
    3781: ("kaidan", []),            # 島田秀平とカイダンさん!
    3782: ("kaidan", []),            # ぁみの全国怪談夜会ツアー
    3783: ("kaidan", []),            # 北こわ ハロウィンSP超怪談
    3784: ("kaidan", []),            # 村上ロック 秋の怪談
    3785: ("kaidan", []),            # 島田秀平×三上丈晴 オカルトトークin岸和田
    3786: ("classic", []),           # ウエンツ瑛士＝ハロウィン企画だが中身はクラシック＝据え置き
    3789: ("kaidan", ["engeki"]),    # 小泉八雲 朗読のしらべ＝怪談の朗読劇
    3790: ("kaidan", []),            # 松原タニシ 事故物件本のトーク＆サイン会
    3793: ("owarai", []),            # 北野誠と観る上方落語＝怪談ではない＝据え置き
    3794: ("kaidan", []),            # 怪談五人羽織
    3797: ("art", ["kaidan"]),       # ホラーにふれる展＝展示
    3798: ("art", ["kaidan"]),       # 東京ホラー特区＝展示イベント
    3801: ("kaidan", []),            # 三木大雲のポジティ部ラジオ（⚠️中身はポジティブ話・主役で読んだ）
    3802: ("owarai", ["kaidan"]),    # 春風亭枝次 怪談『乳房榎』＝落語の怪談噺
}

d = json.load(io.open(P, encoding="utf-8-sig"))
for e in d:
    if e["id"] in PLAN:
        g, ex = PLAN[e["id"]]
        old = (e.get("_genre"), e.get("_extraGenres"))
        e["_genre"] = g
        e["_extraGenres"] = ex
        print("id%d %s%s → %s%s  | %s" % (
            e["id"], old[0], ("+" + ",".join(old[1]) if old[1] else ""),
            g, ("+" + ",".join(ex) if ex else ""), e["artist"][:40]))
json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n→ %s を更新（genreは全件 new のまま）" % P)
