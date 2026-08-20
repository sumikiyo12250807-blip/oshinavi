# -*- coding: utf-8 -*-
"""昼ヒールの削除候補3件を e+ で裏取りする（ぴあ0枠は削除理由にならない）。"""
import io
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CANDS = [
    (3319, "関根勤チャンネル トークライブ2026", "関根勤"),
    (3380, "ヤーレンズと太福の演芸会", "ヤーレンズ"),
    (3876, "平成中村座 十月大歌舞伎", "平成中村座"),
    (3876, "平成中村座 十月大歌舞伎（別語）", "十月大歌舞伎"),
]

for i, (eid, name, kw) in enumerate(CANDS):
    if i:
        time.sleep(4)
    r = subprocess.run([sys.executable, "tmp/eplus_search2_0803.py", kw], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    lines = [ln for ln in txt.splitlines() if ln.strip() and not ln.startswith("len=")]
    print("=" * 76)
    print("id%d %s ／ e+検索語「%s」" % (eid, name, kw))
    for ln in lines[:14]:
        print("   " + ln)
