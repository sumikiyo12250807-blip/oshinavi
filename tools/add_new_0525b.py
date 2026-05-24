# -*- coding: utf-8 -*-
"""2026-05-25 追加分（要相談2件）。ウクライナ国立バレエ(全国ツアー)・淡路の月に誓う。
genre:new プール投入。日付は全て確定情報のみ（仮置きなし）。"""
import json, re

PIA = "https://t.pia.jp/pia/event/event.do?eventBundleCd="
PIAE = "https://t.pia.jp/pia/event/event.do?eventCd="

def pia(code):
    return (PIAE + code) if code[0].isdigit() else (PIA + code)

def L(pia_url=None, eplus=None):
    return {"rakuten": None, "lawson": None, "pia": pia_url, "eplus": eplus}

# (id, artist, name, date, dateLabel, venue, pref, price, links, tickets, saleEndUnknown)
raw = [
 (274,"ウクライナ国立バレエ","ウクライナ国立バレエ「スペシャル・セレクション2026」","2026-08-11",
   "2026年7月23日〜8月11日 全国ツアー（宮城〜兵庫ほか・愛知・千葉・鎌倉）","全国ツアー","全国",None,
   L(pia("b2667105")),
   [{"type":"愛知公演(7/26)","date":"2026-07-26"},
    {"type":"千葉公演(8/2)","date":"2026-07-30"},
    {"type":"全国ツアー(宮城〜兵庫)","date":"2026-08-05"},
    {"type":"鎌倉公演(8/11)","date":"2026-08-09"}], False),

 (275,"淡路の月に誓う","淡路の月に誓う","2026-08-23",
   "2026年7月18日〜8月23日 青海波 波乗亭","青海波 波乗亭","兵庫",None,
   L(pia("2620719")),
   [{"type":"一般発売","startDate":"2026-07-18","date":"2026-08-22"}], False),
]

def build(e):
    eid, artist, name, date, dateLabel, venue, pref, price, links, tickets, seu = e
    o = {"id": eid, "artist": artist, "name": name, "date": date, "dateLabel": dateLabel,
         "venue": venue, "prefecture": pref, "genre": "new", "price": price,
         "links": links, "tickets": tickets, "showSalePeriod": True}
    if seu:
        o["saleEndUnknown"] = True
    o["verified"] = True
    o["verifiedAt"] = "2026-05-25"
    s = json.dumps(o, ensure_ascii=False, indent=6)
    return "\n".join("      " + ln for ln in s.split("\n"))

entries = [build(e) for e in raw]
block = ",\n".join(entries)

path = "index.html"
t = open(path, encoding="utf-8").read()
m = re.search(r"const\s+EVENTS\s*=\s*(\[)", t)
s = m.start(1); d = 0
for i in range(s, len(t)):
    if t[i] == "[": d += 1
    elif t[i] == "]":
        d -= 1
        if d == 0:
            e_idx = i; break
last_brace = t.rfind("}", 0, e_idx)
insert_pos = last_brace + 1
new_t = t[:insert_pos] + ",\n" + block + t[insert_pos:]

# validate
m2 = re.search(r"const\s+EVENTS\s*=\s*(\[)", new_t)
s2 = m2.start(1); d = 0
for i in range(s2, len(new_t)):
    if new_t[i] == "[": d += 1
    elif new_t[i] == "]":
        d -= 1
        if d == 0:
            e2 = i + 1; break
arr = json.loads(new_t[s2:e2])
print("挿入後 件数 =", len(arr))
ids = [x["id"] for x in arr]
assert len(ids) == len(set(ids)), "重複ID発生!"
open(path, "w", encoding="utf-8").write(new_t)
print("書き込み完了。新規", len(raw), "件追加。max id =", max(ids))
