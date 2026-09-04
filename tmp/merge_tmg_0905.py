# -*- coding: utf-8 -*-
"""TMG のツアーが2エントリに割れていたのを1本にまとめる。

- id6546 は bundle(b2669128) を機械パースし直した内容へ更新（4会場6公演・千秋楽 2026-10-21）。
  reconcile の ❌QC-EVDATE「ev.date=2026-10-09 が千秋楽2026-10-21より古い＝画面から消える」の修正。
- id6547（福岡10/17の単独ページ eventCd=2618474）は 6546 に含まれるので削除。
  🚨 畳む前に、6546 の福岡10/17枠へ 6547 の個別URLを焼き込む（feedback_tour_per_ticket_url＝
     枠数だけ見ても飛び先の破壊は見えない）。

🚨 読み書きは newline 未指定（テキストモード往復）。CRLF を壊さない。
"""
import json, re, datetime

PATH = "index.html"
BUILT = "tmp/built_6546_0905.json"

built = {e["id"]: e for e in json.load(open(BUILT, encoding="utf-8"))}[6546]

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

e46, e47 = by[6546], by[6547]
url47 = (e47.get("links") or {}).get("pia") or ""
assert "2618474" in url47, url47

# 6546 を作り直した内容へ（下書きジャンルとフラグは既存のものを残す）
keep = {k: e46.get(k) for k in ("genre", "_genre", "_extraGenres", "_piaSub", "price", "verified")}
for f in ("name", "artist", "date", "dateLabel", "venue", "prefecture", "tickets"):
    e46[f] = built[f]
for k, v in keep.items():
    if v is not None:
        e46[k] = v
if built.get("links", {}).get("amazon") and not (e46.get("links") or {}).get("amazon"):
    e46.setdefault("links", {})["amazon"] = built["links"]["amazon"]
e46["verifiedAt"] = datetime.date.today().isoformat()

# 🚨 福岡10/17の枠に、消す側の個別URLを焼き込む
burned = 0
for t in e46["tickets"]:
    if "福岡" in (t.get("type") or "") and not (t.get("url") or ""):
        t["url"] = url47
        burned += 1

events = [e for e in events if e["id"] != 6547]

bak = "index.html.bak_%s_tmg" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
new_arr = json.dumps(events, ensure_ascii=False, indent=2)
open(PATH, "w", encoding="utf-8").write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("6546: date=%s venue=%s 枠=%d / 焼き込み=%d / 6547削除 / backup=%s"
      % (e46["date"], "OK", len(e46["tickets"]), burned, bak))
