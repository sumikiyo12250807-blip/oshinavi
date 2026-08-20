# -*- coding: utf-8 -*-
"""表記が同じで見分けのつかない枠にぴあの実券種名からラベルを戻す。

  3811 新田恵海        ＝ プレイガイド最速先行が「＜昼公演＞」「＜夜公演＞」の2本
  3862 Kobe Calling  ＝ 2630990 が「（2日間通し券）」（2631003はラベル無しの単日側）
ラベルは 〔…〕 に入れる（check_badges のパース化けガードを通す形）。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_labels2"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

done = []
for e in EVENTS:
    if e["id"] == 3811:
        tks = [t for t in e["tickets"] if t["type"].startswith("プレイガイド最速先行")]
        assert len(tks) == 2, "先行枠が2本でない"
        # ぴあの並び順＝＜夜公演＞→＜昼公演＞（lotRlsCd 68622 / 63917）
        for t, lab, u in zip(tks, ["夜公演", "昼公演"],
                             ["https://t.pia.jp/pia/ticketInformation.do?lotRlsCd=68622",
                              "https://t.pia.jp/pia/ticketInformation.do?lotRlsCd=63917"]):
            t["type"] = t["type"].replace("プレイガイド最速先行（",
                                          "プレイガイド最速先行〔%s〕（" % lab)
            t["url"] = u
        done.append("3811 新田恵海 先行を〔昼公演〕〔夜公演〕に分けた")
    if e["id"] == 3862:
        for t in e["tickets"]:
            if t.get("url", "").endswith("2630990"):
                t["type"] = t["type"].replace("一般発売（", "一般発売〔2日間通し券〕（")
        done.append("3862 Kobe Calling に〔2日間通し券〕を戻した")

assert len(done) == 2, done
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
for d in done:
    print("✅", d)
