# -*- coding: utf-8 -*-
"""2026-08-10：id85『ヒプノシスマイク』Rule the Stage vol.3 のローチケURLを取り込む。
2026-05-18の登録時はローチケの個別公演ページが未公開で links が全部 null のまま放置されていた
（project_url_recheck_id85 の宿題が未完だった）。今日ローチケを実ブラウザで開いて実データを取得：
  - 2026/8/15(土) Zepp Namba(OSAKA) 一般発売＝予定枚数終了（受付 5/30 10:00〜8/14 22:00）
  - 2026/8/22(土) Zepp Sapporo      一般発売＝発売中  （受付 5/30 10:00〜8/14 22:00）
ローチケ検索に出ているのはこの2公演だけ。東京7/23-24・大阪8/14・札幌8/21は掲載が無いので書かない
（[[feedback_no_placeholder_dates]]）。予定枚数終了は消さず残す（[[feedback_soldout_keep_visible]]）。
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_id85"

PF = "%E3%80%8E%E3%83%92%E3%83%97%E3%83%8E%E3%82%B7%E3%82%B9%E3%83%9E%E3%82%A4%E3%82%AF%E3%80%80%EF%BC%8D%EF%BC%A4%EF%BD%89%EF%BD%96%EF%BD%89%EF%BD%93%EF%BD%89%EF%BD%8F%EF%BD%8E%E3%80%80%EF%BC%B2%EF%BD%81%EF%BD%90%E3%80%80%EF%BC%A2%EF%BD%81%EF%BD%94%EF%BD%94%EF%BD%8C%EF%BD%85%EF%BC%8D%E3%80%8F%EF%BC%B2%EF%BD%95%EF%BD%8C%EF%BD%85%E3%80%80%EF%BD%94%EF%BD%88%EF%BD%85%E3%80%80%EF%BC%B3%EF%BD%94%EF%BD%81%EF%BD%87%EF%BD%85%E3%80%8A%EF%BC%A4%EF%BD%89%EF%BD%96%EF%BD%89%EF%BD%93%EF%BD%89%EF%BD%8F%EF%BD%8E%E3%80%80%EF%BC%AA%EF%BD%81%EF%BD%8D%E3%80%80%EF%BC%B4%EF%BD%8F%EF%BD%95%EF%BD%92%E3%80%8B%E3%80%80%EF%BD%96%EF%BD%8F%EF%BD%8C%EF%BC%8E%EF%BC%93"
SAP = ("https://l-tike.com/order/?gLcode=31183&gPfKey=20260403000002174165%2C20260403000002174166"
       "&gEntryMthd=02&gScheduleNo=1&gCarrierCd=08&gPfName=" + PF + "&gBaseVenueCd=12401")
OSA = ("https://l-tike.com/order/?gLcode=31183&gPfKey=20260403000002174164%2C20260403000002174163"
       "&gEntryMthd=02&gScheduleNo=1&gCarrierCd=08&gPfName=" + PF + "&gBaseVenueCd=52388")

NEW = '''{
    "id": 85,
    "artist": "ヒプステ",
    "name": "『ヒプノシスマイク -Division Rap Battle-』Rule the Stage《Division Jam Tour》vol.3",
    "date": "2026-08-22",
    "dateLabel": "2026年8月15日(土) 大阪／2026年8月22日(土) 北海道",
    "venue": "全国ツアー（Zepp Namba（OSAKA）／Zepp Sapporo）",
    "prefecture": "全国",
    "genre": "2.5ji",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": "%s",
      "pia": null,
      "eplus": null
    },
    "tickets": [
      {
        "type": "一般発売（大阪 8/15公演）〜8/14 22:00",
        "date": "2026-08-14",
        "url": "%s",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      },
      {
        "type": "一般発売（北海道 8/22公演）〜8/14 22:00",
        "date": "2026-08-14",
        "url": "%s"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }''' % (SAP, OSA, SAP)


def main():
    shutil.copyfile(P, BAK)
    src = open(P, "rb").read().decode("utf-8")
    m = re.search(r'\n\s*\{\s*"id": 85,', src)
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
    print("id85 にローチケURLを登録（札幌=発売中／大阪=予定枚数終了）(backup: %s)" % BAK)


main()
