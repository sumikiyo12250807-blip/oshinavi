# -*- coding: utf-8 -*-
"""build が skip(売切) にした9件を、ぴあの実ページで1件ずつ確かめる。

「全0券種」は本当の売切とは限らない＝w.pia.jp直販形式の罠がある（[[feedback_wpia_direct_sale_trap]]）。
終了枠すら1枚も無いなら形式違いを疑う。--all 相当で終了枠も数える。
"""
import io
import json
import os
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"

SKIP_IDS = [3787, 3788, 3791, 3792, 3795, 3796, 3799, 3800, 3803]
cands = {c["newid"]: c for c in json.load(
    io.open(os.path.join(ROOT, "tmp", "kaidan_build_cands.json"), encoding="utf-8"))}

for i, nid in enumerate(SKIP_IDS, 1):
    c = cands[nid]
    print("=" * 78)
    print("[%d/%d] id%d %s" % (i, len(SKIP_IDS), nid, c["artist"][:52]))
    print("   ", c["urls"][0])
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, "tools", "pia_tickets.py"), c["urls"][0], "--all"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    body = (r.stdout or "").splitlines()
    for ln in body[1:]:          # 1行目のURLは省く
        print("   ", ln)
    if i < len(SKIP_IDS):
        time.sleep(2)
