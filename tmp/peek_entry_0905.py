# -*- coding: utf-8 -*-
"""指定idのエントリを生JSONで書き出して構造を確かめる。"""
import json, re, io, sys

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
by = {e["id"]: e for e in events}
ids = [int(x) for x in sys.argv[1:]] or [6501]
out = [by[i] for i in ids if i in by]
io.open("tmp/peek_entry_0905.txt", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=2))
print("WROTE tmp/peek_entry_0905.txt ids=%s keys=%s"
      % (ids, sorted(out[0].keys()) if out else "-"))
