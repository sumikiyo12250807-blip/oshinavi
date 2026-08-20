# -*- coding: utf-8 -*-
"""THEカルテットの昭和歌謡コンサートを1エントリ（全国ツアー）に統合する。

既存 id2735 は「（松戸9月公演）」＝千葉9/4の1公演だけ。今朝の在庫に
伊勢原10/6(8/6 10:00発売)・花園11/7(8/8 10:00発売)が出たので、
別エントリを増やさず既存へ足す（[[feedback_tour_consolidate]]）。
各枠に会場別のぴあURLを付ける（[[feedback_tour_per_ticket_url]]）。
"""
import json, re, io, sys, shutil, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_quartet"
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

NEW = [
    {"type": "一般発売（神奈川 10/6公演）8/6 10:00発売", "date": "2026-08-06",
     "startDate": "2026-08-06",
     "url": "https://t.pia.jp/pia/event/event.do?eventCd=2629199"},
    {"type": "一般発売（埼玉 11/7公演）8/8 10:00発売", "date": "2026-08-08",
     "startDate": "2026-08-08",
     "url": "https://t.pia.jp/pia/event/event.do?eventCd=2630041"},
]

hit = 0
for e in EVENTS:
    if e["id"] != 2735:
        continue
    hit += 1
    assert len(e["tickets"]) == 1, "既存枠が1つでない＝前提が変わった"
    e["tickets"][0]["url"] = "https://t.pia.jp/pia/event/event.do?eventCd=2626826"
    e["tickets"].extend(NEW)
    e["artist"] = "THEカルテットの昭和歌謡コンサート"
    e["name"] = "THEカルテットの昭和歌謡コンサート"
    e["venue"] = "全国ツアー（松戸市民劇場／伊勢原市民文化会館 小ホール／深谷市花園文化会館アドニス）"
    e["prefecture"] = "千葉・神奈川・埼玉"
    e["date"] = "2026-11-07"
    e["dateLabel"] = "2026年9月4日(金)〜2026年11月7日(土) 千葉・神奈川・埼玉"
    e["verifiedAt"] = "2026-08-06"
assert hit == 1

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("2735 を全国ツアー3公演に統合（松戸9/4・伊勢原10/6・花園11/7）")
