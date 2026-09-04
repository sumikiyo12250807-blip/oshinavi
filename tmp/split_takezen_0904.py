# -*- coding: utf-8 -*-
"""id668「佐藤竹善 / Neighbors Complain 2026」を2つのエントリに分ける。
ユーザー指示 2026-09-04（選択肢1＝分ける）

中身は別の2企画が混ざっていた（記事の裏取りで発覚）＝
  ① 佐藤竹善／Neighbors Complain -AOR SESSION-（ゲスト 夏川りみ）… 大阪10/2・山口10/3 の2公演
  ② 佐藤竹善 Your Christmas Night 2026（ジャズトリオ帯同の恒例クリスマス企画）… 11/22〜12/26

会場はぴあ実ページで確認済み
  大阪10/2 … 茨木市文化・子育て複合施設おにクル ゴウダホール（4F 大ホール）
  山口10/3 … シンフォニア岩国 コンサートホール

🚨あわせて枠[11]「プレリザーブ（新潟 11/28公演）」の url が 2618320（大阪AORのページ）に
   なっている誤りを直す（同じ新潟11/28の他の枠は 2626893）。

  python tmp/split_takezen_0904.py          # 下見
  python tmp/split_takezen_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
APPLY = "--apply" in sys.argv
AOR_URLS = {"https://t.pia.jp/pia/event/event.do?eventCd=2604304",   # 山口10/3
            "https://t.pia.jp/pia/event/event.do?eventCd=2618320"}   # 大阪10/2
NIIGATA_URL = "https://t.pia.jp/pia/event/event.do?eventCd=2626893"

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた"); sys.exit(1)

e = next((x for x in events if x.get("id") == 668), None)
if not e:
    print("ABORT: id668 が無い"); sys.exit(1)
ts = e.get("tickets", [])
print("元の枠=%d" % len(ts))

# ① 新潟のプレリザーブが大阪AORのURLを指している誤りを直す
fixed = 0
for t in ts:
    if "新潟 11/28公演" in (t.get("type") or "") and t.get("url") == "https://t.pia.jp/pia/event/event.do?eventCd=2618320":
        t["url"] = NIIGATA_URL
        fixed += 1
print("新潟の誤ったURLを直した枠=%d" % fixed)

# ② AOR SESSION の枠を切り出す（公演日が10/2・10/3のもの）
aor = [t for t in ts if re.search(r"（(大阪|山口)\s+10/[23]公演）", t.get("type") or "")]
rest = [t for t in ts if t not in aor]
print("AOR SESSION へ移す枠=%d  / Your Christmas Night に残す枠=%d" % (len(aor), len(rest)))
for t in aor:
    print("   移す: %s ／ url=%s" % (t.get("type"), t.get("url")))
if len(aor) != 2:
    print("ABORT: AOR SESSION の枠が2本でない"); sys.exit(1)

new_id = max(x.get("id") for x in events if isinstance(x.get("id"), int)) + 1

# ③ 新エントリ＝AOR SESSION
new_entry = {
    "id": new_id,
    "artist": "佐藤竹善／Neighbors Complain",
    "name": "佐藤竹善／Neighbors Complain -AOR SESSION-",
    "date": "2026-10-03",
    "dateLabel": "2026年10月2日(金)〜2026年10月3日(土) 大阪・山口",
    "venue": "全国ツアー（茨木市文化・子育て複合施設おにクル ゴウダホール／シンフォニア岩国 コンサートホール）",
    "prefecture": "大阪・山口",
    "genre": e.get("genre"),
    "price": None,
    "links": {"rakuten": None, "lawson": None,
              "pia": "https://t.pia.jp/pia/event/event.do?eventCd=2604304",
              "eplus": None,
              "amazon": (e.get("links") or {}).get("amazon")},
    "tickets": aor,
    "verified": True,
}

# ④ 元のエントリ＝Your Christmas Night に作り替える
e["name"] = "佐藤竹善 Your Christmas Night 2026"
e["artist"] = "佐藤竹善"
e["tickets"] = rest
# links.pia が大阪AORのページのままなので、残る枠でいちばん多く使われているURLに付け替える
from collections import Counter
c = Counter(t.get("url") for t in rest if t.get("url"))
if c:
    e.setdefault("links", {})["pia"] = c.most_common(1)[0][0]
print("Your Christmas Night の links.pia -> %s" % (e.get("links") or {}).get("pia"))

# 🚨会場一覧から AOR SESSION の会場を外す（残すと「その会場の公演があるのに枠が無い」状態になる）
AOR_HALLS = {"シンフォニア岩国 コンサートホール"}
mv = re.match(r"全国ツアー（(.+)）$", e.get("venue") or "")
if mv:
    hs = [x.strip() for x in mv.group(1).split("／")]
    left = [x for x in hs if x not in AOR_HALLS]
    removed = [x for x in hs if x in AOR_HALLS]
    if removed:
        e["venue"] = "全国ツアー（%s）" % "／".join(left) if len(left) > 1 else left[0]
        print("会場から外した: %s" % "／".join(removed))
print("Your Christmas Night の会場: %s" % (e.get("venue") or "")[:110])

events.append(new_entry)
print("新エントリ id=%s %s（枠%d）" % (new_id, new_entry["name"], len(aor)))

if not APPLY:
    print("(下見のみ。--apply で書き込み)"); sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_takezen")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html")
