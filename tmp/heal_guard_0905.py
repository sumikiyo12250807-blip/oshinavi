# -*- coding: utf-8 -*-
"""ヒールの前後で「非ぴあ枠が消えていないか」を突き合わせる。

🚨 `heal_stale_deadlines.py --apply` は tickets を**丸ごと置き換える**。ぴあしか見ないので、
   同じエントリに載っている **e+／楽天／ローチケの枠が巻き添えで消える**。
   道具側の安全弁は「締切が今日以降の枠が失われたら適用しない」を**公演単位**でしか見ないため、
   **e+枠がぴあ枠に置き換わっても本数が同じなら素通りする**。

使い方:
  python tmp/heal_guard_0905.py save          # 適用の前に撮る
  python tmp/heal_guard_0905.py diff          # 適用の後に比べる（1本でも減ったら exit 1）
"""
import json, re, io, sys, datetime

SNAP = "tmp/heal_guard_0905.json"
TODAY = datetime.date.today().isoformat()
VENDORS = ("eplus.jp", "rakuten", "l-tike", "lawson")


def load():
    h = io.open("index.html", encoding="utf-8", newline="").read()
    return json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", h, re.S).group(1))


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


def snap():
    out = {}
    for e in load():
        u_nonpia = [t.get("url") for t in (e.get("tickets") or [])
                    if any(v in (t.get("url") or "") for v in VENDORS)]
        if not u_nonpia:
            continue
        out[str(e["id"])] = {
            "name": e.get("name", "")[:40],
            "nonpia": len(u_nonpia),
            "nonpia_urls": sorted(set(u_nonpia)),
            "total": len(e.get("tickets") or []),
            "visible": sum(1 for t in (e.get("tickets") or []) if visible(t)),
        }
    return out


cmd = sys.argv[1] if len(sys.argv) > 1 else "save"

if cmd == "save":
    s = snap()
    json.dump(s, io.open(SNAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("SAVED entries=%d  nonpia_slots=%d" % (len(s), sum(v["nonpia"] for v in s.values())))
    raise SystemExit(0)

old = json.load(io.open(SNAP, encoding="utf-8"))
new = snap()
buf, bad = [], 0
for i, o in sorted(old.items(), key=lambda x: int(x[0])):
    n = new.get(i)
    if not n:
        bad += 1
        buf.append("🚨 id=%-5s %s ← **非ぴあ枠が全部消えた**（%d本あった）" % (i, o["name"], o["nonpia"]))
        for u in o["nonpia_urls"]:
            buf.append("        %s" % u)
        continue
    if n["nonpia"] < o["nonpia"]:
        bad += 1
        buf.append("🚨 id=%-5s %s ← 非ぴあ枠 %d → %d（%d本消えた）"
                   % (i, o["name"], o["nonpia"], n["nonpia"], o["nonpia"] - n["nonpia"]))
        for u in sorted(set(o["nonpia_urls"]) - set(n["nonpia_urls"])):
            buf.append("        消えた: %s" % u)
    elif n["visible"] < o["visible"]:
        buf.append("△  id=%-5s %s ← 画面に出る枠 %d → %d（非ぴあ枠は無事）"
                   % (i, o["name"], o["visible"], n["visible"]))

tot_o = sum(v["nonpia"] for v in old.values())
tot_n = sum(v["nonpia"] for v in new.values())
buf.append("")
buf.append("非ぴあ枠の合計: %d → %d （差 %+d）" % (tot_o, tot_n, tot_n - tot_o))
buf.append("消えたエントリ: %d件" % bad)
io.open("tmp/heal_guard_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("NONPIA %d -> %d  BAD=%d -> tmp/heal_guard_0905.txt" % (tot_o, tot_n, bad))
raise SystemExit(1 if bad else 0)
