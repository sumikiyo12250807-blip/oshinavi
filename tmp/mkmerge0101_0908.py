# -*- coding: utf-8 -*-
"""昼の便でやる「同名22件を既存へ統合する」入力を組み立てる（適用はしない）。

🚨 tmp/merge_apply_0905.py は built 側に date/dateLabel/venue/prefecture があると**上書きする**。
   候補1件ぶんの値をそのまま渡すと、ツアーの会場一覧や期間が候補1公演ぶんに縮む。
   だからここで **既存と候補の和集合** を作ってから渡す。
🚨 build_pia_entries は ticket.url を付けないことがあるので、投げた元URLを焼き込む
   （feedback_build_pia_multiurl_loses_ticket_url）。
出力＝tmp/merge0101_in.json（merge_apply_0905.py に渡す）と、目で見るための .md
"""
import io, re, json, datetime, collections

# 候補id → 足し先の既存id（エージェントの独立判定 B22件）
PAIRS = [
    # 受付中(0101)から拾った候補のうち、エージェントが「同じツアーの別窓」と判定したB18件
    (7337, 1601), (7346, 2606), (7354, 4366), (7360, 1236), (7362, 5846),
    (7374, 2867), (7377, 4883), (7381, 6923), (7383, 5781), (7385, 578),
    (7417, 4366), (7418, 3059), (7421, 2175), (7423, 3126), (7432, 5791),
    (7434, 3421), (7435, 3130), (7436, 5284),
]

WD = "月火水木金土日"


def jp(d):
    y, m, dd = int(d[:4]), int(d[5:7]), int(d[8:10])
    w = WD[datetime.date(y, m, dd).weekday()]
    return "%d年%d月%d日(%s)" % (y, m, dd, w)


def label_start(lbl):
    """dateLabel の先頭の日付を ISO で返す（無ければ None）"""
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", lbl or "")
    return "%04d-%02d-%02d" % tuple(map(int, m.groups())) if m else None


def venues(v):
    """venue から会場名の並びを取り出す。「全国ツアー（A／B）」→[A,B]、「A」→[A]"""
    v = (v or "").strip()
    if not v:
        return []
    m = re.match(r"^全国ツアー(?:（(.*)）)?$", v)
    if m:
        return [x.strip() for x in (m.group(1) or "").split("／") if x.strip()]
    return [v]


def prefs(p):
    """県の並びを返す。🚨「全国」は捨てない＝捨てると『全国ツアー』が
    候補1公演ぶんの県に縮んで嘘になる（2026-09-08 に下ごしらえで発見）。"""
    return [x.strip() for x in re.split(r"[・／/]", p or "") if x.strip()]


# 🚨 id1202 鶴は既存の venue が「全国ツアー」だけで会場一覧が空だった＝
#    そのまま統合すると候補の会場（梅田/札幌/苫小牧）しか並ばず、元の3会場が消える。
#    ぴあ(eventCd=2623323)から拾い直した実物をここで補う（2026-09-08）。
VENUE_FIX = {}

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))}
cand = {e["id"]: e for e in json.load(io.open("tmp/inject0101_addto.json", encoding="utf-8"))}
# 既存どうしを畳む場合は、足す側も現物(EV)から取る
for _i in ():
    if _i not in cand and _i in EV:
        cand[_i] = EV[_i]
srcurl = {c["newid"]: c["urls"][0] for c in json.load(io.open("tmp/cand0101_0908.json", encoding="utf-8"))}

by_target = collections.defaultdict(list)
for c_id, t_id in PAIRS:
    by_target[t_id].append(c_id)

