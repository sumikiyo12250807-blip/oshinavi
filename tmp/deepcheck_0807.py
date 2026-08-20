# -*- coding: utf-8 -*-
"""新着50件の目視で引っかかった所をぴあ実ページで裏取りする（2026-08-07）。
  3914 大河ドラマ「豊臣兄弟!」＝「プレイガイド最速先行」が締切違いで2枠＝区別がつかない
  3925 Mozu ミニチュア展 岡山＝ぴあ実名は「一般発売＜当日券＞」なのに登録は「一般発売」
  3892 夜の本気ダンス＝15会場ツアーなのに一般発売が4枠しかない（取りこぼし疑い）
  3891 THE MODS＝2会場だけ。ツアーの他会場は？
"""
import io
import json
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGETS = [
    (3914, "大河ドラマ「豊臣兄弟!」コンサート", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670243"),
    (3892, "夜の本気ダンス（bundle）", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669055"),
    (3891, "THE MODS", "https://t.pia.jp/pia/event/event.do?eventCd=2618896"),
]

for i, (eid, label, url) in enumerate(TARGETS):
    if i:
        time.sleep(6)
    r = subprocess.run([sys.executable, "tools/pia_tickets.py", url, "--json", "--all"], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    print("=" * 78)
    print("id=%d %s" % (eid, label))
    try:
        rows = json.loads(txt)
    except Exception as e:
        print("  解析失敗 %s\n%s" % (e, txt[:300]))
        continue
    for x in rows:
        pr = x["perfdate"] + ("〜" + x["perf_end"] if x.get("perf_end") and x["perf_end"] != x["perfdate"] else "")
        print("  [%s] %s %s %s | %s | %s" % (x["state"], pr, x["pref"], x["venue"][:24], x["title"][:60], x["when"]))
