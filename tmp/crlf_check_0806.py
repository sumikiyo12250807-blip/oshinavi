# -*- coding: utf-8 -*-
"""index.html の改行コードと件数を確認する。"""
import json, re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
b = open("index.html", "rb").read()
crlf, lf = b.count(b"\r\n"), b.count(b"\n")
print("CRLF %d / 単独LF %d" % (crlf, lf - crlf))
src = b.decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))
print("エントリ %d件" % len(data))
gone = [i for i in (194, 705, 856, 880, 1123) if any(e["id"] == i for e in data)]
print("残ってしまったid:", gone or "なし")
print("genre:new プール %d件" % sum(1 for e in data if e.get("genre") == "new"))
