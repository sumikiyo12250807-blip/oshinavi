# -*- coding: utf-8 -*-
"""サイト全体の二重登録のうち、畳んでよい2型だけを消す。

  A: 同じ(type,date)で「url無し」と「url有り」が並んでいる → url無しを消す（url有りを残す）
  B: 同じ(type,date)でurlまで完全に同じ → 1つだけ残す
  C: 同じ(type,date)でurlが違う → 🚨触らない（別の売り場かもしれない
     ＝[[feedback_dedup_badges_keeps_urls]]「飛び先が違えば畳まない」）

消す側が startDate を持っていて残す側に無ければ引き継ぐ（情報を失わない）。
改行はCRLFのまま保つ。

  python tmp/fix_dup_all_0904.py          # 下見
  python tmp/fix_dup_all_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil
from collections import defaultdict

PATH = "index.html"
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた")
    sys.exit(1)
print("OK format roundtrip")

before_slots = sum(len(e.get("tickets", [])) for e in events)
n_a, n_b, touched = 0, 0, []

for e in events:
    ts = e.get("tickets", [])
    if len(ts) < 2:
        continue
    g = defaultdict(list)
    for t in ts:
        g[(t.get("type"), t.get("date"))].append(t)
    drop = []
    for k, group in g.items():
        if len(group) < 2:
            continue
        urls = set((t.get("url") or "") for t in group)
        if "" in urls and len(urls - {""}) == 1:
            # A型: url有りを残し、url無しを消す
            survivor = next(t for t in group if t.get("url"))
            for t in group:
                if t.get("url"):
                    continue
                if t.get("startDate") and not survivor.get("startDate"):
                    survivor["startDate"] = t["startDate"]
                drop.append(id(t)); n_a += 1
        elif len(urls) == 1:
            # B型: 完全重複。最初の1つだけ残す
            for t in group[1:]:
                if t.get("startDate") and not group[0].get("startDate"):
                    group[0]["startDate"] = t["startDate"]
                drop.append(id(t)); n_b += 1
        # C型は触らない
    if drop:
        e["tickets"] = [t for t in ts if id(t) not in drop]
        touched.append((e.get("id"), e.get("name"), len(ts), len(e["tickets"])))

after_slots = sum(len(e.get("tickets", [])) for e in events)
print("A_removed=%d  B_removed=%d  TOTAL=%d" % (n_a, n_b, n_a + n_b))
print("SLOTS %d -> %d (差 %d)" % (before_slots, after_slots, before_slots - after_slots))
print("ENTRIES_TOUCHED=%d" % len(touched))

buf = ["二重登録の解消 2026-09-04（A=url無し版を消す / B=完全重複を1つに）", ""]
for eid, name, b, a in touched:
    buf.append("- id%s %s : 枠 %d -> %d" % (eid, name, b, a))
io.open("tmp/fix_dup_all_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

if not APPLY:
    print("(下見のみ。--apply で書き込み)")
    sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_dupall")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html (backup: index.html.bak_0904_dupall)")
