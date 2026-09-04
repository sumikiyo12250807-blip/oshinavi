# -*- coding: utf-8 -*-
"""今朝の未掲載228件が、いまどこまで処理できたかを数える。
🚨件数でなく「処理できた/全部」で出す（[[feedback_coverage_not_count]]）。
判定は index.html の eventCd 登録有無＝**結果**で見る（自分のメモではなく現物）。"""
import json, re, io

html = io.open("index.html", encoding="utf-8", newline="").read()
ex_cds = set(re.findall(r"event(?:Bundle)?Cd=(\w+)", html))

tri = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))


def cd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


total = done = 0
rows = []
rest = []
for k in ("fresh", "samename", "today", "unknown"):
    items = tri[k]
    d = sum(1 for it in items if cd(it.get("url")) in ex_cds)
    rows.append((k, len(items), d))
    total += len(items)
    done += d
    for it in items:
        if cd(it.get("url")) not in ex_cds:
            rest.append((k, it))

print("=== 今朝の未掲載の処理状況（現物のindex.htmlで判定）===")
for k, n, d in rows:
    print("  %-9s %3d件中 %3d件 取り込み済み（残り%d）" % (k, n, d, n - d))
print("  ---------------------------------------------")
print("  合計       %3d件中 %3d件 取り込み済み（残り%d）" % (total, done, total - done))

buf = ["まだ取り込めていない分（%d件）" % len(rest), ""]
for k, it in rest:
    buf.append("[%s] %s | 発売%s | %s %s" % (k, it.get("artist"), it.get("rlsdate"),
                                             it.get("pref"), it.get("venue")))
    buf.append("    %s" % it.get("url"))
io.open("tmp/coverage_rest_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("\n残りの一覧 -> tmp/coverage_rest_0904.txt")
