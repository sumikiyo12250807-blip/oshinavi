# -*- coding: utf-8 -*-
"""「ここ数日クリックされていない」が本当かを日別に数える。
🚨 推測で答えない。CSVの実測だけを出す（feedback_no_speculation）。
"""
import csv, io, collections

rows = list(csv.DictReader(io.open("tmp/x_content_0907.csv", encoding="utf-8-sig")))

def num(x):
    try:
        return int(str(x).replace(",", "") or 0)
    except ValueError:
        return 0

import datetime

# Date は 'Sun, Sep 6, 2026' 形式。先頭10字で切ると日が欠ける（最初にやらかした）
def parse_day(s):
    s = (s or "").strip()
    try:
        return datetime.datetime.strptime(s, "%a, %b %d, %Y").date().isoformat()
    except ValueError:
        return ""

day = collections.OrderedDict()
for r in rows:
    d = parse_day(r.get("Date"))
    if not d:
        continue
    a = day.setdefault(d, {"n": 0, "imp": 0, "clk": 0, "eng": 0, "rt": 0, "fol": 0, "det": 0})
    a["n"] += 1
    a["imp"] += num(r.get("Impressions"))
    a["clk"] += num(r.get("URL Clicks"))
    a["eng"] += num(r.get("Engagements"))
    a["rt"] += num(r.get("Reposts"))
    a["fol"] += num(r.get("New follows"))
    a["det"] += num(r.get("Detail Expands"))

with io.open("tmp/x_daily_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 日別（新しい順・直近30日）===\n")
    f.write("日付        本数  インプ   URLクリック  CTR     詳細クリック  RT  新規フォロー\n")
    for d in sorted(day, reverse=True)[:30]:
        a = day[d]
        ctr = (a["clk"] / a["imp"] * 100) if a["imp"] else 0
        f.write("%s  %3d  %7d  %6d      %5.2f%%  %6d      %3d  %3d\n"
                % (d, a["n"], a["imp"], a["clk"], ctr, a["det"], a["rt"], a["fol"]))

    f.write("\n=== 週ごとのまとめ ===\n")
    wk = collections.OrderedDict()
    for d in sorted(day):
        import datetime
        try:
            dt = datetime.date.fromisoformat(d)
        except ValueError:
            continue
        k = (dt - datetime.timedelta(days=dt.weekday())).isoformat()
        w = wk.setdefault(k, {"n": 0, "imp": 0, "clk": 0})
        w["n"] += day[d]["n"]
        w["imp"] += day[d]["imp"]
        w["clk"] += day[d]["clk"]
    f.write("週の始まり    本数  インプ    URLクリック  CTR\n")
    for k in sorted(wk):
        w = wk[k]
        ctr = (w["clk"] / w["imp"] * 100) if w["imp"] else 0
        f.write("%s   %3d  %7d   %5d      %5.3f%%\n" % (k, w["n"], w["imp"], w["clk"], ctr))

print("wrote tmp/x_daily_0907.txt / 対象 %d投稿" % len(rows))
