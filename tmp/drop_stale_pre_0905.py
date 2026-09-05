# -*- coding: utf-8 -*-
"""同じ販売枠が「発売前の形」と「販売中の形」で2枚あるとき、**発売前の形**を落とす。

🚨 落とす条件は3つ全部を満たすときだけ（1つでも欠けたら触らない）:
   ① 券種の基底名（日付部分を除いた文字列）が同じ
   ② **締切（date）が同じ**  ← ここが安全弁
   ③ 片方が「M/D発売」形、もう片方が「〜M/D」形

   ②が要る理由＝通年券は「〜11/30 12:00」と「12/1 0:00発売」のように
   **締切が違う正しい2枚**（次の販売期間）がある。締切を見ないとこれを消してしまう
   （id2388 名古屋港水族館／id2395 二十四の瞳映画村／id5496 ガーデンミュージアム比叡）。

🚨 url は見ない（同じ枠を「県別に分けた版」と「まとめた版」で持っていることがあり、
   まとめ版だけ url が無い＝id6136 呪術廻戦の型）。代わりに**落とす側に url が無いか**を条件にする。

使い方:
  python tmp/drop_stale_pre_0905.py            # 差分を見るだけ
  python tmp/drop_stale_pre_0905.py --apply
"""
import re, json, io, sys, datetime

PATH = "index.html"
TODAY = datetime.date.today().isoformat()
RE_SALE = re.compile(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$")
RE_END = re.compile(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$")


def base(ty):
    ty = RE_END.sub("", ty or "")
    ty = RE_SALE.sub("", ty)
    return ty.strip()


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))

buf, n_drop, n_entry = [], 0, 0
for e in events:
    tks = e.get("tickets") or []
    # 「販売中の形」を (基底名, 締切) で引く
    live = {}
    for t in tks:
        if RE_END.search(t.get("type") or ""):
            live.setdefault((base(t.get("type")), t.get("date")), []).append(t)
    drop = []
    for t in tks:
        ty = t.get("type") or ""
        if not RE_SALE.search(ty):
            continue
        peers = live.get((base(ty), t.get("date")))
        if not peers:
            continue
        u = (t.get("url") or "").strip()
        # 落としてよいのは2つの場合だけ：
        #   ① 落とす側に飛び先が無い（＝残る側の url があれば導線は失われない）
        #   ② 落とす側と残る側の飛び先が同じ（＝完全に同じ枠）
        # 飛び先が違うなら別の売り場なので触らない（[[feedback_dedup_badges_keeps_urls]]）
        same_url = [p for p in peers if (p.get("url") or "").strip() == u]
        if not u:
            drop.append((t, peers[0]))
        elif same_url:
            drop.append((t, same_url[0]))
    if not drop:
        continue
    keep = [t for t in tks if t not in [d[0] for d in drop]]
    vb, va = sum(1 for t in tks if visible(t)), sum(1 for t in keep if visible(t))
    n_entry += 1
    n_drop += len(drop)
    buf.append("■ id=%-5s %s   枠 %d→%d ／ 画面 %d→%d" % (e["id"], e.get("name", "")[:38], len(tks), len(keep), vb, va))
    for t, peer in drop:
        buf.append("    落とす: %s  （締切=%s url=なし）" % (t.get("type"), t.get("date")))
        buf.append("    残る  : %s  （締切=%s url=%s）" % (peer.get("type"), peer.get("date"), peer.get("url") or "なし"))
    e["_drop"] = drop
    e["_keep"] = keep

buf.append("")
buf.append("落とす枠 %d / エントリ %d件" % (n_drop, n_entry))
io.open("tmp/drop_stale_pre_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("DROP=%d entries=%d -> tmp/drop_stale_pre_0905.txt" % (n_drop, n_entry))

if "--apply" not in sys.argv or not n_drop:
    raise SystemExit(0)

for e in events:
    if "_keep" in e:
        e["tickets"] = e.pop("_keep")
        e.pop("_drop", None)

bak = "index.html.bak_%s_dropstalepre" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
open(PATH, "w", encoding="utf-8").write(
    h[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print("APPLIED drop=%d backup=%s" % (n_drop, bak))
