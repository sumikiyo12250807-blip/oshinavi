# -*- coding: utf-8 -*-
"""3858(阪神対巨人 10/1)の links.pia を外す。

10/1は企画席しかぴあに出ていない（一般発売はまだ）。器を借りた名残で links.pia が
4試合分のバンドル(b2665272)を指していて、照合が 4対7 とズレる。
枠4つはそれぞれ試合別の券種URLを持っているので、エントリ側のぴあリンクは不要。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_3858_link"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

hit = 0
for e in EVENTS:
    if e["id"] == 3858:
        e["links"]["pia"] = None
        hit += 1
        print("枠のURL:")
        for t in e["tickets"]:
            print("   %s → %s" % (t["type"][:46], t.get("url")))
assert hit == 1
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("3858 の links.pia を外した")
