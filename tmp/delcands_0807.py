# -*- coding: utf-8 -*-
"""8/7 朝の削除候補12件の確認用URLを index.html から機械抽出する（捏造禁止）。"""
import io
import json
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

IDS = [1148, 2703, 750, 925, 1094, 1456, 2232, 2850, 2873, 2988, 3482, 3781]
P = r"C:\Users\user\oshinavi\index.html"
shutil.copyfile(P, r"C:\Users\user\oshinavi\index.html.bak_0807_morning_delete")

sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402

evs = extract_events_array(P)
by = {e["id"]: e for e in evs}

for eid in IDS:
    e = by.get(eid)
    if not e:
        print("id=%d 見つからない" % eid)
        continue
    lk = e.get("links") or {}
    urls = [(k, v) for k, v in lk.items() if v and k != "amazon"]
    print("id=%d | %s | %s | %s公演" % (eid, e["name"], e.get("prefecture", ""), e["date"]))
    for k, v in urls:
        print("    %s: %s" % (k, v))
    for t in e.get("tickets", []):
        if t.get("url"):
            print("    枠url: %s" % t["url"])