out, rows, warns = [], [], []
for t_id, c_ids in sorted(by_target.items()):
    e = EV.get(t_id)
    if not e:
        warns.append("既存 id%d が現物に無い" % t_id)
        continue

    starts = [label_start(e.get("dateLabel")) or e.get("date")]
    ends = [e.get("date")]
    fix = VENUE_FIX.get(t_id)
    vs = venues(fix[0]) if fix else venues(e.get("venue"))
    ps = prefs(fix[1]) if fix else prefs(e.get("prefecture"))
    tickets = []
    for c_id in c_ids:
        c = cand.get(c_id)
        if not c:
            warns.append("候補 id%d がビルド結果に無い" % c_id)
            continue
        starts.append(label_start(c.get("dateLabel")) or c.get("date"))
        ends.append(c.get("date"))
        vs += venues(c.get("venue"))
        ps += prefs(c.get("prefecture"))
        u = srcurl.get(c_id) or (c.get("links") or {}).get("pia") or ""
        for t in (c.get("tickets") or []):
            t = dict(t)
            if not t.get("url"):
                t["url"] = u
            tickets.append(t)

    starts = [s for s in starts if s]
    ends = [d for d in ends if d]
    new_start, new_end = min(starts), max(ends)
    vs_uniq = list(dict.fromkeys([v for v in vs if v]))
    ps_uniq = list(dict.fromkeys(ps))

    # 会場が1つだけ／県が1つだけなら「全国ツアー」にしない（嘘になる）
    if len(vs_uniq) >= 2 or len(ps_uniq) >= 2:
        venue = "全国ツアー（%s）" % "／".join(vs_uniq) if vs_uniq else "全国ツアー"
        # 🚨片方でも「全国」なら「全国」のまま＝狭めない。3県以上も「全国」に寄せる
        pref = "全国" if ("全国" in ps_uniq or len(ps_uniq) >= 3) else "・".join(ps_uniq)
        tail = "全国ツアー"
    else:
        venue = vs_uniq[0] if vs_uniq else (e.get("venue") or "")
        pref = ps_uniq[0] if ps_uniq else (e.get("prefecture") or "")
        tail = pref
    label = "%s〜%s %s" % (jp(new_start), jp(new_end), tail) if new_start != new_end \
        else "%s %s" % (jp(new_end), tail)

    # 既存の会場一覧が空の「全国ツアー」だと、候補の会場だけ並べることになって片手落ち
    if not venues(e.get("venue")) and (e.get("venue") or "").startswith("全国ツアー"):
        warns.append("id%d は既存の会場一覧が空＝候補の会場だけが並ぶ。元の会場をぴあで拾い直すか要検討" % t_id)

    out.append({"id": t_id, "artist": e.get("artist"), "links": {},
                "date": new_end, "dateLabel": label, "venue": venue,
                "prefecture": pref, "tickets": tickets})
    rows.append((t_id, e.get("name"), c_ids, e.get("date"), new_end,
                 e.get("venue"), venue, e.get("prefecture"), pref, len(tickets)))

json.dump(out, io.open("tmp/merge0101_in.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

o = io.open("tmp/merge0101_in.md", "w", encoding="utf-8")
o.write("# 昼の便でやる統合の下ごしらえ（まだ当てていない）\n\n")
o.write("統合先 **%d件** ／ 足す枠 **%d枠**\n\n" % (len(out), sum(r[9] for r in rows)))
o.write("| 既存id | 公演名 | 足す候補 | 公演日 | 会場 | 県 | 足す枠 |\n|---|---|---|---|---|---|---|\n")
for t_id, name, c_ids, d0, d1, v0, v1, p0, p1, n in rows:
    o.write("| %d | %s | %s | %s→**%s** | %s→**%s** | %s→**%s** | %d |\n"
            % (t_id, (name or "")[:20], ",".join(map(str, c_ids)), d0, d1,
               (v0 or "")[:26], (v1 or "")[:40], p0, p1, n))
if warns:
    o.write("\n## ⚠️ 気をつける点\n\n")
    for w in warns:
        o.write("- %s\n" % w)
o.close()
print("targets=%d tickets=%d warns=%d -> tmp/merge0101_in.json / .md"
      % (len(out), sum(r[9] for r in rows), len(warns)))
