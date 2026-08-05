# -*- coding: utf-8 -*-
"""ぴあで受付終了だった怪談を、e+で生きていた分だけ拾う（2026-08-05）。

新規3件（全部e+の /sf/detail/ 個別ページでステータスを確認済み＝一覧のラベルで判断していない）:
  3805 HORROR TELLER FESTIVAL 2026        東京 O-WEST/O-nest/7th FLOOR  8/27  〜8/26 18:00 受付中
  3806 島田秀平×城谷歩×響洋平 彩恐酔夜vol.2  埼玉 ハストピア どきどきホール 8/15  〜8/14 23:59 受付中＋当日券
  3807 オカルト超会議 MU PSYCHIC LAB       神奈川 SUPERNOVA KAWASAKI  8/21・8/22 各1部2部＝4枠 受付中
       ※ぴあ(2628671)は受付終了。e+だけが生きている＝[[feedback_delete_nonpia_blindspot]]の実例
既存への枠追加1件:
  3794 怪談五人羽織 … ぴあは〜8/13だが【e+は〜8/27 18:00】＝2週間長く買える。枠とlinks.eplusを追加

同日で時間が違う公演はバッジに公演時間を入れる（[[feedback_same_day_show_time_badge]]）。
"""
import io
import json
import os
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
IDX = os.path.join(ROOT, "index.html")
BAK = os.path.join(ROOT, "index.html.bak_0805_kaidan_eplus")

E = "https://eplus.jp/sf/detail/"

new_entries = [
    {
        "id": 3805,
        "artist": "HORROR TELLER FESTIVAL 2026",
        "name": "HORROR TELLER FESTIVAL 2026",
        "date": "2026-08-27",
        "dateLabel": "2026年8月27日(木) 東京 O-WEST／O-nest／7th FLOOR",
        "venue": "O-WEST／O-nest／7th FLOOR",
        "prefecture": "東京",
        "genre": "new",
        "_genre": "kaidan",
        "_extraGenres": [],
        "_piaSub": "",
        "price": None,
        "links": {"rakuten": None, "lawson": None, "pia": None,
                  "eplus": E + "3608720001-P0030004P021001", "amazon": None},
        "tickets": [
            {"type": "一般発売（東京 8/27公演）〜8/26 18:00", "date": "2026-08-26",
             "url": E + "3608720001-P0030004P021001"},
        ],
        "verified": True,
        "verifiedAt": "2026-08-05",
    },
    {
        "id": 3806,
        "artist": "島田秀平×城谷歩×響洋平 彩恐酔夜vol.2",
        "name": "島田秀平×城谷歩×響洋平 彩恐酔夜vol.2",
        "date": "2026-08-15",
        "dateLabel": "2026年8月15日(土) 埼玉 蓮田市総合文化会館ハストピア どきどきホール",
        "venue": "蓮田市総合文化会館ハストピア どきどきホール",
        "prefecture": "埼玉",
        "genre": "new",
        "_genre": "kaidan",
        "_extraGenres": [],
        "_piaSub": "",
        "price": None,
        "links": {"rakuten": None, "lawson": None, "pia": None,
                  "eplus": E + "4544090001-P0030001P021001", "amazon": None},
        "tickets": [
            {"type": "一般発売（埼玉 8/15公演）〜8/14 23:59", "date": "2026-08-14",
             "url": E + "4544090001-P0030001P021001"},
            {"type": "当日券（埼玉 8/15公演）8/15 0:00発売", "date": "2026-08-15",
             "startDate": "2026-08-15", "url": E + "4544090001-P0030001P021001"},
        ],
        "verified": True,
        "verifiedAt": "2026-08-05",
    },
    {
        "id": 3807,
        "artist": "オカルト超会議 MU PSYCHIC LAB～ムー超能力研究所～",
        "name": "オカルト超会議 MU PSYCHIC LAB～ムー超能力研究所～",
        "date": "2026-08-22",
        "dateLabel": "2026年8月21日(金)〜2026年8月22日(土) 神奈川 SUPERNOVA KAWASAKI",
        "venue": "SUPERNOVA KAWASAKI",
        "prefecture": "神奈川",
        "genre": "new",
        "_genre": "kaidan",
        "_extraGenres": [],
        "_piaSub": "",
        "price": None,
        "links": {"rakuten": None, "lawson": None, "pia": None,
                  "eplus": E + "4199660003-P0030003P021001", "amazon": None},
        "tickets": [
            {"type": "一般発売【1部 15:00】（神奈川 8/21公演）〜8/19 18:00", "date": "2026-08-19",
             "url": E + "4199660003-P0030003P021001"},
            {"type": "一般発売【2部 18:30】（神奈川 8/21公演）〜8/19 18:00", "date": "2026-08-19",
             "url": E + "4199660003-P0030003P021003"},
            {"type": "一般発売【1部 15:00】（神奈川 8/22公演）〜8/20 18:00", "date": "2026-08-20",
             "url": E + "4199660003-P0030003P021002"},
            {"type": "一般発売【2部 18:30】（神奈川 8/22公演）〜8/20 18:00", "date": "2026-08-20",
             "url": E + "4199660003-P0030003P021004"},
        ],
        "verified": True,
        "verifiedAt": "2026-08-05",
    },
]

h = io.open(IDX, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
exist = {e["id"] for e in EVENTS}
dup = [e["id"] for e in new_entries if e["id"] in exist]
assert not dup, "id重複: %s" % dup

# --- 3794 怪談五人羽織にe+枠を足す ---
g = next(e for e in EVENTS if e["id"] == 3794)
g["tickets"].append({
    "type": "一般発売（広島 8/30公演）〜8/27 18:00",
    "date": "2026-08-27",
    "url": E + "3917550001-P0030010P021001",
})
g["links"]["eplus"] = E + "3917550001-P0030010P021001"
print("id3794 怪談五人羽織 → e+枠を追加（ぴあ〜8/13 ／ e+〜8/27 18:00）")

EVENTS.extend(new_entries)

# --- NEW_ORDER に追記（上書きしない＝[[feedback_new_list_order_lock]]）---
mo = re.search(r"(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]", h)
cur = [int(x) for x in re.findall(r"\d+", mo.group(2))]
merged = cur + [e["id"] for e in new_entries if e["id"] not in cur]
h2 = re.sub(r"(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]",
            r"\g<1>[" + ", ".join(str(i) for i in merged) + "]", h, count=1)

shutil.copyfile(IDX, BAK)
m2 = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h2, re.S)
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
io.open(IDX, "w", encoding="utf-8", newline="").write(
    h2[:m2.start()] + m2.group(1) + arr + m2.group(3) + h2[m2.end():])
print("投入 %d件 (3805-3807) / NEW_ORDER %d件 / 総%d件 / backup %s"
      % (len(new_entries), len(merged), len(EVENTS), os.path.basename(BAK)))
