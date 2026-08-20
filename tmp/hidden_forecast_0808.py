# -*- coding: utf-8 -*-
"""昼のヒールをやらないと何枠が画面から消えるかを数える（2026-08-08）。
index.html の非表示判定 (!startDate || startDate<=today) && date<today を機械で当てる。
"""
import collections
import datetime
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402


def d(s):
    try:
        return datetime.date(*map(int, s.split("-")))
    except Exception:
        return None


evs = extract_events_array(r"C:\Users\user\oshinavi\index.html")

for TARGET in ("2026-08-08", "2026-08-09", "2026-08-10"):
    t = d(TARGET)
    hidden, ents = 0, set()
    for e in evs:
        for x in e.get("tickets") or []:
            sd, dt = d(x.get("startDate") or ""), d(x.get("date") or "")
            # 「本日発売」形＝startDate==date（締切が未取込）
            if sd and dt and sd == dt == t:
                hidden += 1
                ents.add(e["id"])
    print("%s 発売で締切が未取込の枠: %d枠 / %dエントリ" % (TARGET, hidden, len(ents)))

# 全体で今この瞬間「隠れ枠」になっているもの（今日より前に発売済みで締切未取込）
today = datetime.date(2026, 8, 8)
now_hidden = []
for e in evs:
    for x in e.get("tickets") or []:
        sd, dt = d(x.get("startDate") or ""), d(x.get("date") or "")
        if sd and dt and sd == dt and dt < today:
            now_hidden.append((e["id"], e.get("artist"), x.get("type")))
print("\n今すでに隠れている枠: %d枠" % len(now_hidden))
for r in now_hidden[:10]:
    print("   id%-5d %s ／ %s" % r)

# 8/8発売のうち、いちばん大きいエントリを例示
ex = collections.Counter()
for e in evs:
    n = sum(1 for x in (e.get("tickets") or [])
            if d(x.get("startDate") or "") == d(x.get("date") or "") == d("2026-08-08"))
    if n:
        ex[(e["id"], e.get("artist"))] = n
print("\n8/8発売で消える枠が多いエントリ 上位10:")
for (eid, art), n in ex.most_common(10):
    print("   id%-5d %-34s %d枠" % (eid, (art or "")[:34], n))
