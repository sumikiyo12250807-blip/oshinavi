# -*- coding: utf-8 -*-
"""指定エントリの全ぴあURLを、1本ずつ間隔を空けて叩いて実態を出す（429の巻き添え対策）。

  python tmp/verify_urls_0806.py 1333,3141

reconcile を一括で回すと429で「買える枠ゼロ」に見える枠が毎回変わる
（[[reference_pia_rate_limit_429]]）。確定させたい時はこれで1本ずつ読む。
"""
import json, re, io, sys, time, importlib.util, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

spec = importlib.util.spec_from_file_location("pt", os.path.join("tools", "pia_tickets.py"))

src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))
ids = [int(x) for x in sys.argv[1].split(",")]

import subprocess

for e in data:
    if e["id"] not in ids:
        continue
    urls = []
    p = (e.get("links") or {}).get("pia")
    if p:
        urls.append(p)
    for t in e.get("tickets") or []:
        u = t.get("url")
        if u and "pia" in u and u not in urls:
            urls.append(u)
    print("=== id%s %s ／ ぴあURL %d本" % (e["id"], (e.get("artist") or "")[:30], len(urls)))
    for u in urls:
        r = subprocess.run([sys.executable, "tools/pia_tickets.py", u],
                           capture_output=True)
        out = r.stdout.decode("utf-8", "replace").strip().splitlines()
        head = [l for l in out if "券種" in l]
        rows = [l for l in out if l.startswith("  [")]
        print("  %s" % u.split("=")[-1])
        print("    %s" % (head[0].strip() if head else "?"))
        for l in rows:
            print("    %s" % l.strip()[:110])
        time.sleep(4)
