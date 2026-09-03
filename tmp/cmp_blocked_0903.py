# -*- coding: utf-8 -*-
"""安全弁でブロックされた4件について、いまの枠とぴあが返した枠を並べて見る。"""
import json, re, io

IDS = [3370, 3735, 3752, 5516]
html = io.open("index.html", encoding="utf-8").read()
events = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))}
built = {o["id"]: o for o in json.load(io.open("tmp/heal_ids.json", encoding="utf-8"))}

for i in IDS:
    e = events.get(i, {})
    b = built.get(i, {})
    print("=" * 78)
    print("id=%s  %s" % (i, e.get("name", "")))
    print("--- いま index.html にある枠 ---")
    for t in e.get("tickets", []):
        print("   type=%s" % t.get("type"))
        print("     startDate=%s date=%s url=%s" % (t.get("startDate"), t.get("date"), (t.get("url") or "")[:80]))
    print("--- ぴあが返した枠 (status=%s) ---" % b.get("status"))
    for t in b.get("tickets", []):
        print("   type=%s" % t.get("type"))
        print("     startDate=%s date=%s url=%s" % (t.get("startDate"), t.get("date"), (t.get("url") or "")[:80]))
    print("--- 参照した代表URL: %s" % (b.get("srcUrl") or b.get("url") or "(不明)"))
    print()
