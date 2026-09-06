# -*- coding: utf-8 -*-
"""X投稿の機械検品（台本 X_SCRIPT.md の決まりを機械で当てられる分だけ）。"""
import re
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

txt = open("tmp/x_posts_0906.txt", encoding="utf-8").read()
posts = re.split(r"=====POST\d+=====\n", txt)[1:]

BAN = ["生で浴びる", "あんた", "両方おさえる", "両方押さえる", "https://oshinavi.jp",
       "&amp;", "&gt;", "&lt;"]
WD = "月火水木金土日"
ng = 0

for i, p in enumerate(posts, 1):
    p = p.rstrip("\n")
    errs = []

    # 1行目＝見出し
    head = p.splitlines()[0]
    if not (head.startswith('OSHINAVIの"') and head.endswith("ピックアップ🎫")):
        errs.append("見出しの形が違う: %s" % head)

    # 「。」の直後は改行（例外＝モーニング娘。／文中の公演名の「。～」）
    for mm in re.finditer(r"。(?!\n)(.)", p):
        ctx = p[max(0, mm.start() - 12):mm.start() + 3].replace("\n", "⏎")
        if "モーニング娘。" in p[max(0, mm.start() - 8):mm.start() + 1]:
            continue
        if "武満徹。" in p[max(0, mm.start() - 5):mm.start() + 1]:
            continue
        errs.append("「。」のあとが改行でない: …%s…" % ctx)

    # CTA と素のURL
    if "▼チケット情報はこちら" not in p:
        errs.append("CTA「▼チケット情報はこちら」が無い")
    if "oshinavi.jp" not in p:
        errs.append("oshinavi.jp が無い")
    if re.search(r"https?://oshinavi", p) or re.search(r"oshinavi\.jp\?", p):
        errs.append("URLに http:// か ?x= が付いている")

    # タグ
    if "#OSHINAVI" not in p or "#チケット" not in p:
        errs.append("タグが足りない")

    # 封印
    for b in BAN:
        if b in p:
            errs.append("禁止語「%s」" % b)

    # 件数の実数（「明日37件発売」の類）
    for mm in re.finditer(r"(明日|今日)\D{0,6}(\d+)件", p):
        errs.append("件数の実数: %s" % mm.group(0))

    # ぴあ等の直リンク
    if re.search(r"(pia\.jp|eplus\.jp|l-tike|rakuten)", p):
        errs.append("外部の売り場への直リンク/言及")

    # 曜日をカレンダーと照合
    for mm in re.finditer(r"(\d{1,2})/(\d{1,2})\((.)\)", p):
        mo, dd, w = int(mm.group(1)), int(mm.group(2)), mm.group(3)
        year = 2026
        try:
            d = datetime.date(year, mo, dd)
        except ValueError:
            errs.append("ありえない日付: %s" % mm.group(0))
            continue
        if WD[d.weekday()] != w:
            errs.append("曜日が違う: %s は %s曜" % (mm.group(0), WD[d.weekday()]))

    print("--- POST%d  %d字 ---" % (i, len(p)))
    if errs:
        ng += len(errs)
        for e in errs:
            print("   🚨 %s" % e)
    else:
        print("   ✅ 問題なし")

print("")
print("=== 8本中の指摘 %d件 ===" % ng)
