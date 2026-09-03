# -*- coding: utf-8 -*-
"""index.html の EVENTS を解析して、同一エントリ内の重複チケット枠を数える（読み取り専用）"""
import re, json, collections, io, sys

PATH = r"C:\Users\user\oshinavi\index.html"

with open(PATH, "r", encoding="utf-8", newline="") as f:
    html = f.read()

m = re.search(r"const EVENTS = (\[.*?\]);", html, re.S)
if not m:
    print("EVENTS not found")
    sys.exit(1)

events = json.loads(m.group(1))
print("events_total=%d" % len(events))

tickets_total = sum(len(e.get("tickets") or []) for e in events)
print("tickets_total=%d" % tickets_total)

cat_mixed = []   # 空urlと非空urlが混在し、非空側は1種類
cat_same = []    # url が全部まったく同じ（空同士含む）
cat_multi = []   # 2種類以上の異なるurl（空を除く非空が2種類以上、または他）
groups_total = 0
dup_ticket_count = 0  # 重複グループ内のticket総数
collapse_removed = 0

for e in events:
    ts = e.get("tickets") or []
    buckets = collections.OrderedDict()
    for t in ts:
        key = (t.get("type"), t.get("date"))
        buckets.setdefault(key, []).append(t)
    for key, group in buckets.items():
        if len(group) < 2:
            continue
        groups_total += 1
        dup_ticket_count += len(group)
        collapse_removed += len(group) - 1
        urls = [ (t.get("url") or "") for t in group ]
        nonempty = sorted(set(u for u in urls if u.strip() != ""))
        has_empty = any(u.strip() == "" for u in urls)
        rec = {
            "id": e.get("id"),
            "name": e.get("name"),
            "type": key[0],
            "date": key[1],
            "n": len(group),
            "urls": urls,
        }
        if len(set(urls)) == 1:
            cat_same.append(rec)
        elif has_empty and len(nonempty) == 1:
            cat_mixed.append(rec)
        else:
            cat_multi.append(rec)

print("dup_groups_total=%d" % groups_total)
print("tickets_in_dup_groups=%d" % dup_ticket_count)
print("cat_mixed_empty_plus_one_url=%d" % len(cat_mixed))
print("cat_all_identical_url=%d" % len(cat_same))
print("cat_multiple_distinct_urls=%d" % len(cat_multi))
print("collapse: tickets_total %d -> %d (removed %d)" % (tickets_total, tickets_total - collapse_removed, collapse_removed))

def dump(title, lst, n=5):
    out = {"category": title, "group_count": len(lst), "samples": lst[:n]}
    return out

result = {
    "events_total": len(events),
    "tickets_total": tickets_total,
    "dup_groups_total": groups_total,
    "tickets_after_collapse": tickets_total - collapse_removed,
    "categories": [
        dump("mixed_empty_and_single_url", cat_mixed),
        dump("all_identical_url", cat_same),
        dump("multiple_distinct_urls", cat_multi),
    ],
}
with io.open(r"C:\Users\user\oshinavi\tmp\dup_ticket_audit_result.json", "w", encoding="utf-8") as f:
    f.write(json.dumps(result, ensure_ascii=False, indent=1))
print("wrote tmp/dup_ticket_audit_result.json")

# 参考: 分類ごとのエントリ数（ユニークid）
for title, lst in [("mixed", cat_mixed), ("same", cat_same), ("multi", cat_multi)]:
    print("%s_unique_entries=%d" % (title, len(set(r["id"] for r in lst))))
