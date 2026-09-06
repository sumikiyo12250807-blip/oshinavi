# -*- coding: utf-8 -*-
"""check_expired の「公演終了済」候補を、公演日と生き枠で仕分ける。
出力: tmp/delcand_0907.txt（消してよい／今日の公演で保留／配信で生き枠あり）
URLは index.html から機械抽出したものだけを出す（DELETE_GATE 4.7）。
"""
import re, json, datetime

TODAY = "2026-09-07"

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}

txt = open("tmp/expired_0907.txt", encoding="utf-8").read()

# 「期限切れ削除候補(公演終了済)」の行だけ拾う
ids = []
for m in re.finditer(r"^  id=(\d+): (.*?)$", txt, re.M):
    eid = int(m.group(1))
    line = m.group(2)
    if "開催終了" in line:
        ids.append((eid, line))

def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)

ok, hold_today, hold_alive = [], [], []
for eid, line in ids:
    e = by.get(eid)
    if not e:
        continue
    d = e.get("date") or ""
    alive = [t for t in e.get("tickets", []) if visible(t)]
    url = ""
    for k in ("pia", "eplus", "rakuten", "lawson"):
        if (e.get("links") or {}).get(k):
            url = e["links"][k]
            break
    row = (eid, d, e.get("name", "")[:46], url, len(alive))
    if d >= TODAY:
        hold_today.append(row)
    elif alive:
        hold_alive.append(row)
    else:
        ok.append(row)

with open("tmp/delcand_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 削除候補の仕分け (today=%s) ===\n" % TODAY)
    f.write("公演終了済の候補 %d件 → 消してよい %d / 公演が今日以降で保留 %d / 生き枠ありで保留 %d\n\n"
            % (len(ids), len(ok), len(hold_today), len(hold_alive)))
    f.write("【消してよい】公演日が昨日以前・画面に出る枠ゼロ\n")
    for r in sorted(ok, key=lambda x: x[1]):
        f.write("  id=%-6s 公演%s 枠0  %s\n     %s\n" % (r[0], r[1], r[2], r[3] or "(URLなし)"))
    f.write("\n【保留】公演が今日以降\n")
    for r in sorted(hold_today, key=lambda x: x[1]):
        f.write("  id=%-6s 公演%s 生き枠%d  %s\n     %s\n" % (r[0], r[1], r[4], r[2], r[3] or "(URLなし)"))
    f.write("\n【保留】生きている枠がある（配信など）\n")
    for r in sorted(hold_alive, key=lambda x: x[1]):
        f.write("  id=%-6s 公演%s 生き枠%d  %s\n     %s\n" % (r[0], r[1], r[4], r[2], r[3] or "(URLなし)"))
    f.write("\n【消してよいidのカンマ区切り】\n%s\n" % ",".join(str(r[0]) for r in sorted(ok, key=lambda x: x[0])))

print("cand=%d ok=%d hold_today=%d hold_alive=%d" % (len(ids), len(ok), len(hold_today), len(hold_alive)))
