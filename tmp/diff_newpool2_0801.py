# -*- coding: utf-8 -*-
"""新着プール：登録tickets vs ぴあ再導出tickets の差分（改良版）。

改良点＝偽陽性つぶし:
  heal は links.pia だけを叩いて作り直すので、**会場別URL(ticket.url)を持つ枠**は
  「ぴあに無い」と誤検出される（2026-08-01 真心ブラザーズで発生）。
  → ticket.url が links.pia と違う枠は「別ページ管理」として除外する。
適用はしない（新着プールは NEW_ORDER 固定・報告用）。"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

H = r"C:\Users\user\oshinavi\index.html"
J = r"C:\Users\user\oshinavi\tmp\heal_ids.json"

h = open(H, "rb").read().decode("utf-8")
evs = json.loads(re.search(r"  const EVENTS = (\[.*?\]);", h, re.S).group(1))
cur = {e["id"]: e for e in evs}
items = json.load(open(J, encoding="utf-8"))


def base(ty):
    ty = re.sub(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$", "", ty or "")
    ty = re.sub(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$", "", ty)
    return ty.strip()


miss_rows, drop_rows = [], []
for it in items:
    eid = it.get("id")
    e = cur.get(eid)
    if not e or e.get("genre") != "new":
        continue
    piaurl = (e.get("links") or {}).get("pia") or ""
    newt = it.get("tickets") or []
    oldt = e.get("tickets") or []
    oldk = {base(t.get("type")) for t in oldt}
    newk = {base(t.get("type")) for t in newt}

    missing = [t for t in newt if base(t.get("type")) not in oldk]
    # 別ページ管理(会場別URL)の枠は「ぴあに無い」判定から除外
    gone = [
        t for t in oldt
        if base(t.get("type")) not in newk
        and (not t.get("url") or t.get("url") == piaurl)
    ]
    other = [
        t for t in oldt
        if base(t.get("type")) not in newk
        and t.get("url") and t.get("url") != piaurl
    ]
    if missing:
        miss_rows.append((eid, e, oldt, missing))
    if gone:
        drop_rows.append((eid, e, gone, other))

print("=== ① 取りこぼし：ぴあにあって登録に無い枠 ===")
if not miss_rows:
    print("  なし ✅")
for eid, e, oldt, missing in sorted(miss_rows, key=lambda r: -len(r[3])):
    print("\n■ id=%s %s（登録%d枠）" % (eid, e.get("name"), len(oldt)))
    for t in missing:
        print("   ➕ %s  [date=%s start=%s]" % (t.get("type"), t.get("date"), t.get("startDate")))
    print("   pia: %s" % ((e.get("links") or {}).get("pia")))

print("\n\n=== ② 登録にあってぴあ(links.pia)に無い枠 ===")
if not drop_rows:
    print("  なし ✅")
for eid, e, gone, other in drop_rows:
    print("\n■ id=%s %s" % (eid, e.get("name")))
    for t in gone:
        print("   ➖ %s  [date=%s]" % (t.get("type"), t.get("date")))
    if other:
        print("   （別ページ管理として除外した枠: %d件）" % len(other))
    print("   pia: %s" % ((e.get("links") or {}).get("pia")))

print("\n差分なし: %d件 / 全%d件" % (len(items) - len({r[0] for r in miss_rows} | {r[0] for r in drop_rows}), len(items)))
