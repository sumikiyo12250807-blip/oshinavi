# -*- coding: utf-8 -*-
"""id940 の2枠に「予定枚数終了」を付ける（消さない）。

根拠＝ぴあの生HTMLの状態テキストを直接読んだ（tmp/statustext_0905.txt）:
  eventCd=2617186 千葉9/30 一般発売           … [予定枚数終了]
  eventCd=2610059 山形10/11(酒田) 一般発売    … [予定枚数終了]
どちらも登録上の締切（9/24・10/8）はまだ未来なのに、ぴあでは売り切れていた
＝**買えないものを載せている**状態だった。

DELETE_GATE 1.＝「予定枚数終了（売り切れた）」は ❌消さない。`soldout: true` ＋ `soldoutSince`。
（`saleEnded` は付けない＝あれは「期間が終わっただけ」の点線バッジ）
"""
import re, json, io, datetime

PATH = "index.html"
TODAY = datetime.date.today().isoformat()
TARGET = [
    (940, "2617186", "千葉 9/30"),
    (940, "2610059", "山形 10/11"),
]

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

buf, n = [], 0
for i, cd, label in TARGET:
    e = by.get(i)
    if not e:
        buf.append("SKIP id=%s（現物に無い）" % i)
        continue
    hit = False
    for t in e.get("tickets") or []:
        if cd not in (t.get("url") or ""):
            continue
        hit = True
        if t.get("soldout"):
            buf.append("SKIP id=%s %s ← 既に soldout" % (i, t.get("type")))
            continue
        t["soldout"] = True
        t["soldoutSince"] = TODAY
        n += 1
        buf.append("id=%s  %s" % (i, t.get("type")))
        buf.append("      → soldout:true / soldoutSince:%s（根拠＝ぴあ実ページの状態テキスト「予定枚数終了」）" % TODAY)
    if not hit:
        buf.append("🚨 id=%s に %s(%s) を指す枠が無い" % (i, cd, label))

buf.append("")
buf.append("付けた枠: %d" % n)
io.open("tmp/mark_soldout_940_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("SOLDOUT=%d" % n)

if n:
    bak = "index.html.bak_%s_soldout940" % datetime.date.today().strftime("%m%d")
    open(bak, "w", encoding="utf-8").write(h)
    open(PATH, "w", encoding="utf-8").write(
        h[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
    print("APPLIED backup=%s" % bak)
