# -*- coding: utf-8 -*-
"""A型統合の「残す側（既存）」のぴあURLが生きているかだけを確かめる。
ぴあは単独 eventCd を消して bundle に作り直すので、死んだ側を残すと購入ボタンが無言で死ぬ
（feedback_pia_eventcd_gone）。1件ずつ間を空けて叩く（429対策）。
"""
import json
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

DEAD = ("ご指定の公演情報が見つかりませんでした", "指定された公演は存在しません")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

plan = json.load(open("tmp/merge_plan_0906.json", encoding="utf-8"))
pairs = [tuple(x) for x in plan["A"]]

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
byid = {e["id"]: e for e in json.loads(m.group(2))}

for nid, eid in pairs:
    e = byid.get(eid)
    if not e:
        print("id=%d 見つからない" % eid)
        continue
    u = ((e.get("links") or {}).get("pia") or "")
    if not u:
        print("既存%-5d  ぴあURL無し  %s" % (eid, (e.get("artist") or "")[:30]))
        continue
    try:
        req = urllib.request.Request(u, headers=UA)
        body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        if "sorry.pia.jp" in body[:2000]:
            st = "⚠️混雑ページ（判定不能）"
        elif any(d in body for d in DEAD):
            st = "🚨DEAD"
        else:
            st = "OK"
        print("既存%-5d  %-10s %-30s %s" % (eid, st, (e.get("artist") or "")[:30], u))
    except Exception as ex:
        print("既存%-5d  ❌ERR %s  %s" % (eid, ex, u))
    time.sleep(2.0)
