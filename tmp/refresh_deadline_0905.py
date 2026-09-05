# -*- coding: utf-8 -*-
"""ビルド結果を使って、既存枠の「締切だけ」を取り直す。

🚨 何を直すか＝**同じ枠なのに、登録が「発売前の形」のまま取り残されている**もの。
   例（2026-09-05 id3818）:
     登録   poco会員限定先行販売（東京 12/28公演）**9/4 11:00発売**   締切=2026-09-04 開始=2026-09-04
     実ページ poco会員限定先行販売（東京 12/28公演）**〜9/17 23:59**  ＝9/4に発売開始して受付中
   締切が過去なので**画面に出ない**＝買えるのに載っていない状態。

🚨 やるのは「同じ (券種の基底名, 飛び先URL) の枠」の **type と date の入れ替えだけ**。
   枠は増やさない・減らさない・URLは触らない（[[feedback_build_pia_multiurl_loses_ticket_url]]
   の「置換は枠を殺す」を踏まないため、対象を1枠単位に限定する）。

使い方:
  python tmp/refresh_deadline_0905.py <built.json> [<built.json> ...]           # 差分を見るだけ
  python tmp/refresh_deadline_0905.py <built.json> ... --apply
"""
import json, re, io, sys, datetime

PATH = "index.html"
TODAY = datetime.date.today().isoformat()
RE_SALE = re.compile(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$")   # 発売前の形
RE_END = re.compile(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$")      # 販売中の形


def base(ty):
    ty = RE_END.sub("", ty or "")
    ty = RE_SALE.sub("", ty)
    return ty.strip()


srcs = [a for a in sys.argv[1:] if not a.startswith("--")]
built = {}
for s in srcs:
    for e in json.load(io.open(s, encoding="utf-8")):
        built.setdefault(e["id"], []).extend(e.get("tickets") or [])

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

buf, todo = [], []
for i, tks in sorted(built.items()):
    e = by.get(i)
    if not e:
        continue
    # ビルド側の枠を (基底名, url) で引けるようにする。
    # 「販売中の形（〜M/D）」を優先し、無ければ「発売前の形（M/D発売）」も採る
    # （次の先行が発売前で開いていることがある＝2026-09-05 id4325 / id4839）。
    idx = {}
    for nt in tks:
        k = (base(nt.get("type")), (nt.get("url") or "").strip())
        if k not in idx or RE_END.search(nt.get("type") or ""):
            idx[k] = nt
    # 🚨現物側に「販売中の形」が既にある (基底名, url) は触らない。
    #   更新すると**完全に同じ枠が2枚**になる（2026-09-05 id2254 杉山清貴で気づいた＝
    #   「発売前の形」と「販売中の形」が両方残っている重複の残骸。あれは別途、実ページを見て片方を消す）。
    have_live = {(base(t.get("type")), (t.get("url") or "").strip())
                 for t in (e.get("tickets") or []) if RE_END.search(t.get("type") or "")}
    # 現物側で「締切が今日以降＝画面に出ている」枠の (基底名, url)
    live_now = {(base(t.get("type")), (t.get("url") or "").strip())
                for t in (e.get("tickets") or []) if (t.get("date") or "") >= TODAY}
    for t in e.get("tickets") or []:
        ty = t.get("type") or ""
        key = (base(ty), (t.get("url") or "").strip())
        is_pre = bool(RE_SALE.search(ty))
        # 🚨対象は2つ：
        #   ① 「発売前の形」のまま取り残された枠（締切=startDate で画面に出ない）
        #   ② 「販売中の形」だが**締切が過去**の枠＝次の先行が開いているのに古い締切のまま
        #      （2026-09-05 実例＝id4079 Eve/4117 RAINCOVER/4415 Tohji ほか6件。
        #       ぴあの「オフィシャル4次先行」「セブン-イレブン先行」が kenshu で「先行」に潰れるので、
        #       券種名が既存と同じになり merge_apply が「既にある」と判定して更新できない）
        if not is_pre and (t.get("date") or "") >= TODAY:
            continue                       # 今も画面に出ている枠は触らない
        if is_pre and key in have_live:
            buf.append("SKIP id=%-5s %s ← 同じ枠の「販売中の形」が既にある（重複になるので触らない）" % (i, ty))
            continue
        if not is_pre and key in live_now:
            buf.append("SKIP id=%-5s %s ← 同じ枠で締切が未来のものが既にある" % (i, ty))
            continue
        nt = idx.get(key)
        if not nt:
            continue
        if (t.get("date") or "") >= (nt.get("date") or ""):
            continue                       # 既に新しい／同じなら触らない
        if (nt.get("date") or "") < TODAY:
            continue                       # 取り直しても過去なら意味がない
        buf.append("id=%-5s %s" % (i, e.get("name", "")[:40]))
        buf.append("    旧 %s  (締切=%s 開始=%s 画面=%s)"
                   % (ty, t.get("date"), t.get("startDate"),
                      "出ない" if (t.get("date") or "") < TODAY else "出る"))
        buf.append("    新 %s  (締切=%s)" % (nt.get("type"), nt.get("date")))
        todo.append((t, nt))

buf.append("")
buf.append("締切を取り直す枠: %d" % len(todo))
io.open("tmp/refresh_deadline_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("REFRESH=%d -> tmp/refresh_deadline_0905.txt" % len(todo))

if "--apply" not in sys.argv or not todo:
    raise SystemExit(0)

for t, nt in todo:
    t["type"] = nt["type"]
    t["date"] = nt["date"]
    # 発売前の形（M/D発売）なら startDate が要る＝カウントダウンの起点。
    # 販売中の形（〜M/D）なら要らないので落とす。
    if nt.get("startDate"):
        t["startDate"] = nt["startDate"]
    else:
        t.pop("startDate", None)

bak = "index.html.bak_%s_refreshdl" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
open(PATH, "w", encoding="utf-8").write(
    h[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print("APPLIED slots=%d backup=%s" % (len(todo), bak))
