# -*- coding: utf-8 -*-
"""e+から2件ぶんを入れる（2026-09-05）。値はすべて tools/eplus_detail.py の機械パース結果から。

A) id1613 THE GOOD-BYE ＝ 千秋楽が 9/6静岡 だったので公演日を直し、静岡9/6の枠を足す。
   実ページ https://eplus.jp/sf/detail/0084690001
     ▼2026/9/6(日) SOUND SHOWER ark（静岡県）
       予定枚数終了 | 先着 ★一般発売 | 受付 2026/7/26 10:00〜2026/9/5(土)18:00
   → 売り切れは消さずに「予定枚数終了」で出す（soldout:true・saleEnded は付けない）

B) THE BACK HORN presents 後角祭 -koukakusai- ＝ 新規（genre:"new"）。
   実ページ https://eplus.jp/sf/detail/0030840001-P0030624P021001 / ...002
     ▼2026/11/14(土) 郡山HIP SHOT JAPAN（福島県） 受付中 | 抽選 ◆<14日公演>プレイガイド最速先行
     ▼2026/11/15(日) 同上                        受付中 | 抽選 ◆<15日公演>プレイガイド最速先行
       どちらも受付 2026/9/3(木)18:00〜2026/9/13(日)23:59
   → 同じ会場の連日公演なので1エントリにまとめる（feedback_tour_consolidate）

🚨 読み書きは newline 未指定（テキストモード往復）＝CRLF を壊さない。
"""
import json, re, datetime

PATH = "index.html"
TODAY = datetime.date.today().isoformat()

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

# ---- A) id1613 ----
e = by[1613]
assert e["date"] == "2026-09-04", e["date"]
e["date"] = "2026-09-06"
e["dateLabel"] = "2026年8月26日(水)〜2026年9月6日(日) 愛知・大阪・神奈川・静岡"
v = e.get("venue") or ""
mv = re.match(r"全国ツアー（(.*)）$", v)
vs = mv.group(1).split("／") if mv else [v]
if "SOUND SHOWER ark" not in vs:
    vs.append("SOUND SHOWER ark")
e["venue"] = "全国ツアー（" + "／".join(vs) + "）"
e["prefecture"] = "愛知・大阪・神奈川・静岡"
e.setdefault("links", {})["eplus"] = "https://eplus.jp/sf/detail/0084690001"
e["tickets"].append({
    "type": "一般発売（静岡県 9/6公演）〜9/5 18:00",
    "date": "2026-09-05",
    "soldout": True,
    "soldoutSince": TODAY,
    "url": "https://eplus.jp/sf/detail/0084690001",
})
e["verified"] = True
e["verifiedAt"] = TODAY

# ---- B) 後角祭（新規） ----
nid = max(x["id"] for x in events) + 1
kk = {
    "id": nid,
    "artist": "THE BACK HORN",
    "name": "THE BACK HORN presents 後角祭 -koukakusai-",
    "date": "2026-11-15",
    "dateLabel": "2026年11月14日(土)〜2026年11月15日(日) 福島 郡山HIP SHOT JAPAN",
    "venue": "郡山HIP SHOT JAPAN",
    "prefecture": "福島",
    "genre": "new",
    "_genre": "rock",
    "_extraGenres": [],
    "_piaSub": None,
    "price": None,
    "links": {
        "rakuten": None, "lawson": None, "pia": None,
        "eplus": "https://eplus.jp/sf/detail/0030840001-P0030624P021001", "amazon": None,
    },
    "tickets": [
        {"type": "抽選プレイガイド最速先行（福島県 11/14公演）〜9/13 23:59",
         "date": "2026-09-13",
         "url": "https://eplus.jp/sf/detail/0030840001-P0030624P021001"},
        {"type": "抽選プレイガイド最速先行（福島県 11/15公演）〜9/13 23:59",
         "date": "2026-09-13",
         "url": "https://eplus.jp/sf/detail/0030840001-P0030624P021002"},
    ],
    "verified": True,
    "verifiedAt": TODAY,
}
events.append(kk)

# NEW_ORDER に新しい id を足す（投入順＝id昇順で固定）
m2 = re.search(r"(const NEW_ORDER = )(\[.*?\])(;)", h, re.S)
order = json.loads(m2.group(2))
if nid not in order:
    order.append(nid)
order = sorted(order)

bak = "index.html.bak_%s_eplus" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
body = h[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
m2b = re.search(r"(const NEW_ORDER = )(\[.*?\])(;)", body, re.S)
body = body[:m2b.start()] + m2b.group(1) + json.dumps(order, ensure_ascii=False) + m2b.group(3) + body[m2b.end():]
open(PATH, "w", encoding="utf-8").write(body)
print("id1613 date=%s 枠=%d / 後角祭 id=%d 枠=%d / NEW_ORDER=%d / backup=%s"
      % (by[1613]["date"], len(by[1613]["tickets"]), nid, len(kk["tickets"]), len(order), bak))
