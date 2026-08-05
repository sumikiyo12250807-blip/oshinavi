# -*- coding: utf-8 -*-
"""pia_kw_search の出力(tmp/kw_kaidan/*.txt と tmp/kw_kaidan.txt)を集約し、
既に index.html に載っている eventCd/eventBundleCd を除いて「未登録の候補」だけ出す。

使い方: python tmp/kaidan_dedup_0805.py
出力  : tmp/kaidan_candidates.txt（人が読む用）＋ tmp/kaidan_candidates.json（投入用の素）
"""
import glob
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = r"C:\Users\user\oshinavi"
IDX = os.path.join(ROOT, "index.html")

# ---- 既存に出てくるぴあコードを全部集める（links.pia も ticket.url も本文も）----
h = io.open(IDX, encoding="utf-8").read()
known = set(re.findall(r"event(?:Bundle)?Cd=(b?\d+)", h))
print("既存index.htmlのぴあコード:", len(known), "個")

# ---- 検索結果を読む ----
files = [os.path.join(ROOT, "tmp", "kw_kaidan.txt")] + sorted(
    glob.glob(os.path.join(ROOT, "tmp", "kw_kaidan", "*.txt"))
)
BLOCK = re.compile(
    r"\[(?P<st>[^\]]+)\]\s*(?P<name>.+?)\n"
    r"\s*公演日:\s*(?P<day>.+?)\n"
    r"\s*会場\s*:\s*(?P<venue>.+?)\n"
    r"(?:\s*発売日:\s*(?P<rls>.+?)\n)?"
    r"\s*URL\s*:\s*(?P<url>\S+)",
)

seen, rows = {}, []
for f in files:
    if not os.path.exists(f):
        continue
    txt = io.open(f, encoding="utf-8").read()
    word = os.path.splitext(os.path.basename(f))[0].replace("kw_kaidan", "怪談")
    for m in BLOCK.finditer(txt):
        d = m.groupdict()
        cd = re.search(r"event(?:Bundle)?Cd=(b?\d+)", d["url"])
        if not cd:
            continue
        cd = cd.group(1)
        if cd in seen:
            if word not in seen[cd]["words"]:
                seen[cd]["words"].append(word)
            continue
        seen[cd] = {
            "cd": cd, "status": d["st"], "name": d["name"].strip(),
            "day": d["day"].strip(), "venue": d["venue"].strip(),
            "rls": (d["rls"] or "").strip(), "url": d["url"].strip(),
            "words": [word], "known": cd in known,
        }
        rows.append(seen[cd])

new = [r for r in rows if not r["known"]]
old = [r for r in rows if r["known"]]
print("検索ヒット合計: %d件（既存 %d / 未登録 %d）" % (len(rows), len(old), len(new)))

lines = ["=== 未登録の候補 %d件 ===" % len(new), ""]
for r in sorted(new, key=lambda x: x["day"]):
    lines.append("[%s] %s" % (r["status"], r["name"]))
    lines.append("   公演日: %s ／ %s" % (r["day"], r["venue"]))
    if r["rls"]:
        lines.append("   発売日: %s" % r["rls"])
    lines.append("   ヒット語: %s" % ",".join(r["words"]))
    lines.append("   %s" % r["url"])
    lines.append("")
lines += ["", "=== 既に載っている %d件（参考）===" % len(old), ""]
for r in sorted(old, key=lambda x: x["day"]):
    lines.append("  %s ／ %s ／ %s" % (r["name"][:52], r["day"], r["venue"][:28]))

io.open(os.path.join(ROOT, "tmp", "kaidan_candidates.txt"), "w", encoding="utf-8").write("\n".join(lines))
json.dump(new, io.open(os.path.join(ROOT, "tmp", "kaidan_candidates.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("→ tmp/kaidan_candidates.txt / .json")
