# -*- coding: utf-8 -*-
"""2026-08-10 朝ルーチン：宿題エントリの修正・ツアー育成。
- 106 リポビタンDチャレンジカップ … 東大阪8/8終了→新潟9/5(生きてる枠)へ会場・公演日を移す
- 1037 みえるとか みえないとか … e+で兵庫8/16(受付中)・神奈川8/20(予定枚数終了)＝ツアー統合
- 1656 Summer Eye … e+で京都10/3・愛知10/4・東京10/8が一般発売受付中＝ツアー統合
- 2340 osage … e+で宮城10/4・福岡10/10・愛知10/23・広島10/24・東京11/1が受付中＝ツアー統合
index.html は CRLF。バイナリで読み書きし、差し込む本文も CRLF に揃える
（feedback_index_html_crlf_preserve）。
"""
import re
import sys
import shutil

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_morning_fix"

NEW = {}

NEW[106] = '''{
    "id": 106,
    "artist": "リポビタンDチャレンジカップ2026",
    "name": "リポビタンDチャレンジカップ2026 日本代表対カナダ代表",
    "date": "2026-09-05",
    "venue": "デンカビッグスワンスタジアム",
    "prefecture": "新潟",
    "genre": "sports",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668072",
      "eplus": null
    },
    "tickets": [
      {
        "type": "一般発売（チケットぴあ）（新潟 9/5公演）〜9/4 23:59",
        "date": "2026-09-04"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10",
    "dateLabel": "2026年9月5日(土) 新潟 デンカビッグスワンスタジアム"
  }'''

NEW[1037] = '''{
    "id": 1037,
    "artist": "おどる絵本『みえるとか みえないとか』",
    "name": "おどる絵本『みえるとか みえないとか』",
    "date": "2026-08-20",
    "dateLabel": "2026年8月16日(日)〜2026年8月20日(木) 全国ツアー",
    "venue": "全国ツアー（神戸文化ホール 中ホール／茅ヶ崎市民文化会館 大ホール）",
    "prefecture": "全国",
    "genre": "kids",
    "extraGenres": [
      "engeki"
    ],
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": null,
      "eplus": "https://eplus.jp/sf/detail/4526820001-P0030001P021001"
    },
    "tickets": [
      {
        "type": "一般発売（兵庫 8/16公演）〜8/12 18:00",
        "date": "2026-08-12",
        "url": "https://eplus.jp/sf/detail/4526820001-P0030001P021001"
      },
      {
        "type": "一般発売（神奈川 8/20公演）〜8/18 18:00",
        "date": "2026-08-18",
        "url": "https://eplus.jp/sf/detail/4514670001-P0030001P021001",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''

NEW[1656] = '''{
    "id": 1656,
    "artist": "Summer Eye",
    "name": "Summer Eye",
    "date": "2026-10-08",
    "dateLabel": "2026年10月3日(土)〜2026年10月8日(木) 全国ツアー",
    "venue": "全国ツアー（京都 磔磔／24PILLARS／LIQUIDROOM）",
    "prefecture": "全国",
    "genre": "jpop",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventCd=2622699",
      "eplus": "https://eplus.jp/sf/detail/3963800001-P0030009P021001",
      "amazon": "https://www.amazon.co.jp/s?k=Summer%20Eye%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
      {
        "type": "一般発売（京都 10/3公演）〜10/2 23:59",
        "date": "2026-10-02",
        "url": "https://eplus.jp/sf/detail/3963800001-P0030009P021001"
      },
      {
        "type": "一般発売（愛知 10/4公演）〜10/3 23:59",
        "date": "2026-10-03",
        "url": "https://eplus.jp/sf/detail/3963800001-P0030010P021001"
      },
      {
        "type": "一般発売（東京 10/8公演）〜10/7 23:59",
        "date": "2026-10-07",
        "url": "https://eplus.jp/sf/detail/3963800001-P0030011P021001"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''

NEW[2340] = '''{
    "id": 2340,
    "artist": "osage",
    "name": "osage",
    "date": "2026-11-01",
    "dateLabel": "2026年10月4日(日)〜2026年11月1日(日) 全国ツアー",
    "venue": "全国ツアー（仙台LIVE HOUSE enn3rd／LIVE HOUSE Queblick／名古屋ell.SIZE／広島Cave-Be／渋谷クラブクアトロ）",
    "prefecture": "全国",
    "genre": "jpop",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventCd=2624941",
      "eplus": "https://eplus.jp/sf/detail/3030470001-P0030088P021001",
      "amazon": "https://www.amazon.co.jp/s?k=osage%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
      {
        "type": "一般発売（宮城 10/4公演）〜10/3 23:59",
        "date": "2026-10-03",
        "url": "https://eplus.jp/sf/detail/3030470001-P0030088P021001"
      },
      {
        "type": "一般発売（福岡 10/10公演）〜10/9 20:00",
        "date": "2026-10-09",
        "url": "https://eplus.jp/sf/detail/3030470001-P0030089P021001"
      },
      {
        "type": "一般発売（愛知 10/23公演）〜10/22 18:00",
        "date": "2026-10-22",
        "url": "https://eplus.jp/sf/detail/3030470001-P0030090P021001"
      },
      {
        "type": "一般発売（広島 10/24公演）〜10/23 20:00",
        "date": "2026-10-23",
        "url": "https://eplus.jp/sf/detail/3030470001-P0030091P021001"
      },
      {
        "type": "一般発売（東京 11/1公演）〜10/28 18:00",
        "date": "2026-10-28",
        "url": "https://eplus.jp/sf/detail/3030470001-P0030092P021001"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''


def entry_span(src, eid):
    m = re.search(r'\n\s*\{\s*"id": %d,' % eid, src)
    if not m:
        raise SystemExit("id=%d が見つからない" % eid)
    i = src.index("{", m.start())
    depth = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return i, j + 1
    raise SystemExit("id=%d の閉じ括弧が見つからない" % eid)


def main():
    shutil.copyfile(P, BAK)
    src = open(P, "rb").read().decode("utf-8")
    crlf_before = src.count("\r\n")
    for eid in sorted(NEW):
        i, j = entry_span(src, eid)
        body = NEW[eid].replace("\r\n", "\n").replace("\n", "\r\n")
        src = src[:i] + body + src[j:]
        print("id=%d 置換 %d文字 → %d文字" % (eid, j - i, len(body)))
    out = src.encode("utf-8")
    lone_lf = len(re.findall(rb"(?<!\r)\n", out))
    print("CRLF %d→%d / 単独LF %d" % (crlf_before, src.count("\r\n"), lone_lf))
    assert lone_lf == 0, "単独LFが混ざった＝改行が壊れている"
    open(P, "wb").write(out)
    print("書き込み完了 (backup: %s)" % BAK)


main()
