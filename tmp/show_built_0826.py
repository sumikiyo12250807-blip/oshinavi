# -*- coding: utf-8 -*-
"""ビルド結果を一覧する。締切が近すぎる枠（受付中で4日以内に終わる）を洗い出すのが目的。
feedback_harvest_source_order_and_far_deadline＝締切が遠いものを優先／もうじき終わる枠は載せない。"""
import json
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

TODAY = datetime.date.today()
rows = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "tmp/built_0826.json", encoding="utf-8"))

near, ok = [], []
for e in rows:
    ds = []
    for t in e.get("tickets") or []:
        d = t.get("date")
        if not d:
            continue
        try:
            ds.append((datetime.date.fromisoformat(d) - TODAY).days)
        except ValueError:
            pass
    latest = max(ds) if ds else None
    (ok if (latest is None or latest >= 4) else near).append((e, latest))

print("=== ビルド %d件（締切が4日以上先＝%d件 / 4日以内に全部終わる＝%d件）===" % (len(rows), len(ok), len(near)))
for label, group in (("✅載せる候補", ok), ("⚠️もうじき終わる（載せない）", near)):
    print("")
    print("=" * 68)
    print("%s %d件" % (label, len(group)))
    for e, latest in group:
        print("  id=%-5d %-30s 公演%s 枠%d %s" % (
            e["id"], (e.get("artist") or "")[:30], e.get("date"), len(e.get("tickets") or []),
            ("最終締切まであと%d日" % latest) if latest is not None else "締切不明"))
        for t in e.get("tickets") or []:
            print("        - %s | date=%s | startDate=%s" % (
                t.get("type"), t.get("date"), t.get("startDate")))
