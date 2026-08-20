# -*- coding: utf-8 -*-
"""8/9・8/10発売の枠を抜く＝旅行中に出す投稿の候補出し（2026-08-07夜）。"""
import collections
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402

STRONG = ["jpop", "rock", "idol", "anime", "kpop", "vtuber", "youtuber", "seiyuu", "hiphop", "2.5ji"]
evs = extract_events_array(r"C:\Users\user\oshinavi\index.html")

for TARGET in ("2026-08-09", "2026-08-10"):
    rows = []
    for e in evs:
        hit = [t for t in (e.get("tickets") or []) if t.get("startDate") == TARGET]
        if hit:
            rows.append((e, hit))
    print("=" * 74)
    print("### %s 発売開始 %d件 / %s" % (TARGET, len(rows),
          dict(collections.Counter(e.get("genre") for e, _ in rows).most_common())))
    strong = [(e, h) for e, h in rows if e.get("genre") in STRONG]
    for e, hit in strong:
        print("  id%-5d [%s] %s" % (e["id"], e.get("genre"), e.get("artist")))
        print("        %s ／ %s ／ 千秋楽 %s" % (e.get("prefecture"), (e.get("venue") or "")[:44], e.get("date")))
        for t in hit[:4]:
            print("        枠: %s" % t.get("type"))
        if len(hit) > 4:
            print("        …ほか%d枠" % (len(hit) - 4))
