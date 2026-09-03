# -*- coding: utf-8 -*-
"""C型（同じ枠に「個別eventCd版」と「bundle版」の2枚がある）の処理。
🚨ユーザーの方針決定が要る。既定は KEEP="individual"（公演ごとの個別ページを残す）。

  python tmp/fix_dup_c_0904.py                       # 下見（個別ページを残す想定）
  python tmp/fix_dup_c_0904.py --keep bundle         # まとめページを残す想定で下見
  python tmp/fix_dup_c_0904.py --apply               # 実行

url が「個別 vs bundle」のペアになっているグループだけを対象にする。
それ以外のC型（別ドメイン・別eventCd同士など）は触らない。
"""
import json, re, io, sys, shutil
from collections import defaultdict

PATH = "index.html"
APPLY = "--apply" in sys.argv
KEEP = "bundle" if "--keep" in sys.argv and "bundle" in sys.argv else "individual"

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた")
    sys.exit(1)
print("OK format roundtrip  KEEP=%s" % KEEP)


def is_bundle(u):
    return "eventBundleCd=" in (u or "")


before = sum(len(e.get("tickets", [])) for e in events)
n, skipped, touched = 0, 0, []
buf = ["C型の解消 2026-09-04（残す側=%s）" % KEEP, ""]

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
        if len(urls) < 2 or "" in urls:
            continue                      # A/B型はここでは扱わない
        bund = [t for t in group if is_bundle(t.get("url"))]
        indiv = [t for t in group if t.get("url") and not is_bundle(t.get("url"))]
        if not bund or not indiv or len(bund) + len(indiv) != len(group):
            skipped += 1
            continue                      # 個別vsbundleの形でなければ触らない
        losers = bund if KEEP == "individual" else indiv
        keepers = indiv if KEEP == "individual" else bund
        if len(keepers) != 1:
            skipped += 1
            continue                      # 残す側が1本に決まらないなら触らない
        for t in losers:
            if t.get("startDate") and not keepers[0].get("startDate"):
                keepers[0]["startDate"] = t["startDate"]
            drop.append(id(t)); n += 1
        buf.append("- id%s %s : %s（〜%s） 残す %s" % (
            e.get("id"), e.get("name"), k[0], k[1], keepers[0].get("url")))
    if drop:
        e["tickets"] = [t for t in ts if id(t) not in drop]
        touched.append(e.get("id"))

after = sum(len(e.get("tickets", [])) for e in events)
print("REMOVED=%d  SKIPPED(形が違う)=%d  ENTRIES=%d" % (n, skipped, len(set(touched))))
print("SLOTS %d -> %d" % (before, after))
io.open("tmp/fix_dup_c_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

if not APPLY:
    print("(下見のみ。--apply で書き込み)")
    sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_dupc")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html (backup: index.html.bak_0904_dupc)")
