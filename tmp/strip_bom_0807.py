# -*- coding: utf-8 -*-
"""PowerShellの > で付いたUTF-8 BOMを剥がしてJSONとして読めるようにする。"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = r"C:\Users\user\oshinavi\tmp\built_0807.json"
raw = open(P, "rb").read()
if raw.startswith(b"\xef\xbb\xbf"):
    raw = raw[3:]
    open(P, "wb").write(raw)
    print("BOMを剥がした")
data = json.loads(raw.decode("utf-8"))
print("エントリ %d件 / id %d..%d" % (len(data), data[0]["id"], data[-1]["id"]))
