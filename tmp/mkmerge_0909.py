# -*- coding: utf-8 -*-
"""総ざらいで出た4枠を、merge_apply_0905.py に食わせる形（＝統合先idの入力）に組み替える。

🚨merge_apply は date/dateLabel/venue/prefecture を**渡した値でそのまま置き換える**。
   だからここで「既存 ∪ 新規」を作っておかないと、ツアーの会場一覧が1会場に縮んで嘘になる
   （2026-09-08に「全国」を捨てて鶴が大阪・北海道に縮んだのと同じ事故）。
🚨ticket の url は必ず埋める（feedback_tour_per_ticket_url／
   feedback_build_pia_multiurl_loses_ticket_url＝build は2本目以降 url を付けない）。
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

MAP = {90001: 3422, 90003: 4103, 90005: 3471, 90006: 579}

built = {e["id"]: e for e in json.load(io.open("tmp/pri_built_0909.json", encoding="utf-8"))}
s = io.open("index.html", encoding="utf-8").read()
evs = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", s, re.S).group(1))
by = {e["id"]: e for e in evs}


def venue_union(old, new):
    if not new or new in old:
        return old
    m = re.match(r"^全国ツアー（(.+)）$", old)
    inner = m.group(1) if m else old
    return "全国ツアー（%s／%s）" % (inner, new)


def pref_union(old, new):
    """🚨3つ以上は「全国」。ここで県を1つに縮めると全国ツアーが嘘になる。"""
    if old == "全国":
        return "全国"
    ps, seen = [], set()
    for x in re.split(r"[・／/]", old or "") + [new or ""]:
        x = x.strip()
        if x and x not in seen:
            seen.add(x); ps.append(x)
    return "全国" if len(ps) >= 3 else "・".join(ps)


out = []
for nid, tid in sorted(MAP.items()):
    b, e = built[nid], by[tid]
    pia = (b.get("links") or {}).get("pia")
    assert pia, nid

    tks = []
    for t in b.get("tickets") or []:
        t = dict(t)
        if not t.get("url"):
            t["url"] = pia               # 🚨会場別ぴあURLを焼き込む
        tks.append(t)

    # 公演日は千秋楽（遅いほう）。dateLabel も遅いほうに合わせる
    if (b.get("date") or "") > (e.get("date") or ""):
        date, label = b["date"], b.get("dateLabel")
        head = re.match(r"^(\d{4}年\d{1,2}月\d{1,2}日\(.\))", e.get("dateLabel") or "")
        tail = re.match(r"^(\d{4}年\d{1,2}月\d{1,2}日\(.\))", b.get("dateLabel") or "")
        # 🚨単独会場だったエントリに別会場を足したら、dateLabel も「初日〜千秋楽 全国ツアー」にする
        #   （新しい1公演だけの表記にすると、元の公演が消えたように見える）
        if head and tail:
            label = "%s〜%s 全国ツアー" % (head.group(1), tail.group(1))
    else:
        date, label = e["date"], e["dateLabel"]

    out.append({
        "id": tid,
        "date": date,
        "dateLabel": label,
        "venue": venue_union(e.get("venue") or "", b.get("venue") or ""),
        "prefecture": pref_union(e.get("prefecture") or "", b.get("prefecture") or ""),
        "links": {"pia": (e.get("links") or {}).get("pia") or pia},   # 既存の親URLを守る
        "tickets": tks,
    })

io.open("tmp/merge_built_0909.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))

for o in out:
    print("id%-5s 公演日=%s" % (o["id"], o["date"]))
    print("   dateLabel=%s" % o["dateLabel"])
    print("   venue=%s" % o["venue"])
    print("   県=%s" % o["prefecture"])
    for t in o["tickets"]:
        print("   + %s | %s" % (t["type"], t["url"]))
