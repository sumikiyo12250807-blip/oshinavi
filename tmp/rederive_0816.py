# -*- coding: utf-8 -*-
"""id=300 / 3834 をぴあ実ページからゼロ再導出して、date(千秋楽)・dateLabel・venue・prefecture の
現状と機械導出値を並べる（手直しの判断材料。書き込みはしない）"""
import sys, json, io
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

TARGETS = [
    (300, "メインランドジャパン ファンタジースペシャル ブロードウェイミュージカル『ピーター・パン』",
     "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2665822"),
    (3834, "雷獣チャンネル THE LIVE「PLAY」",
     "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670291"),
]

for newid, artist, url in TARGETS:
    print("=" * 70)
    print("id=%s %s" % (newid, artist))
    try:
        ent = B.build({"newid": newid, "artist": artist, "urls": [url]})
    except Exception as e:
        print("  ERROR:", type(e).__name__, e)
        continue
    if not ent:
        print("  → 買える枠ゼロ（None）")
        continue
    for k in ("name", "date", "dateLabel", "venue", "prefecture"):
        print("  %-12s %s" % (k, ent.get(k)))
    print("  tickets:")
    for t in ent.get("tickets", []):
        print("    - %s | date=%s startDate=%s" % (t.get("type"), t.get("date"), t.get("startDate")))
