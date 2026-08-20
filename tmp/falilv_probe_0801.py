# -*- coding: utf-8 -*-
"""ベガスの各eventCdの券種を pia_tickets.py で順に取る（429回避で間隔を空ける）"""
import io
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CDS = [
    ("2627622", "11/1 仙台Rensa(登録済id2776)"),
    ("2627049", "11/13 KYOTO MUSE"),
    ("2628029", "11/19 ダイアモンドホール(愛知)"),
    ("2630548", "11/27 Zepp Haneda(東京)"),
    ("2630358", "12/3 DRUM LOGOS(福岡)"),
    ("2612152", "8/28 NIIGATA LOTS(新潟)"),
    ("2611889", "8/9 仙台Rensa"),
    ("2611992", "9/26 KBSホール(京都)"),
]

for cd, label in CDS:
    print("=" * 70)
    print("### %s  eventCd=%s" % (label, cd))
    r = subprocess.run(
        [sys.executable, "tools/pia_tickets.py", cd, "--all"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(r.stdout.strip())
    if r.returncode != 0:
        print("!! exit=%d %s" % (r.returncode, (r.stderr or "").strip()[:200]))
    time.sleep(4)
