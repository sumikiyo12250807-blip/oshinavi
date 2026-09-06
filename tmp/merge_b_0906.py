# -*- coding: utf-8 -*-
"""B型＝同じツアーなのに別エントリになっている7組を畳む。

畳まないもの（別興行なので触らない）:
  7067 OZアカデミー女子プロレス（2027/1/10）と 2704（2026/11/7）＝別の大会
  7069 K-1 WORLD MAX 2026（12/29 横浜）と 2560（9/12 代々木）＝別の大会
  7071 センダイガールズ<大阪大会>（12/19）と 4934（11/1）＝別の大会

やること
1. 新側にしか無い枠を既存へ足す。🚨足す枠には飛び先URLを必ず入れる
   （新側の ticket.url →無ければ新側エントリの links.pia）
2. 会場を「全国ツアー（A／B／…）」の形で足し合わせる（重複は消す・順番は既存が先）
3. 🚨公演日(date)を、登録されている枠の券種名から千秋楽を割り出して直す
   ＝「（東京 12/11公演）」「（愛知 R9年 1/17公演）」を読む。
   これをやらないと、チケットがまだ売っているのに翌朝カードごと消える（今朝483羊文学で実際に起きた）
4. 新側を EVENTS と NEW_ORDER から外す（欠番。idは振り直さない）
"""
import json
import re
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

TODAY = "2026-09-06"
APPLY = "--apply" in sys.argv

# 新id → 残す既存id
# 🚨7027 柴田聡子は外した＝ぴあの実ページ（2628364／2628529）どちらにも**ツアー名の記載が無く**、
#   大阪11/11と東京11/27が同じツアーだと証明できなかった。推測で畳まない。
PAIRS = [(7041, 4052), (7042, 4040), (7043, 4040), (7044, 4040),
         (7051, 3750), (7077, 3635), (7078, 3635), (7097, 6151),
         (7098, 6550)]

h = open("index.html", encoding="utf-8").read()
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


# 「（東京 12/11公演）」「（岩手 R9年 1/17公演）」「（神奈川 11/12〜11/15公演）」から
# いちばん後ろの公演日を取る。R9年＝2027年。
DATE_RE = re.compile(r"(R9年\s*)?(\d{1,2})/(\d{1,2})")


def last_show_date(ttype):
    mm = re.search(r"（[^（）]*?公演）", ttype or "")
    if not mm:
        return None
    seg = mm.group(0)
    best = None
    r9 = False
    for hit in DATE_RE.finditer(seg):
        if hit.group(1):
            r9 = True
        mo, dd = int(hit.group(2)), int(hit.group(3))
        year = 2027 if r9 else 2026
        try:
            d = datetime.date(year, mo, dd)
        except ValueError:
            continue
        if best is None or d > best:
            best = d
    return best.isoformat() if best else None


def venue_parts(v):
    if not v:
        return []
    mm = re.match(r"全国ツアー（(.+)）$", v)
    body = mm.group(1) if mm else v
    return [x for x in body.split("／") if x]


def join_venue(parts):
    parts = [p for i, p in enumerate(parts) if p not in parts[:i]]
    if len(parts) == 1:
        return parts[0]
    return "全国ツアー（%s）" % "／".join(parts)


drop = set()
log = []
for nid, eid in PAIRS:
    new, old = byid.get(nid), byid.get(eid)
    if not new or not old:
        print("⚠️ 見つからない new=%s old=%s" % (nid, eid))
        continue
    newurl = pia(new)
    have = {(t.get("type"), t.get("date")) for t in (old.get("tickets") or [])}
    added = []
    for t in (new.get("tickets") or []):
        if (t.get("type"), t.get("date")) in have:
            continue
        t = dict(t)
        if not t.get("url"):
            t["url"] = newurl
        added.append(t)
    old["tickets"] = (old.get("tickets") or []) + added
    for t in old["tickets"]:
        if not t.get("url"):
            t["url"] = pia(old) or newurl
    oldvenue = old.get("venue")
    old["venue"] = join_venue(venue_parts(oldvenue) + venue_parts(new.get("venue")))
    olddate = old.get("date")
    cands = [olddate, new.get("date")]
    for t in old["tickets"]:
        d = last_show_date(t.get("type"))
        if d:
            cands.append(d)
    old["date"] = max([c for c in cands if c])
    drop.add(nid)
    log.append((nid, eid, new.get("artist"), added, olddate, old["date"], oldvenue, old["venue"]))

