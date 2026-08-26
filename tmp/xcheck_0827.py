# -*- coding: utf-8 -*-
"""X投稿の機械検品（2026-08-26 改訂版）。

🚨字数のルールが変わった＝250〜330の**上限は外れた**（ユーザー 2026-08-26
「文字数は増えても大丈夫だから、簡素な文章じゃ無く」）。350〜500字を目安に厚みを持たせる。
ここでは「250字未満＝簡素すぎ」だけを警告する。

🚨曜日の照合は「8/27(木)」形と「8月27日(木)」形の**両方**を見る（前は前者だけだった）。
"""
import re
import io
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

posts = io.open("tmp/xposts_0827.txt", encoding="utf-8").read().split("\n---\n")
W = "月火水木金土日"
YEAR = 2026
ok_all = True
for i, p in enumerate(posts, 1):
    p = p.strip("\n")
    n = len(p)
    issues = []
    if n < 250:
        issues.append("字数 %d（250未満＝簡素すぎ）" % n)
    for m in re.finditer(r"。(?!$)", p):
        nxt = p[m.end():m.end() + 1]
        if nxt and nxt != "\n":
            issues.append("「。」の後が改行でない: …%s" % p[max(0, m.start() - 12):m.end() + 6].replace("\n", "⏎"))
    if "▼チケット情報はこちら" not in p:
        issues.append("CTAが無い")
    if "#OSHINAVI" not in p:
        issues.append("署名タグが無い")
    if not re.search(r"(?<!/)oshinavi\.jp", p):
        issues.append("oshinavi.jp が無い")
    if re.search(r"oshinavi\.jp[/?]", p):
        issues.append("URLに余計な文字が付いている")
    if re.search(r"\d+\s*(件|本)(も|の公演|あ)", p):
        issues.append("件数を書いている疑い（feedback_x_no_counts_oshi_first）")
    # 曜日照合（2形式）
    for mo, d, w in re.findall(r"(\d{1,2})/(\d{1,2})\((.)\)", p) + \
                    re.findall(r"(\d{1,2})月(\d{1,2})日\((.)\)", p):
        try:
            real = W[datetime.date(YEAR, int(mo), int(d)).weekday()]
        except ValueError:
            issues.append("日付が不正: %s/%s" % (mo, d))
            continue
        if real != w:
            issues.append("曜日ちがい %s/%s は(%s)なのに(%s)と書いてある" % (mo, d, real, w))
    print("【%d本目】%d文字  %s" % (i, n, "OK" if not issues else "🚨"))
    for x in issues:
        print("    - %s" % x)
        ok_all = False

print("")
print("総合:", "OK" if ok_all else "🚨要修正")
