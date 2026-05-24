# -*- coding: utf-8 -*-
"""2026-05-25 ぴあ・ステージ新着の一括追加（genre:new プール投入）。
既存フォーマット（6sp object / 12sp keys）を壊さず、EVENTS配列末尾に挿入する。
発売前で締切不明のものは startDate===date（発売日カウントダウン）＋ saleEndUnknown:true。
仮の締切日は一切置かない（発売日に締切を再確認する運用）。"""
import json, re

PIA = "https://t.pia.jp/pia/event/event.do?eventBundleCd="
PIAE = "https://t.pia.jp/pia/event/event.do?eventCd="

def pia(code):
    return (PIAE + code) if code[0].isdigit() else (PIA + code)

def L(pia_url=None, eplus=None):
    return {"rakuten": None, "lawson": None, "pia": pia_url, "eplus": eplus}

# (id, artist, name, date, dateLabel, venue, pref, price, links, tickets, saleEndUnknown)
raw = [
 (268,"花總まり／黒羽麻璃央／渡邉蒼 ほか","ミュージカル『AGATHA(アガサ)』(名古屋公演)","2026-08-16",
   "2026年8月15日(土)・16日(日) 名古屋","名古屋文理大学文化フォーラム 大ホール","愛知",None,
   L(pia("b2667204")),
   [{"type":"一般発売","startDate":"2026-05-30","date":"2026-05-30"}], True),

 (269,"望海風斗／坂本昌行 ほか","ミュージカル『ファニー・ガール』(大阪公演)","2026-10-18",
   "2026年10月9日〜18日 梅田芸術劇場メインホール","梅田芸術劇場メインホール","大阪",None,
   L(pia("b2667960")),
   [{"type":"一般発売(大阪)","startDate":"2026-07-11","date":"2026-07-11"}], True),

 (270,"山本耕史／ゆりやんレトリィバァ ほか","ミュージカル『フル・モンティ』(東京公演)","2026-09-07",
   "2026年8月19日〜9月7日 東京国際フォーラム ホールC","東京国際フォーラム ホールC","東京",None,
   L(pia("b2667308")),
   [{"type":"一般発売(東京)","startDate":"2026-06-06","date":"2026-06-06"}], True),

 (271,"凰稀かなめ／妃海風／彩凪翔／さくらまや ほか","舞台『TARKIE』","2026-09-06",
   "2026年8月22日〜30日(東京)／9月3日〜6日(大阪)","有楽町よみうりホール／COOL JAPAN PARK OSAKA TTホール","東京・大阪",None,
   L(pia("b2665501")),
   [{"type":"一般発売(東京)","startDate":"2026-07-25","date":"2026-07-25"},
    {"type":"一般発売(大阪)","startDate":"2026-07-25","date":"2026-07-25"}], True),

 (272,"市村正親","舞台『シークレットステージ』","2026-10-18",
   "2026年9月9日〜24日(東京)／10月17日〜18日(静岡)","東京建物ぴあシアター／三島市民文化会館","東京・静岡",None,
   L(pia("b2667799")),
   [{"type":"一般発売(東京)","startDate":"2026-06-10","date":"2026-06-10"},
    {"type":"一般発売(静岡)","startDate":"2026-06-27","date":"2026-06-27"}], True),

 (273,"美少女戦士セーラームーン","美少女戦士セーラームーン -Shining Theater-","2026-06-30",
   "2026年6月1日〜30日 品川プリンスホテル クラブeX","品川プリンスホテル クラブeX","東京",None,
   L(pia("b2665668")),
   [{"type":"6/1〜7公演","date":"2026-06-04"},
    {"type":"6/8〜14公演","date":"2026-06-11"},
    {"type":"6/15〜21公演","date":"2026-06-18"},
    {"type":"6/22〜28公演","date":"2026-06-25"},
    {"type":"6/29〜30公演","date":"2026-06-27"}], False),
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
