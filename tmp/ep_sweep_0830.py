# -*- coding: utf-8 -*-
"""e+ の「受付前（＝発売前）」を全ジャンル走査して、未掲載を1本にまとめる。

memory: reference_eplus_harvest
  - 一覧は公演日昇順なので**発売前は後ろのページ**（p30以降を狙う）
  - 状態は「受付前」＝発売前 ／ 券種(先着/抽選)で間引かない（feedback_capture_all_not_select）
🚨 e+ は「ぴあ以外」なので、投入前にユーザーの目視確認が要る（feedback_nonpia_user_eyes_until_gate）。
   このスクリプトは収集だけ。
"""
import json
import os
import subprocess
import sys
import shutil

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GENRES = ["rock-indies", "idol", "classic", "enka", "hiphop-rap", "visual",
          "voiceactor-live", "anime-song", "k-pop-asian", "jazz-fusion", "festival"]
OUT = "tmp/eplus_presale.json"

allitems = []
# 先に取ってある j-pop を回収
if os.path.exists("tmp/ep_j-pop_0830.json"):
    allitems += json.load(open("tmp/ep_j-pop_0830.json", encoding="utf-8"))

summary = []
for g in GENRES:
    logp = "tmp/_ep_%s_0830.log" % g
    with open(logp, "w", encoding="utf-8") as lf:
        r = subprocess.run([sys.executable, "tools/eplus_harvest.py", "presale", g,
                            "30", "62", "300", "受付前"],
                           stdout=lf, stderr=subprocess.STDOUT)
    n = 0
    if os.path.exists(OUT):
        try:
            items = json.load(open(OUT, encoding="utf-8"))
            n = len(items)
            shutil.copy(OUT, "tmp/ep_%s_0830.json" % g)
            for it in items:
                it["_genre"] = g
            allitems += items
        except Exception as e:
            print("  %s 読めず %s" % (g, e))
    print("%-16s 未掲載 %d件 (exit %s)" % (g, n, r.returncode))
    summary.append((g, n))

# eid で重複排除
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
