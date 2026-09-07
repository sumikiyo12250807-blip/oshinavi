# -*- coding: utf-8 -*-
"""週ごとに「まとめ／主役」の比率とCTRを出す。
インプが増えたのにクリックが落ちた原因が、型の構成の変化で説明できるかを見る。
"""
import csv, io, collections, datetime, re

rows = list(csv.DictReader(io.open("tmp/x_content_0907.csv", encoding="utf-8-sig")))


def num(x):
    try:
        return int(str(x).replace(",", "") or 0)
    except ValueError:
        return 0


def parse_day(s):
    try:
        return datetime.datetime.strptime((s or "").strip(), "%a, %b %d, %Y").date()
    except ValueError:
        return None


def kind(t):
    """まとめ＝ジャンルの束を並べる回。主役＝1組を立てる回。
    CSVの本文は204字で切れるので、冒頭だけで判定できる語を使う。"""
    t = t or ""
    if re.search(r"のまとめ|まとめよ|まとめて並べ|【\d{1,2}/\d{1,2}\(.\)発売】.*\n.*\n.*\n", t):
        return "まとめ"
    return "主役ほか"


wk = collections.OrderedDict()
for r in rows:
    d = parse_day(r.get("Date"))
    if not d:
        continue
    k = (d - datetime.timedelta(days=d.weekday())).isoformat()
    kd = kind(r.get("Post text"))
    a = wk.setdefault(k, collections.OrderedDict())
    b = a.setdefault(kd, {"n": 0, "imp": 0, "clk": 0})
    b["n"] += 1
    b["imp"] += num(r.get("Impressions"))
    b["clk"] += num(r.get("URL Clicks"))

with io.open("tmp/x_type_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 週 × 型（まとめ／主役ほか）===\n")
    f.write("週の始まり    型        本数  インプ    クリック  CTR\n")
    for k in sorted(wk):
        for kd in ("まとめ", "主役ほか"):
            b = wk[k].get(kd)
            if not b:
                continue
            ctr = (b["clk"] / b["imp"] * 100) if b["imp"] else 0
            f.write("%s   %-8s  %3d  %7d   %5d    %6.3f%%\n" % (k, kd, b["n"], b["imp"], b["clk"], ctr))
        f.write("\n")
print("wrote tmp/x_type_0907.txt")
