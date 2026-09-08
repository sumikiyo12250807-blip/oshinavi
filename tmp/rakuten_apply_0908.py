# -*- coding: utf-8 -*-
"""楽天の組み立て22件を仕分けて、投入用と統合用に分ける。

【仕分けの根拠＝既存の中身を実際に見て決めた】
  ✂️捨てる5件（既存が同じ枠を全部持っている）
    7496/7497/7498/7499 ウルトラヒーローズ4会場 → id2544 が4会場4枠すべて所持
      （岐阜〜9/11・兵庫〜9/25・宮城〜10/31・千葉〜11/13 が完全一致）
    7507 ANA presents ナーポオケラ → id1768 Na Pookela ナーポオケラ が同内容
      🚨これは [[reference_rakuten_harvest]] が名指しで警告していた「別名の既存とかぶる」型
  🔗統合1件
    7509 ダンロップフェニックス → 既存 id5308 へ。
      既存は「一般発売〜9/29」、楽天は「一般発売【早割デイリーチケット】〜9/30」＝**券種が違う別枠**
      （[[feedback_capture_all_deadlines_on_add]] 登録済みでも締切日が違う窓は取りこぼし）
  ✅投入16件（残り）
    ⚠️7495 アプガ（２）後夜祭 は id3237 アプガ（仮）と同じ飛行船シアター 9/21 だが**グループも公演名も別**
    ⚠️7500 ザコシ単独 は id2926「動画でポン!公開収録」と同じ有楽町朝日ホール 9/20 だが
       id2926 の締切は 9/3 で**もう買えない**（明日の期限切れtriageで消える）。楽天のほうは今買える
"""
import io, json, sys

sys.stdout.reconfigure(encoding="utf-8")

DROP = {7496, 7497, 7498, 7499, 7507}
MERGE = {7509: 5308}

built = json.load(io.open("tmp/built_rakuten_0908.json", encoding="utf-8"))
inject, merge = [], []
for e in built:
    if e["id"] in DROP:
        continue
    if e["id"] in MERGE:
        merge.append(e)
        continue
    inject.append(e)

# 投入分はidを詰め直す（欠番を作らない）
base = min(e["id"] for e in inject)
for i, e in enumerate(inject):
    e["id"] = base + i

io.open("tmp/rakuten_inject_0908.json", "w", encoding="utf-8").write(
    json.dumps(inject, ensure_ascii=False, indent=1))

# 統合分は merge_apply_0905.py の形（既存の公演日・会場・県は据え置き）
out = []
s = io.open("index.html", encoding="utf-8").read()
import re
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", s, re.S).group(1))
by = {x["id"]: x for x in EV}
for e in merge:
    t = by[MERGE[e["id"]]]
    ru = (e.get("links") or {}).get("rakuten")
    tks = []
    for k in e.get("tickets") or []:
        k = dict(k)
        if not k.get("url"):
            k["url"] = ru
        tks.append(k)
    out.append({
        "id": t["id"],
        "date": t["date"], "dateLabel": t["dateLabel"],
        "venue": t["venue"], "prefecture": t["prefecture"],
        # 🚨既存に楽天リンクが無いので、ここで足す（Deep Link形式のまま）
        "links": dict(t.get("links") or {}, rakuten=ru),
        "tickets": tks,
    })
io.open("tmp/rakuten_merge_0908.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))

print("捨てた %d件 / 統合 %d件 / 投入 %d件（id%d..%d）"
      % (len(DROP), len(merge), len(inject), base, base + len(inject) - 1))
for e in inject:
    print("  id%d %s" % (e["id"], e["name"][:56]))
