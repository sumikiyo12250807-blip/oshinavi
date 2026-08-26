# -*- coding: utf-8 -*-
"""統合・再導出で落ちた ticket.url を、直前のバックアップから復元する。

なぜ＝build_pia_entries に複数URLを渡すと2本目以降の枠に url が付かない
（feedback_build_pia_multiurl_loses_ticket_url）。tickets を置換すると url が消え、
reconcile が links.pia のページしか見なくなって生きた枠を「0枠」と誤報する。

対応の取り方＝**バッジ文言（type）の完全一致**だけ。県+公演日+締切が入った文字列なので、
同じ文言なら同じ枠と見てよい。「県+M/D が一致したら刻む」式の当てはめはしない（2026-08-23の反省）。

  python tmp/restore_urls_0826.py <bak.html> <id,id,...>            # 調べるだけ
  python tmp/restore_urls_0826.py <bak.html> <id,id,...> --apply    # 書き込む
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

BAK = sys.argv[1]
IDS = set(int(x) for x in sys.argv[2].split(","))
APPLY = "--apply" in sys.argv


def load(path):
    src = open(path, encoding="utf-8").read()
    mm = re.search(r"(  const EVENTS = )(\[.*?\])(;)", src, re.S)
    return src, mm, json.loads(mm.group(2))


_, _, before = load(BAK)
h, m, EVENTS = load("index.html")
b_by_id = {e["id"]: e for e in before}
by_id = {e["id"]: e for e in EVENTS}

n = 0
for eid in sorted(IDS):
    eb, ea = b_by_id.get(eid), by_id.get(eid)
    if not eb or not ea:
        continue
    old_url = {}
    for t in eb.get("tickets") or []:
        if t.get("url"):
            old_url[t.get("type")] = t["url"]
    hits = []
    for t in ea.get("tickets") or []:
        if t.get("url"):
            continue
        u = old_url.get(t.get("type"))
        if u:
            t["url"] = u
            hits.append((t.get("type"), u))
            n += 1
    if hits:
        print("id=%-5d %s" % (eid, ea.get("artist")))
        for ty, u in hits:
            print("    %s\n        → %s" % (ty, u))

print("")
if APPLY and n:
    open("index.html.bak_0826_restore", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open("index.html", "w", encoding="utf-8").write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("%d枠のURLを戻した (backup: index.html.bak_0826_restore)" % n)
else:
    print("%d枠が対象（--apply で書き込む）" % n)
