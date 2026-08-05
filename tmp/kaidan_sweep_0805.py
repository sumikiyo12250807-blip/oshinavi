# -*- coding: utf-8 -*-
"""怪談ジャンルの総ざらい（2026-08-05 ユーザー指示「怪談を取りに行って」）。

pia_kw_search.py を語ごとに回して tmp/kw_kaidan/<語>.txt に落とす。
ジャンル語（怪談・心霊…）＋怪談師/怪談YouTuberの名前で引く。
ぴあ429を避けるため語の間に3秒空ける（[[reference_pia_rate_limit_429]]）。
"""
import io
import os
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = r"C:\Users\user\oshinavi"
OUT = os.path.join(ROOT, "tmp", "kw_kaidan")
os.makedirs(OUT, exist_ok=True)

WORDS = [
    # ジャンル語
    "心霊", "都市伝説", "オカルト", "怖い話", "百物語", "怪異", "ホラー", "実話怪談",
    # 怪談師・怪談YouTuber（ユーザー指摘の「YouTuberもイベントいっぱい」枠）
    "島田秀平", "好井まさお", "ナナフシギ", "田中俊行", "松原タニシ", "北野誠",
    "三木大雲", "夜馬裕", "匠平", "伊山亮吉", "チビル松村", "深津さくら",
    "シークエンスはやとも", "ゾゾゾ", "牛抱せん夏", "村上ロック", "ぁみ",
    "怪談グランプリ", "怪談最恐戦", "怪談ライブ",
]

for i, w in enumerate(WORDS, 1):
    dst = os.path.join(OUT, "%s.txt" % w)
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "pia_kw_search.py"), w, "--out", dst],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    tail = (r.stdout or r.stderr or "").strip().splitlines()
    print("[%2d/%d] %-12s %s" % (i, len(WORDS), w, tail[-1] if tail else "(出力なし)"))
    if i < len(WORDS):
        time.sleep(3)
print("\n完了 →", OUT)
