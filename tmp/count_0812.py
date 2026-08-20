#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""index.html のエントリ件数と genre:new の件数を数える。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.stdout.reconfigure(encoding="utf-8")
from heal_stale_deadlines import load_events  # noqa: E402

with open("index.html", "rb") as f:
    h = f.read().decode("utf-8")
_m, EVENTS = load_events(h)
new = [e for e in EVENTS if e.get("genre") == "new"]
print(f"全{len(EVENTS)}件 / genre:new {len(new)}件")
if new:
    ids = [e.get("id") for e in new]
    print(f"new id: {min(ids)}-{max(ids)}")
