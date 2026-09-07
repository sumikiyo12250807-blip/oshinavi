# -*- coding: utf-8 -*-
"""「クリックが落ちた」を、跳ねた1本を外して検算する。
🚨 外れ値1本で群が持ち上がる／落ちて見えるので、全体と外れ値を外した後を必ず並べる
   （2026-08-31に同じ罠を1日で2回踏んでいる）。
"""
import csv, io, collections, datetime

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


wk = collections.OrderedDict()
for r in rows:
    d = parse_day(r.get("Date"))
    if not d:
        continue
    k = (d - datetime.timedelta(days=d.weekday())).isoformat()
    wk.setdefault(k, []).append((num(r.get("URL Clicks")), num(r.get("Impressions")),
                                 (r.get("Post text") or "")[:34]))

with io.open("tmp/x_outlier_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 週ごと：全体と「クリック最多の1本を外した後」===\n")
    f.write("週の始まり    本数  インプ    クリック  CTR      ｜外れ値1本を外すと クリック  CTR      ｜外した1本\n")
    for k in sorted(wk)[-8:]:
        v = sorted(wk[k], reverse=True)
        clk = sum(x[0] for x in v)
        imp = sum(x[1] for x in v)
        ctr = (clk / imp * 100) if imp else 0
        rest = v[1:]
        rclk = sum(x[0] for x in rest)
        rimp = sum(x[1] for x in rest)
        rctr = (rclk / rimp * 100) if rimp else 0
        top = v[0]
        f.write("%s   %3d  %7d   %5d   %6.3f%%  ｜ %5d   %6.3f%%  ｜ clk%d %s\n"
                % (k, len(v), imp, clk, ctr, rclk, rctr, top[0], top[2].replace("\n", " ")[:30]))

    f.write("\n=== 1本あたりの平均（週ごと）===\n")
    f.write("週の始まり    1本あたりインプ  1本あたりクリック\n")
    for k in sorted(wk)[-8:]:
        v = wk[k]
        f.write("%s   %8.0f         %5.2f\n"
                % (k, sum(x[1] for x in v) / len(v), sum(x[0] for x in v) / len(v)))
print("wrote tmp/x_outlier_0907.txt")
