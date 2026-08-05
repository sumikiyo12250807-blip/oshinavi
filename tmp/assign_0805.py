# -*- coding: utf-8 -*-
"""新着プールを振り分ける。ただし【機械で確認しきれていない子はプールに残す】（ユーザー指示 2026-08-05
「見えてない部分だけ残して　他はふりわけOK　自信ないところは残して、わたしがみるわ」）。

残す条件（1つでも当てはまれば残す＝安全側に倒す）:
  A ぴあの機械照合が効かない＝links.pia が無い（e+/楽天/ローチケのみ）
      → reconcile_pia は【ぴあ専用】なので二段構えが丸ごと効かない（[[feedback_delete_nonpia_blindspot]]）
  B 同一エントリ内で「締切(date,startDate)が同じ」枠が複数ある
      → reconcile が対を確定できず【未照合skip】になる枠（今回125件で25枠あった）。
        「一致」と出ていてもその枠は見ていない（[[reference_reconcile_pia_qc_gate]]）
  C 表記の根拠に推定が混じっている＝3676（引換場所ラベルをぴあHTMLの出現順で振った）
  D ジャンルの相談が残っている＝3801（三木大雲のポジティ部ラジオ＝kaidan か owarai か）

振り分ける子は _genre→genre / _extraGenres→extraGenres に移し、下書きフィールドを消す。
NEW_ORDER は残す子だけにする（並びは既存の順を保つ＝[[feedback_new_list_order_lock]]）。
"""
import io
import json
import os
import re
import shutil
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
IDX = os.path.join(ROOT, "index.html")
BAK = os.path.join(ROOT, "index.html.bak_0805_assign")

KEEP_MANUAL = {3676: "引換場所ラベルをぴあの出現順で推定した",
               3801: "ジャンル相談中（kaidan か owarai か）"}

h = io.open(IDX, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
pool = [e for e in EVENTS if e.get("genre") == "new"]

keep, move = [], []
for e in pool:
    why = []
    if not (e.get("links") or {}).get("pia"):
        why.append("ぴあリンク無し＝機械照合が効かない")
    dup = Counter((t.get("date"), t.get("startDate")) for t in (e.get("tickets") or []))
    if any(v > 1 for v in dup.values()):
        why.append("同じ締切の枠が複数＝reconcileが照合できない枠を含む")
    if e["id"] in KEEP_MANUAL:
        why.append(KEEP_MANUAL[e["id"]])
    (keep if why else move).append((e, why))

print("=== プールに残す %d件 ===" % len(keep))
for e, why in sorted(keep, key=lambda x: x[0]["id"]):
    print("  id%-5d %-42s ← %s" % (e["id"], (e.get("artist") or "")[:42], " ／ ".join(why)))

c = Counter()
for e, _ in move:
    g = e.get("_genre")
    ex = e.get("_extraGenres") or []
    assert g and g != "new", "下書きジャンルが無い: id%d" % e["id"]
    e["genre"] = g
    if ex:
        e["extraGenres"] = ex
    for k in ("_genre", "_extraGenres", "_piaSub"):
        e.pop(k, None)
    c[g + ("+" + ",".join(ex) if ex else "")] += 1

print("\n=== 振り分けた %d件 ===" % len(move))
for k, v in c.most_common():
    print("   %-18s %d件" % (k, v))

keep_ids = [e["id"] for e, _ in keep]
mo = re.search(r"(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]", h)
cur = [int(x) for x in re.findall(r"\d+", mo.group(2))]
new_order = [i for i in cur if i in keep_ids]
h2 = re.sub(r"(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]",
            r"\g<1>[" + ", ".join(str(i) for i in new_order) + "]", h, count=1)

shutil.copyfile(IDX, BAK)
m2 = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h2, re.S)
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
io.open(IDX, "w", encoding="utf-8", newline="").write(
    h2[:m2.start()] + m2.group(1) + arr + m2.group(3) + h2[m2.end():])
print("\n✅ NEW_ORDER %d件 / genre:new %d件 / backup %s"
      % (len(new_order), len(keep), os.path.basename(BAK)))
