# -*- coding: utf-8 -*-
"""ぴあの個別イベントページが今どれくらいで返ってくるかを1件だけ測る。
ヒールが遅い原因が「ぴあ側の応答」なのかを切り分けるための最小実験。"""
import urllib.request, time, sys, re

U = "https://t.pia.jp/pia/event/event.do?eventCd=2634279"   # 5516 Golden Moon Concert
t0 = time.time()
try:
    req = urllib.request.Request(U, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "replace")
        code = r.status
    dt = time.time() - t0
    print("HTTP=%s  bytes=%d  seconds=%.1f" % (code, len(body), dt))
    # 混雑ページ／エラーページの見分け
    for mark, label in (("sorry", "SORRY_PAGE"), ("ただいまアクセスが集中", "CONGESTED"),
                        ("見つかりませんでした", "NOT_FOUND"), ("__status", "HAS_TICKET_CARDS")):
        print("  %-18s %s" % (label, mark in body))
    n = len(re.findall(r"__status", body))
    print("  status_blocks=%d" % n)
except Exception as ex:
    print("ERROR after %.1fs: %s" % (time.time() - t0, ex))