for nid, eid, name, added, od, nd, ov, nv in log:
    print("新%-5d → 既存%-5d  %s" % (nid, eid, name))
    if od != nd:
        print("      公演日 %s → %s（千秋楽を券種名から取り直した）" % (od, nd))
    if ov != nv:
        print("      会場   %s" % nv[:100])
    for t in added:
        print("      ＋枠 %s （〜%s）→ %s" % (t.get("type"), t.get("date"), t.get("url")))
    if not added:
        print("      ＋枠 なし（同じ枠が既に登録済み＝URLの別名だっただけ）")

# 検算＝畳んだ後に、両側の「画面に出る枠」の (券種名, 締切) の和集合が全部残っているか
bad = []
for nid, eid in PAIRS:
    if nid not in byid or eid not in byid:
        continue
    after = {(t.get("type"), t.get("date")) for t in (byid[eid].get("tickets") or []) if visible(t)}
    nourl = [t.get("type") for t in (byid[eid].get("tickets") or []) if visible(t) and not t.get("url")]
    if nourl:
        bad.append((nid, eid, "飛び先が空の枠: " + str(nourl[:3])))

print("")
if bad:
    print("🚨 止める")
    for x in bad:
        print("   ", x)
else:
    print("✅ 飛び先が空の枠はゼロ")

kept = [e for e in EVENTS if e["id"] not in drop]
print("EVENTS %d件 → %d件（%d件を欠番に）" % (len(EVENTS), len(kept), len(drop)))

if APPLY:
    if bad:
        sys.exit(1)
    open("index.html.bak_0906_mergeB", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(kept, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    mo = re.search(r"(  const NEW_ORDER = \[)([^\]]*)(\];)", out)
    ids = [int(x) for x in mo.group(2).replace("\n", "").split(",") if x.strip()]
    left = [i for i in ids if i not in drop]
    out = out[:mo.start()] + mo.group(1) + ", ".join(str(i) for i in left) + mo.group(3) + out[mo.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    with open("logs/merged_2026-09-06.md", "a", encoding="utf-8") as f:
        f.write("\n\n## B型（同じツアーが別エントリに割れていた）\n\n")
        f.write("| 欠番にした新id | 残した既存id | 公演名 | 足した枠 | 公演日 | 確認用URL |\n|---|---|---|---|---|---|\n")
        for nid, eid, name, added, od, nd, ov, nv in log:
            f.write("| %d | %d | %s | %d枠 | %s→%s | %s |\n"
                    % (nid, eid, (name or "").replace("|", "／"), len(added), od, nd,
                       pia(byid[eid])))
        f.write("\n### 畳まなかったもの（別興行）\n")
        f.write("- 7067 OZアカデミー女子プロレス（2027/1/10 横浜産貿ホール）と 2704（2026/11/7 ラジアントホール）\n")
        f.write("- 7069 K-1 WORLD MAX 2026（12/29 横浜BUNTAI）と 2560（9/12 代々木第二）\n")
        f.write("- 7071 センダイガールズ＜大阪大会＞（12/19 アゼリア大正）と 4934（11/1 176BOX）\n")
        f.write("- 7027 柴田聡子（大阪11/11）と 4233（東京11/27）\n")
        f.write("  ＝ぴあの実ページ（2628364／2628529）どちらにもツアー名の記載が無く、\n")
        f.write("  同じツアーだと証明できなかったので畳まなかった。\n")
        f.write("  🚨あわせて発見＝4233 は ぴあに「プレリザーブ」があるのに登録は一般発売の1枠だけ＝取りこぼし。\n")
    print("書き込み完了 (backup: index.html.bak_0906_mergeB / logs/merged_2026-09-06.md に追記)")
else:
    print("（--apply で書き込む）")
