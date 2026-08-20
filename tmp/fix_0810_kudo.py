# -*- coding: utf-8 -*-
"""2026-08-10：2300 工藤静香を「大分8/9単発（終演）」から全国ツアーへ育成。
e+ に山口8/11・北海道8/15・鳥取8/22・岩手8/29・東京9/5 の一般発売が残っており、
どれも「予定枚数終了」＝消さずに残す（feedback_soldout_keep_visible）。
根拠＝tools/eplus_detail.py の機械パース（2026-08-10 取得・全枠 0/5 受付中＝予定枚数終了）。
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_kudo"
B = "https://eplus.jp/sf/detail/0201250001-P00301%s"

NEW = '''{
    "id": 2300,
    "artist": "工藤静香",
    "name": "工藤静香",
    "date": "2026-09-05",
    "dateLabel": "2026年8月11日(火)〜2026年9月5日(土) 全国ツアー",
    "venue": "全国ツアー（KDDI 維新ホール メインホール／コーチャンフォー釧路文化ホール 大ホール／エースパック未来中心 大ホール／奥州市文化会館(Zホール) 大ホール／NHKホール）",
    "prefecture": "全国",
    "genre": "jpop",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667295",
      "eplus": "https://eplus.jp/sf/detail/0201250001-P0030125P021001",
      "amazon": "https://www.amazon.co.jp/s?k=%E5%B7%A5%E8%97%A4%E9%9D%99%E9%A6%99%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
      {
        "type": "一般発売（山口 8/11公演）〜8/10 23:59",
        "date": "2026-08-10",
        "url": "https://eplus.jp/sf/detail/0201250001-P0030121P021001",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      },
      {
        "type": "一般発売（北海道 8/15公演）〜8/14 23:59",
        "date": "2026-08-14",
        "url": "https://eplus.jp/sf/detail/0201250001-P0030122P021001",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      },
      {
        "type": "一般発売（鳥取 8/22公演）〜8/21 23:59",
        "date": "2026-08-21",
        "url": "https://eplus.jp/sf/detail/0201250001-P0030123P021001",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      },
      {
        "type": "一般発売（岩手 8/29公演）〜8/28 23:59",
        "date": "2026-08-28",
        "url": "https://eplus.jp/sf/detail/0201250001-P0030124P021001",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      },
      {
        "type": "一般発売（東京 9/5公演）〜9/4 23:59",
        "date": "2026-09-04",
        "url": "https://eplus.jp/sf/detail/0201250001-P0030125P021001",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''


def main():
    shutil.copyfile(P, BAK)
    src = open(P, "rb").read().decode("utf-8")
    m = re.search(r'\n\s*\{\s*"id": 2300,', src)
    i = src.index("{", m.start())
    d = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            d += 1
        elif src[j] == "}":
            d -= 1
            if d == 0:
                break
    body = NEW.replace("\r\n", "\n").replace("\n", "\r\n")
    src = src[:i] + body + src[j + 1:]
    out = src.encode("utf-8")
    assert len(re.findall(rb"(?<!\r)\n", out)) == 0, "単独LFが混ざった"
    open(P, "wb").write(out)
    print("2300 工藤静香を全国ツアー5枠（全部 予定枚数終了）へ更新 (backup: %s)" % BAK)


main()
