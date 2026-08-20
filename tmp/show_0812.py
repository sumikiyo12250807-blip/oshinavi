#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""指定idのエントリをそのままJSONで出す。"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
sys.stdout.reconfigure(encoding="utf-8")
from heal_stale_deadlines import load_events  # noqa: E402

with open("index.html", "rb") as f:
    h = f.read().decode("utf-8")
_m, EVENTS = load_events(h)
ids = [int(x) for x in sys.argv[1].split(",")]
for e in EVENTS:
    if e.get("id") in ids:
        print(json.dumps(e, ensure_ascii=False, indent=2))
