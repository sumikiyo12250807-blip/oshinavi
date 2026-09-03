# -*- coding: utf-8 -*-
"""記事の「発売になる公演」の箱に入れる中身を、機械で確定させる。
🚨ここに出た文字列だけを記事に使う（手で書き足さない＝[[feedback_no_fake_info]]）。"""
import json, re, io, datetime

FROM, TO = "2026-09-07", "2026-09-13"
MAIN = [4500, 4489, 4236, 668, 4246]
TILE = [6060, 4103, 4230, 4490, 6141, 2103]   # 参考：後で入れ替え可

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}
WD = "月火水木金土日"


def jp(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return "%d/%d(%s)" % (m, dd, WD[datetime.date(y, m, dd).weekday()])


def week_slots(e):
    out = []
    for t in e.get("tickets", []):
        if t.get("soldout") or t.get("saleEnded"):
            continue
        sd = t.get("startDate") or ""
        if FROM <= sd <= TO and re.search(r"\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売", t.get("type") or ""):
            out.append(t)
    return out


buf = []
for i in MAIN:
    e = by_id.get(i)
    if not e:
        continue
    ss = week_slots(e)
    times = sorted(set(re.search(r"(\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2})発売", t["type"]).group(1)
                       for t in ss if re.search(r"(\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2})発売", t["type"])))
    dates = sorted(set(t.get("startDate") for t in ss))
    buf.append("=" * 68)
    buf.append("■ %s（id%s）" % (e.get("name"), i))
    buf.append("  発売＝%s" % "／".join("%s %s" % (jp(d), t.split()[-1]) for d, t in zip(dates, times)))
    buf.append("  ぴあ＝%s" % ((e.get("links") or {}).get("pia") or ""))
    buf.append("  【発売になる公演】（券種名から機械抽出・この文字列をそのまま使う）")
    for t in ss:
        # 「一般発売（大阪 11/2公演）9/12 10:00発売」から〈県 公演日〉を取る
        m = re.search(r"（(.+?)\s*([\d/〜]+(?:R9年\s*[\d/〜]+)?)公演）", t["type"])
        label = t["type"]
        if m:
            label = "%s %s公演" % (m.group(1), m.group(2))
        kind = t["type"].split("（")[0]
        buf.append("    ・%-28s ／ 券種＝%s" % (label, kind))
    buf.append("  会場（エントリの記録）: %s" % e.get("venue"))
    buf.append("  期間: %s" % e.get("dateLabel"))

io.open("tmp/pickup_boxes_0907.txt", "w", encoding="utf-8").write("\n".join(buf))
print("WROTE tmp/pickup_boxes_0907.txt  MAIN=%d" % len(MAIN))
