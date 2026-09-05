# -*- coding: utf-8 -*-
"""パーサー修正の前後で、再ビルドの券種名がどう変わったかを全件突き合わせる。
あわせて 3050/6053（統合先が別イベントなので保留）を落とした投入用ビルドを書き出す。
"""
import json, io

OLD = json.load(io.open("tmp/merge_built_0905.json", encoding="utf-8"))
NEW = json.load(io.open("tmp/merge_built2_0905.json", encoding="utf-8"))
HOLD = {3050, 6053}

o = {e["id"]: e for e in OLD}
n = {e["id"]: e for e in NEW}

buf = ["パーサー修正の前後diff（%d件 → %d件）" % (len(o), len(n)), ""]
diff_ids = []
for i in sorted(set(o) | set(n)):
    eo, en = o.get(i), n.get(i)
    to = [t.get("type") for t in (eo or {}).get("tickets", [])]
    tn = [t.get("type") for t in (en or {}).get("tickets", [])]
    if to == tn:
        continue
    diff_ids.append(i)
    buf.append("■ id=%s %s  枠 %d → %d" % (i, (en or eo).get("name", "")[:34], len(to), len(tn)))
    for x in to:
        if x not in tn:
            buf.append("    - 旧 %s" % x)
    for x in tn:
        if x not in to:
            buf.append("    + 新 %s" % x)
    buf.append("")

buf.append("差が出たエントリ: %d件 %s" % (len(diff_ids), diff_ids))
buf.append("")
buf.append("=== 保留（投入用ビルドから外す） ===")
for i in sorted(HOLD):
    e = n.get(i)
    buf.append("  id=%s %s ← 統合先が別イベント（既存はe+由来でぴあ枠ゼロ）" % (i, (e or {}).get("name", "")))

out = [e for e in NEW if e["id"] not in HOLD]
json.dump(out, io.open("tmp/merge_built2_use_0905.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open("tmp/built_diff_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("DIFF_ENTRIES=%d / USE=%d entries (%d slots) -> tmp/merge_built2_use_0905.json"
      % (len(diff_ids), len(out), sum(len(e.get("tickets") or []) for e in out)))
