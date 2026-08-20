# -*- coding: utf-8 -*-
"""新着プール52件：登録済みticketsと、ぴあから再導出したticketsの差分を出す。
適用はしない（新着プールは並び順ロック＝feedback_new_list_order_lock）。報告用。"""
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

data = json.load(open(J, encoding="utf-8"))
items = data if isinstance(data, list) else data.get("items") or data.get("converts") or []


def base(ty):
    """券種名から日付・時刻部分を落とした比較キー"""
    ty = re.sub(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$", "", ty or "")
    ty = re.sub(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$", "", ty)
    return ty.strip()


rows = []
for it in items:
    if not isinstance(it, dict):
        continue
    eid = it.get("id")
    e = cur.get(eid)
    if not e or e.get("genre") != "new":
        continue
    newt = it.get("tickets") or []
    oldt = e.get("tickets") or []
    oldk = {base(t.get("type")) for t in oldt}
    newk = {base(t.get("type")) for t in newt}
    missing = [t for t in newt if base(t.get("type")) not in oldk]
    gone = [t for t in oldt if base(t.get("type")) not in newk]
    if missing or gone:
        rows.append((eid, e, oldt, newt, missing, gone))

print("=== 新着プール 取りこぼし監査（差分があった %d件 / 52件中）===\n" % len(rows))
rows.sort(key=lambda r: -len(r[4]))
for eid, e, oldt, newt, missing, gone in rows:
    print("■ id=%s %s" % (eid, e.get("name")))
    print("   登録 %d枠 → ぴあ実態 %d枠" % (len(oldt), len(newt)))
    for t in missing:
        print("   ➕未登録: %s" % t.get("type"))
        print("        date=%s startDate=%s" % (t.get("date"), t.get("startDate")))
    for t in gone:
        print("   ➖ぴあに無い(登録のみ): %s" % t.get("type"))
    print("   pia: %s" % ((e.get("links") or {}).get("pia")))
    print()

print("差分なし: %d件" % (52 - len(rows)))
