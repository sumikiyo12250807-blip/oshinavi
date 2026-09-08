# -*- coding: utf-8 -*-
"""照合で出た MISSING を「ヒールで直るもの」と「そうでないもの」に分ける。

ヒールで直る型＝登録が「M/D HH:MM発売」の単日形（startDate==date）で、
ぴあ側は発売開始後に締切を出している。＝今日10時などに売り始めたぶん。
それ以外＝本当に枠が足りていない可能性があるので、別に見る。
"""
import io, re, json, sys

sys.stdout.reconfigure(encoding="utf-8")
TODAY = "2026-09-08"

raw = open("tmp/reconcile0101_0908.txt", "rb").read()
try:
    txt = raw.decode("utf-8")
except Exception:
    txt = raw.decode("cp932", "replace")

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))}

blocks = re.split(r"\n(?=[✅🚨⚠️❌💤] id=)", txt)
heal, other, gone = [], [], []
for b in blocks:
    m = re.match(r"🚨 id=(\d+)", b)
    if not m:
        continue
    i = int(m.group(1))
    e = EV.get(i)
    if not e:
        gone.append(i)
        continue
    single = [t for t in (e.get("tickets") or [])
              if t.get("startDate") and t.get("startDate") == t.get("date")]
    today_start = [t for t in single if t.get("startDate") == TODAY]
    name = (e.get("name") or "")[:30]
    if today_start:
        heal.append((i, name, len(today_start)))
    elif single:
        heal.append((i, name, 0))
    else:
        other.append((i, name, b.strip().splitlines()[1][:90] if len(b.strip().splitlines()) > 1 else ""))

o = io.open("tmp/classify_missing_0908.md", "w", encoding="utf-8")
o.write("# 照合のMISSINGを仕分ける（today=%s）\n\n" % TODAY)
o.write("- ✅ヒールで直る見込み … **%d件**（登録が「M/D HH:MM発売」の単日形＝締切がまだ入っていない）\n" % len(heal))
o.write("- 🚨別に見る必要がある … **%d件**\n" % len(other))
if gone:
    o.write("- （現物に無いid … %d件）\n" % len(gone))
o.write("\n## ✅ヒールで直る見込み\n\n| id | 公演名 | 今日発売の単日枠 |\n|---|---|---|\n")
for i, n, k in heal:
    o.write("| %d | %s | %d |\n" % (i, n, k))
if other:
    o.write("\n## 🚨別に見る必要がある\n\n")
    for i, n, detail in other:
        o.write("- **id%d %s**\n  %s\n" % (i, n, detail))
o.close()
print("heal=%d other=%d gone=%d -> tmp/classify_missing_0908.md" % (len(heal), len(other), len(gone)))
