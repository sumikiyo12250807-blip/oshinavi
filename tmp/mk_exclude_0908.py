# -*- coding: utf-8 -*-
"""振り分けから外すidを作る＝①ぴあ以外（ユーザーの目視待ち）②相談中の件"""
import io, re, json

HOLD = [7165]   # 博多・天神落語まつり＝公演日(千秋楽)の扱いを相談中

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
pool = [e for e in EV if e.get("genre") == "new"]

def is_pia(e):
    lk = e.get("links", {}) or {}
    blob = " ".join([lk.get(k) or "" for k in ("pia", "eplus", "rakuten", "lawson")]
                    + [(t.get("url") or "") for t in (e.get("tickets") or [])])
    if "eplus.jp" in blob or "rakuten" in blob or "l-tike" in blob:
        return False
    return "t.pia.jp" in blob

nonpia = sorted(e["id"] for e in pool if not is_pia(e))
pia = sorted(e["id"] for e in pool if is_pia(e))
ex = sorted(set(nonpia) | set(HOLD))

io.open("tmp/exclude_0908.txt", "w", encoding="utf-8").write(",".join(str(i) for i in ex))
o = io.open("tmp/exclude_0908.md", "w", encoding="utf-8")
o.write("プール%d件 / ぴあ%d件 / ぴあ以外%d件\n" % (len(pool), len(pia), len(nonpia)))
o.write("振り分ける（ぴあ・相談中を除く）= %d件\n" % (len(pia) - len([i for i in HOLD if i in pia])))
o.write("除外 = %d件（ぴあ以外%d + 相談中%d）\n" % (len(ex), len(nonpia), len(HOLD)))
o.close()
print("pool=%d pia=%d nonpia=%d exclude=%d -> tmp/exclude_0908.txt"
      % (len(pool), len(pia), len(nonpia), len(ex)))
