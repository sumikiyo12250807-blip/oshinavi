# -*- coding: utf-8 -*-
"""怪談スイープの候補を build_pia_entries 用の候補JSONに整形する。

  ・既存と名前がぶつかる2件(稲川淳二 b2665530 / 松原タニシ b2668442)は外す＝既存エントリの育成に回す
  ・newid は index.html の最大id+1 から連番
出力: tmp/kaidan_build_cands.json
"""
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"

# build_pia_entries.norm_fw と同じ流儀＝（）／〜～ は意味のある記号なので
# 退避してからNFKCし、あとで戻す（半角チルダに化けるのを防ぐ）
_PROT = {"（": "\u0001", "）": "\u0002", "／": "\u0003", "〜": "\u0004", "～": "\u0005"}


def norm_fw(s):
    for k, v in _PROT.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFKC", s)
    for k, v in _PROT.items():
        s = s.replace(v, k)
    return s

SKIP = {"b2665530", "b2668442"}   # 既存id44 / id958 の育成に回す

h = io.open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", h, re.S).group(1))
nxt = max(e["id"] for e in events) + 1
print("既存最大id =", nxt - 1, "→ 新規は", nxt, "から")

A = json.load(io.open(os.path.join(ROOT, "tmp", "kaidan_A.json"), encoding="utf-8"))
B = json.load(io.open(os.path.join(ROOT, "tmp", "kaidan_B.json"), encoding="utf-8"))

cands = []
for r in sorted(A + B, key=lambda x: x["day"]):
    if r["cd"] in SKIP:
        continue
    name = norm_fw(r["name"]).strip()
    cands.append({"newid": nxt, "artist": name, "urls": [r["url"]]})
    nxt += 1

json.dump(cands, io.open(os.path.join(ROOT, "tmp", "kaidan_build_cands.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("候補 %d件 → tmp/kaidan_build_cands.json" % len(cands))
for c in cands:
    print("  %d  %s" % (c["newid"], c["artist"][:56]))
