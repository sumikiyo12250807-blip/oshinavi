# -*- coding: utf-8 -*-
"""id=611 / 406 をぴあ実ページからゼロ再導出（読むだけ）"""
import sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

TARGETS = [
    (611, "Unlucky Morpheus", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2665502"),
    (406, "RISING SUN ROCK FESTIVAL 2026", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2666420"),
]

for newid, artist, url in TARGETS:
    print("=" * 70)
    print("id=%s %s" % (newid, artist))
    try:
        ent = B.build({"newid": newid, "artist": artist, "urls": [url]})
    except Exception as e:
        print("  ERROR:", type(e).__name__, e); continue
    if not ent:
        print("  → 買える枠ゼロ（None）"); continue
    for k in ("name", "date", "dateLabel", "venue", "prefecture"):
        print("  %-12s %s" % (k, ent.get(k)))
    for t in ent.get("tickets", []):
        print("    - %s | date=%s startDate=%s" % (t.get("type"), t.get("date"), t.get("startDate")))
