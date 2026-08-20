# -*- coding: utf-8 -*-
"""既存の運用を見る：指定ジャンルに入っているアーティスト名を並べる。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from heal_stale_deadlines import load_events  # noqa: E402

with open("index.html", "rb") as f:
    h = f.read().decode("utf-8")
_m, EVENTS = load_events(h)
for g in sys.argv[1].split(","):
    rows = [e for e in EVENTS if e.get("genre") == g]
    print("== %s: %d件" % (g, len(rows)))
    print("   " + " / ".join(e.get("artist", "")[:16] for e in rows[-25:]))
