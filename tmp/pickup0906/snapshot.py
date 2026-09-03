# -*- coding: utf-8 -*-
"""記事を書いた時点の「主役5組＋名前タイル12組の枠」を記録する。
土曜にもう一度これを回して差分を見る＝原稿を書いたあとにぴあが枠を足すため
（[[feedback_deadline_extended_after_register]]／2026-08-23に真心ブラザーズが8→9公演になっていた）。

  python tmp/pickup0906/snapshot.py            # 記録する
  python tmp/pickup0906/snapshot.py --diff     # 記録と今を比べる（土曜にこれを回す）
"""
import json, re, io, sys, os

SNAP = "tmp/pickup0906/snapshot.json"
FROM, TO = "2026-09-07", "2026-09-13"
IDS = [4500, 4489, 4236, 668, 4246,            # 主役5組
       6060, 6003, 950, 4228, 4235, 4227, 5993, 6009, 4103, 6141, 4230, 4490]  # タイル12組

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}


def week_slots(e):
    r = []
    for t in e.get("tickets", []):
        if t.get("soldout") or t.get("saleEnded"):
            continue
        sd = t.get("startDate") or ""
        if FROM <= sd <= TO and re.search(r"\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売", t.get("type") or ""):
            r.append(t.get("type"))
    return sorted(r)


now = {}
for i in IDS:
    e = by_id.get(i)
    if not e:
        now[str(i)] = {"name": "(消えた)", "slots": []}
        continue
    now[str(i)] = {"name": e.get("name"), "date": e.get("date"),
                   "venue": e.get("venue"), "slots": week_slots(e)}

if "--diff" not in sys.argv:
    json.dump(now, io.open(SNAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("記録した: %s" % SNAP)
    print("対象 %d件 / 今週の発売枠 合計 %d本" % (len(now), sum(len(v["slots"]) for v in now.values())))
    sys.exit(0)

if not os.path.exists(SNAP):
    print("記録が無い。先に --diff なしで回して"); sys.exit(3)
old = json.load(io.open(SNAP, encoding="utf-8"))

buf, changed = [], 0
for k, v in now.items():
    o = old.get(k)
    if not o:
        buf.append("新しく入った id=%s %s" % (k, v["name"])); changed += 1; continue
    add = [x for x in v["slots"] if x not in o["slots"]]
    los = [x for x in o["slots"] if x not in v["slots"]]
    if add or los or v.get("date") != o.get("date") or v.get("venue") != o.get("venue"):
        changed += 1
        buf.append("=" * 66)
        buf.append("id=%s %s" % (k, v["name"]))
        if v.get("date") != o.get("date"):
            buf.append("  🚨千秋楽が変わった: %s -> %s" % (o.get("date"), v.get("date")))
        if v.get("venue") != o.get("venue"):
            buf.append("  🚨会場が変わった")
            buf.append("     旧: %s" % o.get("venue"))
            buf.append("     新: %s" % v.get("venue"))
        for x in add:
            buf.append("  ＋増えた枠: %s" % x)
        for x in los:
            buf.append("  −消えた枠: %s" % x)

io.open("tmp/pickup0906/snapshot_diff.txt", "w", encoding="utf-8").write("\n".join(buf) or "変化なし")
print("変化があったエントリ=%d / %d" % (changed, len(now)))
print("詳細 -> tmp/pickup0906/snapshot_diff.txt")
if changed:
    print("🚨記事の本文と「発売になる公演」の箱を、この差分で直してから公開すること")
    sys.exit(2)
print("✅記事を書いた時点から変わっていない")
