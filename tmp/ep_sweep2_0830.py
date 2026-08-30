# -*- coding: utf-8 -*-
"""e+ の受付前（発売前）を、0件だったジャンルについて **p1〜p30** で取り直す。

🚨 なぜ最初に空振りしたか
  memory reference_eplus_harvest に「一覧は公演日昇順なので発売前は後ろのページ」とある。
  これは **j-pop のようにページ数が多い（62p超）ジャンル** の話で、
  ページ総数が30未満のジャンルを p30〜62 で見に行くと**範囲外＝必ず0件**になる。
  ＝「後ろのページ」は相対的な位置であって、絶対のページ番号ではない。
"""
import json
import os
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GENRES = ["classic", "idol", "enka", "hiphop-rap", "visual",
          "voiceactor-live", "anime-song", "k-pop-asian", "jazz-fusion", "festival"]
OUT = "tmp/eplus_presale.json"

allitems = []
for f in ("tmp/ep_j-pop_0830.json", "tmp/ep_rock-indies_0830.json"):
    if os.path.exists(f):
        items = json.load(open(f, encoding="utf-8"))
        for it in items:
            it.setdefault("_genre", os.path.basename(f)[3:-10])
        allitems += items

summary = []
for g in GENRES:
    with open("tmp/_ep2_%s_0830.log" % g, "w", encoding="utf-8") as lf:
        r = subprocess.run([sys.executable, "tools/eplus_harvest.py", "presale", g,
                            "1", "30", "300", "受付前"],
                           stdout=lf, stderr=subprocess.STDOUT)
    n = 0
    if os.path.exists(OUT):
        try:
            items = json.load(open(OUT, encoding="utf-8"))
            n = len(items)
            shutil.copy(OUT, "tmp/ep2_%s_0830.json" % g)
            for it in items:
                it["_genre"] = g
            allitems += items
        except Exception as e:
            print("  %s 読めず %s" % (g, e))
    print("%-16s 未掲載 %d件 (exit %s)" % (g, n, r.returncode))
    summary.append((g, n))

seen, uniq = set(), []
for it in allitems:
    k = it.get("eid") or it.get("url")
    if k in seen:
        continue
    seen.add(k)
    uniq.append(it)

json.dump(uniq, open("tmp/ep_presale_all_0830.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print()
print("=== 合計 %d件（重複除き）→ tmp/ep_presale_all_0830.json ===" % len(uniq))
for g, n in summary:
    print("   %-16s %d" % (g, n))
