# -*- coding: utf-8 -*-
"""A型15件を畳む＝「同じ公演日・同じ会場なのに、ぴあのeventCdが別」だけの重複。

やること
1. 新側(7025..7098)の枠のうち、既存に無いもの((type,date)で判定)を既存へ足す
2. 🚨足す枠に url が無ければ、新側のぴあURLを焼き込む
   （feedback_tour_per_ticket_url＝畳む前に url 空の枠へカードリンクを入れる。
     入れないと、畳んだ瞬間その枠の飛び先が消える）
3. 新側のエントリを EVENTS と NEW_ORDER から外す（＝欠番。id は振り直さない）
4. 前後で「画面に出る枠」の数が減っていないことを機械で確認する
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

TODAY = "2026-09-06"
APPLY = "--apply" in sys.argv

plan = json.load(open("tmp/merge_plan_0906.json", encoding="utf-8"))
PAIRS = [tuple(x) for x in plan["A"]]

h = open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e["id"]: e for e in EVENTS}


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


def pia(e):
    return ((e.get("links") or {}).get("pia") or "")


# 重複を畳むので「足し算」では見ない。画面に出る枠の (券種名, 締切) の**和集合**が
# 畳んだ後も全部残っているかで見る（feedback_dedup_badges_keeps_urls と同じ考え方）。
before = {}
for nid, eid in PAIRS:
    before[eid] = {(t.get("type"), t.get("date"))
                   for t in (byid[eid].get("tickets") or []) if visible(t)}
    before[nid] = {(t.get("type"), t.get("date"))
                   for t in (byid[nid].get("tickets") or []) if visible(t)}

drop = set()
log = []
for nid, eid in PAIRS:
    new, old = byid[nid], byid[eid]
    newurl = pia(new)
    have = {(t.get("type"), t.get("date")) for t in (old.get("tickets") or [])}
    added = []
    for t in (new.get("tickets") or []):
        if (t.get("type"), t.get("date")) in have:
            continue
        t = dict(t)
        if not t.get("url"):
            t["url"] = newurl            # 飛び先を焼き込んでから畳む
        added.append(t)
    old["tickets"] = (old.get("tickets") or []) + added
    # 既存側の url 空の枠にも、既存のぴあURLを焼いておく（畳んだ後に飛び先が無い枠を作らない）
    for t in old["tickets"]:
        if not t.get("url"):
            t["url"] = pia(old) or newurl
    drop.add(nid)
    log.append((nid, eid, new.get("artist"), added, newurl, pia(old)))

for nid, eid, name, added, nu, ou in log:
    print("新%-5d → 既存%-5d  %s" % (nid, eid, name))
    if added:
        for t in added:
            print("      ＋枠 %s （〜%s）→ %s" % (t.get("type"), t.get("date"), t.get("url")))
    else:
        print("      ＋枠 なし（同じ枠が既に登録済み）")

kept = [e for e in EVENTS if e["id"] not in drop]

print("")
bad = []
for nid, eid in PAIRS:
    after = {(t.get("type"), t.get("date"))
             for t in (byid[eid].get("tickets") or []) if visible(t)}
    want = before[eid] | before[nid]
    missing = want - after
    if missing:
        bad.append((nid, eid, missing))
    # 飛び先が空の枠が残っていないかも見る
    nourl = [t.get("type") for t in (byid[eid].get("tickets") or [])
             if visible(t) and not t.get("url")]
    if nourl:
        bad.append((nid, eid, {("url空", x) for x in nourl}))
if bad:
    print("🚨 畳むと消える枠／飛び先の無い枠がある＝止める")
    for nid, eid, missing in bad:
        for x in missing:
            print("   新%d→既存%d  %s" % (nid, eid, x))
else:
    print("✅ 画面に出る枠の (券種名, 締切) は和集合が全部残っている／飛び先が空の枠もゼロ")

print("EVENTS %d件 → %d件（%d件を欠番に）" % (len(EVENTS), len(kept), len(drop)))

if APPLY:
    if bad:
        print("中止：枠が減るので書き込まない")
        sys.exit(1)
    open("index.html.bak_0906_mergeA", "w", encoding="utf-8", newline="").write(h)
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
    left = [i for i in ids if i not in drop]
    out = out[:mo.start()] + mo.group(1) + ", ".join(str(i) for i in left) + mo.group(3) + out[mo.end():]
    open("index.html", "w", encoding="utf-8", newline="").write(out)
    with open("logs/merged_2026-09-06.md", "w", encoding="utf-8") as f:
        f.write("# 統合 2026-09-06（昼の便・A型）\n\n")
        f.write("「同じ公演日・同じ会場なのに、ぴあの eventCd が別」だけの重複を畳んだ。\n")
        f.write("畳む前に、url が空の枠へカードリンクを焼き込んでいる（feedback_tour_per_ticket_url）。\n\n")
        f.write("| 欠番にした新id | 残した既存id | 公演名 | 足した枠 | 確認用URL |\n|---|---|---|---|---|\n")
        for nid, eid, name, added, nu, ou in log:
            f.write("| %d | %d | %s | %d枠 | %s |\n"
                    % (nid, eid, (name or "").replace("|", "／"), len(added), ou or nu))
    print("書き込み完了 (backup: index.html.bak_0906_mergeA / logs/merged_2026-09-06.md)")
else:
    print("（--apply で書き込む）")
