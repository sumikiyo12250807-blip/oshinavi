# -*- coding: utf-8 -*-
"""夜の便の取りこぼし潰し＝X投稿に出す組をぴあで総ざらいして見つけた未登録枠を、既存へ足す。

🚨投稿の誘導先は oshinavi.jp なので、着地したページに公演が欠けていたら
　わざわざ来た人が自分の推しを見つけられない（feedback_x_link_oshinavi_only の裏返し）。
🚨足す枠には必ず飛び先URLを焼き込む（feedback_tour_per_ticket_url）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

APPLY = "--apply" in sys.argv

# 構築した新id → 足す先の既存id
TO = {9001: 2538, 9002: 2538, 9003: 2538, 9004: 2538,
      9005: 5162, 9006: 5162,
      9007: 3732,
      9008: 6025,
      9009: 4173, 9010: 4173}

built = {e["id"]: e for e in json.load(open("tmp/built_x_0906.json", encoding="utf-8"))}

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e["id"]: e for e in EVENTS}


def pia(e):
    return ((e.get("links") or {}).get("pia") or "")


def venue_parts(v):
    if not v:
        return []
    mm = re.match(r"全国ツアー（(.+)）$", v)
    body = mm.group(1) if mm else v
    return [x for x in body.split("／") if x]


def join_venue(parts):
    parts = [p for i, p in enumerate(parts) if p not in parts[:i]]
    return parts[0] if len(parts) == 1 else "全国ツアー（%s）" % "／".join(parts)


DATE_RE = re.compile(r"(R9年\s*)?(\d{1,2})/(\d{1,2})")
import datetime


def last_show_date(ttype):
    mm = re.search(r"（[^（）]*?公演）", ttype or "")
    if not mm:
        return None
    seg, best, r9 = mm.group(0), None, False
    for hit in DATE_RE.finditer(seg):
        if hit.group(1):
            r9 = True
        try:
            d = datetime.date(2027 if r9 else 2026, int(hit.group(2)), int(hit.group(3)))
        except ValueError:
            continue
        if best is None or d > best:
            best = d
    return best.isoformat() if best else None


log = []
for nid, eid in TO.items():
    new, old = built.get(nid), byid.get(eid)
    if not new or not old:
        print("⚠️ 見つからない new=%s old=%s" % (nid, eid))
        continue
    url = pia(new)
    have = {(t.get("type"), t.get("date")) for t in (old.get("tickets") or [])}
    added = []
    for t in (new.get("tickets") or []):
        if (t.get("type"), t.get("date")) in have:
            continue
        t = dict(t)
        if not t.get("url"):
            t["url"] = url
        added.append(t)
    old["tickets"] = (old.get("tickets") or []) + added
    for t in old["tickets"]:
        if not t.get("url"):
            t["url"] = pia(old) or url
    ov, od = old.get("venue"), old.get("date")
    old["venue"] = join_venue(venue_parts(ov) + venue_parts(new.get("venue")))
    cands = [od, new.get("date")] + [last_show_date(t.get("type")) for t in old["tickets"]]
    old["date"] = max([c for c in cands if c])
    log.append((nid, eid, old.get("artist"), added, od, old["date"], ov, old["venue"], url))

for nid, eid, name, added, od, nd, ov, nv, url in log:
    print("→ 既存%-5d %s" % (eid, name))
    if od != nd:
        print("     公演日 %s → %s" % (od, nd))
    for t in added:
        print("     ＋枠 %s （〜%s）→ %s" % (t.get("type"), t.get("date"), t.get("url")))
    if not added:
        print("     ＋枠 なし（もう登録されていた）")

bad = []
for eid in set(TO.values()):
    e = byid[eid]
    nourl = [t.get("type") for t in (e.get("tickets") or []) if not t.get("url")]
    if nourl:
        bad.append((eid, nourl[:3]))
print("")
if bad:
    print("🚨 飛び先が空の枠がある＝止める: %s" % bad)
else:
    print("✅ 飛び先が空の枠はゼロ")

if APPLY:
    if bad:
        sys.exit(1)
    open("index.html.bak_0906_xaudit", "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    out = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
    open("index.html", "w", encoding="utf-8").write(out)
    with open("logs/xaudit_2026-09-06.md", "w", encoding="utf-8") as f:
        f.write("# X投稿の取りこぼし潰し 2026-09-06（夜の便）\n\n")
        f.write("投稿に名前を出す組を `pia_kw_search` で総ざらいし、登録に無い eventCd を炙り出して足した。\n")
        f.write("ツアーまとめページ(bundle)だけ見ない（feedback_pia_bundle_hides_shows）。\n\n")
        f.write("| 足した先 | 公演名 | 足した枠 | 公演日 | 確認用URL |\n|---|---|---|---|---|\n")
        for nid, eid, name, added, od, nd, ov, nv, url in log:
            if not added:
                continue
            f.write("| %d | %s | %d枠 | %s→%s | %s |\n"
                    % (eid, (name or "").replace("|", "／"), len(added), od, nd, url))
        f.write("\n## 取りこぼしではなかったもの（フェス出演・対バン・誤ヒット）\n")
        f.write("- chilldspot＝FIELDS SO GOOD 2026（フェス出演）\n")
        f.write("- WILD BLUE＝ポムフェス／AGESTOCK2026（フェス出演）\n")
        f.write("- LiLi＝ROCK IN AUTUMN／TOKYO CALLING（対バン・フェス）、フジコ・ヘミング上映は誤ヒット\n")
        f.write("- log you＝BEEEEM FES／PEAK SPOT JOIN（対バン）\n")
        f.write("- CHAPTERHOUSE／めろめろぱんち＝未登録ゼロ\n")
    print("書き込み完了 (backup: index.html.bak_0906_xaudit / logs/xaudit_2026-09-06.md)")
else:
    print("（--apply で書き込む）")
