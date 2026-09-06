# -*- coding: utf-8 -*-
"""B型・C型の統合候補を、枠の中身と飛び先URLまで並べて出す（夜の便の材料）。
実ページは叩かない。判断はこの表を見てから実ページで裏を取る。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

plan = json.load(open("tmp/merge_plan_0906.json", encoding="utf-8"))
h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
byid = {e["id"]: e for e in json.loads(m.group(2))}


def dump(e, tag):
    if not e:
        return
    print("  %s id=%-5d 公演%s  %s" % (tag, e["id"], e.get("date"), (e.get("venue") or "")[:60]))
    print("        %s" % ((e.get("links") or {}).get("pia") or "-"))
    for t in (e.get("tickets") or []):
        print("        枠 %s （〜%s）%s" % (t.get("type"), t.get("date"),
                                        ("→ " + t["url"]) if t.get("url") else ""))


print("=== B型：同じアーティストで既存が1件（同じツアーか要確認） ===")
for nid, eid in plan["B"]:
    if nid not in byid:
        continue
    print("")
    print("● %s" % (byid[nid].get("artist")))
    dump(byid[nid], "新  ")
    dump(byid.get(eid), "既存")

print("")
print("=== C型：既存が複数あって行き先を決められない ===")
for nid, exs in plan["C"]:
    if nid not in byid:
        continue
    print("")
    print("● %s" % (byid[nid].get("artist")))
    dump(byid[nid], "新  ")
    for eid in exs:
        dump(byid.get(eid), "既存")
