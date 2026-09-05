# -*- coding: utf-8 -*-
"""名前タイル12組の「発売日」表記が、現物の枠と合っているかを突き合わせる。

🚨 タイルは「名前＋発売日」だけを出す作りなので、会場や千秋楽が変わっても直す必要はない。
   ただし**発売日が増えた／早まった**ときは直さないと嘘になる
   （2026-09-05 実例＝天満天神繁昌亭に 9/7 発売の枠が増えたのに、タイルは「9/9／9/10／9/11ほか」のまま）。
"""
import json, re, io, datetime

FROM, TO = "2026-09-07", "2026-09-13"
TILES = [6060, 6003, 950, 4228, 4235, 4227, 5993, 6009, 4103, 6141, 4230, 4490]
WD = "月火水木金土日"

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}
sec = io.open("tmp/pickup0906/section.html", encoding="utf-8").read()

tiles = []
for m in re.finditer(r'<span class="pk-o-name">(.*?)</span>\s*<span class="pk-o-when">(.*?)</span>', sec, re.S):
    tiles.append((re.sub(r"<[^>]+>", "", m.group(1)).strip(),
                  re.sub(r"<[^>]+>", "", m.group(2)).strip()))

RE_START = re.compile(r"(\d{1,2})/(\d{1,2})(?:\s*(\d{1,2}:\d{2}))?\s*発売\s*$")


def sale_start(t):
    if t.get("startDate"):
        return t["startDate"]
    m = RE_START.search(t.get("type") or "")
    if m:
        y = 2026 if int(m.group(1)) >= 9 else 2027
        return "%04d-%02d-%02d" % (y, int(m.group(1)), int(m.group(2)))
    return None


def md(iso):
    y, mo, d = (int(x) for x in iso.split("-"))
    return "%d/%d(%s)" % (mo, d, WD[datetime.date(y, mo, d).weekday()])


buf, ng = [], 0
for idx, i in enumerate(TILES):
    e = by_id.get(i)
    nm_art = (e.get("artist") or e.get("name", "")) if e else "(現物に無い)"
    days = sorted({sale_start(t) for t in (e.get("tickets") or []) if sale_start(t) and FROM <= sale_start(t) <= TO}) if e else []
    real = "／".join(md(d) for d in days)
    shown = tiles[idx][1] if idx < len(tiles) else "(タイルが無い)"
    shown_name = tiles[idx][0] if idx < len(tiles) else ""
    # 表記に載っている日付を拾って、現物の日付集合と比べる
    shown_days = set(re.findall(r"(\d{1,2})/(\d{1,2})", shown))
    real_days = set((str(int(d.split("-")[1])), str(int(d.split("-")[2]))) for d in days)
    missing = sorted(real_days - shown_days, key=lambda x: (int(x[0]), int(x[1])))
    extra = sorted(shown_days - real_days, key=lambda x: (int(x[0]), int(x[1])))
    earliest_ok = (not days) or (str(int(days[0].split("-")[1])), str(int(days[0].split("-")[2]))) in shown_days
    mark = "OK  "
    if missing and not re.search(r"ほか", shown):
        mark = "🚨NG"
    elif not earliest_ok:
        mark = "🚨NG"          # いちばん早い発売日が表記に無いのは「ほか」でも許さない
    elif missing:
        mark = "△   "          # 「ほか」で吸収されている
    if mark.startswith("🚨"):
        ng += 1
    buf.append("%s id=%-5s %-30s" % (mark, i, nm_art[:30]))
    buf.append("      タイル表記: %s   （%s）" % (shown, shown_name[:28]))
    buf.append("      現物の発売日: %s" % (real or "(今週は無し)"))
    if missing:
        buf.append("      表記に無い日: %s" % "／".join("%s/%s" % x for x in missing))
    if extra:
        buf.append("      現物に無い日: %s" % "／".join("%s/%s" % x for x in extra))
    buf.append("")

buf.append("要対応: %d件" % ng)
io.open("tmp/tiles_check_0906.txt", "w", encoding="utf-8").write("\n".join(buf))
print("NG=%d -> tmp/tiles_check_0906.txt" % ng)
