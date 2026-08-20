# -*- coding: utf-8 -*-
"""8/9 ヒール削除候補18件の素性（名前/会場/公演日/links）を出す。"""
import io
import json
import sys

sys.path.insert(0, "tools")
from check_expired import extract_events_array  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

IDS = [130, 1071, 1644, 1656, 2223, 2340, 2341, 2401, 2415, 2416,
       3137, 3287, 3392, 3432, 3513, 3670, 3872, 3875]

evs = extract_events_array("index.html")
by_id = {e.get("id"): e for e in evs}

for eid in IDS:
    e = by_id.get(eid)
    if not e:
        print("id%d: 見つからない" % eid)
        continue
    links = e.get("links") or {}
    live = {k: v for k, v in links.items() if v}
    print("=" * 78)
    print("id%d %s / %s" % (eid, e.get("artist", ""), e.get("title", "")))
    print("   会場=%s 公演日=%s ジャンル=%s" % (e.get("venue", ""), e.get("date", ""), e.get("genre", "")))
    print("   links(値あり)=%s" % json.dumps(live, ensure_ascii=False))
    for t in (e.get("tickets") or []):
        print("   枠: %s | date=%s start=%s soldout=%s"
              % (t.get("type", ""), t.get("date"), t.get("startDate"), t.get("soldout")))
