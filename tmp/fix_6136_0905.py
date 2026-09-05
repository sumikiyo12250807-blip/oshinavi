# -*- coding: utf-8 -*-
"""id6136 舞台「呪術廻戦」の重複2枠を落とす。

【実ページ】eventCd=2628216 / 2628218 はどちらも**同じ2枠**を出している（売り場コードが同一）:
  lotRlsCd=28811 「■舞台「呪術廻戦」-渋谷事変前編-（東京・大阪）」 〜9/8 23:59
  lotRlsCd=34055 「舞台「呪術廻戦」-渋谷事変前編-〔東京・大阪〕」   〜9/14 23:59
＝**買える枠は2つだけ**。

【登録6枠】
  1 先行（東京 11/14〜11/23公演）9/2 12:00発売  〆9/8   url=2628216   ← 28811 の東京側
  2 先行（大阪 11/28〜11/29公演）9/2 12:00発売  〆9/8   url=2628218   ← 28811 の大阪側
  3 先行（東京 11/14〜11/23公演）9/4 12:00発売  〆9/14  url=2628216   ← 34055 の東京側
  4 先行（大阪 11/28〜11/29公演）9/4 12:00発売  〆9/14  url=2628218   ← 34055 の大阪側
  5 先行（東京・大阪 11/14〜11/29公演）〜9/8 23:59      url=なし      ← 28811 のまとめ版（重複）
  6 先行（東京・大阪 11/14〜11/29公演）9/4 12:00発売    url=なし      ← 34055 のまとめ版（重複）

🚨 落とすのは **5 と 6**。理由は2つ：
  ① 1〜4 と同じ販売枠を、県をまとめた形でもう一度登録している（同じ枠が2通りで載っている）
  ② url が無いので `links.pia`（=2628216・**東京**のページ）に飛ぶ。
     「**東京・大阪**」と名乗っているのに**大阪の人が押すと東京のページに着く**＝飛び先が壊れている
     （[[feedback_tour_per_ticket_url]]＝1つのバッジが別々のeventCdページにまたがるなら券種を分割する。
      1〜4がその「分割した正しい形」）

✅ 落としても**買える枠は減らない**＝5の代わりに1と2、6の代わりに3と4が残る。
   むしろ大阪の枠が正しい売り場（2628218）に飛ぶようになる。

🚨 `check_dup_slots` はこの型を拾えない＝判定キーが券種名で、
   「先行（東京 …）」と「先行（東京・大阪 …）」を**別物**と見るため。
"""
import re, json, io, datetime

PATH = "index.html"
TODAY = datetime.date.today().isoformat()
TARGET_ID = 6136
DROP_TYPES = [
    "先行（東京・大阪 11/14〜11/29公演）〜9/8 23:59",
    "先行（東京・大阪 11/14〜11/29公演）9/4 12:00発売",
]

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}
e = by.get(TARGET_ID)
assert e, "id%s が現物に無い" % TARGET_ID


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), (t.get("date") or "")
    return not ((not sd or sd <= TODAY) and d < TODAY)


before = e.get("tickets") or []
n_vis_before = sum(1 for t in before if visible(t))
keep, dropped = [], []
for t in before:
    if (t.get("type") or "").strip() in DROP_TYPES and not (t.get("url") or "").strip():
        dropped.append(t)
    else:
        keep.append(t)

n_vis_after = sum(1 for t in keep if visible(t))
buf = ["id=%s %s" % (TARGET_ID, e.get("name", "")), "",
       "枠 %d → %d（落とす %d）" % (len(before), len(keep), len(dropped)),
       "画面に出る枠 %d → %d" % (n_vis_before, n_vis_after), ""]
for t in dropped:
    buf.append("  落とす: %s  （締切=%s url=%s）" % (t.get("type"), t.get("date"), t.get("url") or "なし"))
buf.append("")
for t in keep:
    buf.append("  残す  : %s  （締切=%s url=%s）" % (t.get("type"), t.get("date"), t.get("url") or "なし"))

io.open("tmp/fix_6136_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("DROP=%d  可視 %d → %d" % (len(dropped), n_vis_before, n_vis_after))

# 🚨 落とす前の安全弁＝残す側に「同じ締切の枠」があること（買える枠が減らないこと）を確かめる
for t in dropped:
    same = [k for k in keep if (k.get("date") or "") == (t.get("date") or "")]
    if not same:
        raise SystemExit("🚨中止: 締切 %s の枠が残らない（買える枠が減る）" % t.get("date"))

import sys
if "--apply" not in sys.argv or not dropped:
    raise SystemExit(0)

e["tickets"] = keep
bak = "index.html.bak_%s_fix6136" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
open(PATH, "w", encoding="utf-8").write(
    h[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print("APPLIED backup=%s" % bak)
