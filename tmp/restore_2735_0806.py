# -*- coding: utf-8 -*-
"""2735 THEカルテットを、昼のヒールで潰れた1枠から本来の3枠へ戻す。

🚨原因＝`heal_stale_deadlines --apply` は tickets を丸ごと置き換える。
   このときぴあが429で空を返すと、**朝に統合した会場の枠がそのまま消える**。
   （2026-08-06実害＝松戸9/4・伊勢原10/6が消え、埼玉11/7の1枠だけになった）
実態は単発で叩き直して確認済み:
   松戸  2626826 千葉 9/4公演   受付中 〜9/3 23:59
   伊勢原 2629199 神奈川 10/6公演 受付中 〜10/5 23:59（8/6 10:00に発売済み＝締切が入った）
   花園  2630041 埼玉 11/7公演  発売前 8/8 10:00発売
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_restore2735"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

E = "https://t.pia.jp/pia/event/event.do?eventCd=%s"
TICKETS = [
    {"type": "一般発売（千葉 9/4公演）〜9/3 23:59", "date": "2026-09-03",
     "url": E % "2626826"},
    {"type": "一般発売（神奈川 10/6公演）〜10/5 23:59", "date": "2026-10-05",
     "startDate": "2026-08-06", "url": E % "2629199"},
    {"type": "一般発売（埼玉 11/7公演）8/8 10:00発売", "date": "2026-08-08",
     "startDate": "2026-08-08", "url": E % "2630041"},
]

hit = 0
for e in EVENTS:
    if e["id"] != 2735:
        continue
    hit += 1
    e["tickets"] = TICKETS
    e["venue"] = "全国ツアー（松戸市民劇場／伊勢原市民文化会館 小ホール／深谷市花園文化会館アドニス）"
    e["prefecture"] = "千葉・神奈川・埼玉"
    e["date"] = "2026-11-07"
    e["dateLabel"] = "2026年9月4日(金)〜2026年11月7日(土) 千葉・神奈川・埼玉"
assert hit == 1

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("2735 を3枠（松戸9/4・伊勢原10/6・花園11/7）に復旧した")
