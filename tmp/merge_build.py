# -*- coding: utf-8 -*-
import json, re, urllib.parse, os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base = r"C:\Users\user\oshinavi"
files = ["built_A","built_B","built_C","built_D","built_E","built_F","built_G","built_H","built_I"]

# harvestのperfdate（公演日）を eventCd で引けるようにする
pre = json.load(open(os.path.join(base, "tmp", "presale_01.json"), encoding="utf-8"))
perfmap = {}
for it in pre["new"]:
    mm = re.search(r'event(?:Bundle)?Cd=(\w+)', it.get("url", ""))
    if mm:
        perfmap[mm.group(1)] = it.get("perfdate", "")

def parse_perf(s):
    ds = re.findall(r'(\d{4})/(\d{1,2})/(\d{1,2})', s or "")
    if not ds:
        return None
    dts = sorted("%04d-%02d-%02d" % (int(y), int(m), int(d)) for y, m, d in ds)
    return dts[-1]

entries = []
seen = {}
dups = []
for f in files:
    p = os.path.join(base, "tmp", f + ".json")
    data = json.load(open(p, encoding="utf-8"))
    for e in data:
        pia = e.get("pia", "")
        m = re.search(r'event(?:Bundle)?Cd=(\w+)', pia)
        cd = m.group(1) if m else pia
        if cd in seen:
            dups.append((f, e.get("artist"), cd))
            continue
        seen[cd] = e["artist"]
        e["_cd"] = cd
        entries.append(e)

def norm_pref(p):
    if not p: return p
    parts = re.split(r'[・/／]', p)
    out = []
    for t in parts:
        t = t.strip()
        if t == "北海道":
            out.append(t); continue
        if t and t[-1] in "都府県":
            t = t[:-1]
        out.append(t)
    # 重複除去・順序維持
    seen2 = []
    for t in out:
        if t and t not in seen2:
            seen2.append(t)
    return "・".join(seen2)

def conv_url(u):
    if not u: return u
    m = re.search(r'eventBundleCd=(\w+)', u)
    if m: return "https://t.pia.jp/pia/event/event.do?eventBundleCd=" + m.group(1)
    m = re.search(r'eventCd=(\w+)', u)
    if m: return "https://t.pia.jp/pia/event/event.do?eventCd=" + m.group(1)
    return u

start_id = 855
built = []
guess_rows = []
for i, e in enumerate(entries):
    eid = start_id + i
    pia = conv_url(e.get("pia", ""))
    links = {"rakuten": None, "lawson": None, "pia": pia, "eplus": None}
    ak = e.get("amazonKeyword")
    if ak:
        links["amazon"] = "https://www.amazon.co.jp/s?k=" + urllib.parse.quote(ak) + "&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    tickets = []
    for t in e.get("tickets", []):
        nt = {"type": t["type"]}
        if t.get("startDate"): nt["startDate"] = t["startDate"]
        nt["date"] = t["date"]
        if t.get("url"): nt["url"] = conv_url(t["url"])
        tickets.append(nt)
    perf = parse_perf(perfmap.get(e["_cd"], ""))
    ev_date = perf if perf else e["date"]
    obj = {
        "id": eid,
        "artist": e["artist"],
        "name": e["name"],
        "date": ev_date,
        "dateLabel": e["dateLabel"],
        "venue": e["venue"],
        "prefecture": norm_pref(e["prefecture"]),
        "genre": "new",
        "price": None,
        "links": links,
        "tickets": tickets,
        "verified": True,
        "verifiedAt": "2026-06-17"
    }
    built.append(obj)
    guess_rows.append((eid, e.get("genreGuess",""), e["artist"], obj["prefecture"], e.get("status","")))

js = json.dumps(built, ensure_ascii=False, indent=2)
open(os.path.join(base, "tmp", "final_built.json"), "w", encoding="utf-8").write(js)
ids = [o["id"] for o in built]
open(os.path.join(base, "tmp", "new_order.txt"), "w").write(",".join(map(str, ids)))

print("=== 構築 %d件  id %d〜%d ===" % (len(built), ids[0], ids[-1]))
print("--- 重複排除 %d件 ---" % len(dups))
for d in dups:
    print("  DUP除外:", d[0], d[1], d[2])
print("--- ジャンル推定 ---")
from collections import Counter
c = Counter(g[1] for g in guess_rows)
print(dict(c))
print("--- 当日引換券/要注意 status ---")
for g in guess_rows:
    if "当日" in g[4] or "全枠終了" in g[4]:
        print("  ", g[0], g[2], "|", g[4][:40])
