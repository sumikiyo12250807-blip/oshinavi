# -*- coding: utf-8 -*-
"""2026-08-10：plan.md の積み残し3件を実データで作り直す。
- 2194 LINDBERG … 発売前のまま止まっていた5枠に実締切を入れ、**未登録だった北海道2公演**(札幌12/10・小樽12/12)を追加。
                  死んだ先行3枠(香川2次プレリザーブ・広島プリセール・e+先着先行)は落とす。
- 1691 『Yerma イェルマ』 … 東京9/21〜10/12の一般発売はぴあで受付終了→落とす。追加公演10/10と愛知11/7〜8に実締切を入れる。
- 1619 826aska … ぴあ枠は両方終了。e+に福井8/23・和歌山9/5(昼夜)・滋賀9/6(昼夜)が受付中、群馬9/26(昼夜)は予定枚数終了→ツアー統合。
根拠＝tools/pia_tickets.py と tools/eplus_detail.py の機械パース（2026-08-10 取得）。
バッジ内の山括弧は半角だと innerHTML でタグ扱いになるので全角＜＞を使う。
"""
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_leftovers"
E = "https://eplus.jp/sf/detail/"

NEW = {}

NEW[2194] = '''{
    "id": 2194,
    "artist": "LINDBERG",
    "name": "LINDBERG",
    "date": "2026-12-18",
    "dateLabel": "2026年10月12日(月)〜2026年12月18日(金) 全国ツアー",
    "venue": "全国ツアー（Zepp Nagoya／KT Zepp Yokohama／広島LIVE VANQUISH／仙台 darwin／HEAVEN’S ROCK Utsunomiya VJ-2／ペニーレーン24／小樽GOLDSTONE／豊洲PIT）",
    "prefecture": "全国",
    "genre": "jpop",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventCd=2621618",
      "eplus": "https://eplus.jp/sf/detail/0273960001-P0030153P021001",
      "amazon": "https://www.amazon.co.jp/s?k=LINDBERG%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
      {
        "type": "一般発売（愛知 10/12公演）〜10/11 23:59",
        "date": "2026-10-11",
        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2619757"
      },
      {
        "type": "一般発売（神奈川 10/23公演）〜10/7 23:59",
        "date": "2026-10-07",
        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2618730"
      },
      {
        "type": "先着一般発売（神奈川 10/23公演）〜10/19 18:00",
        "date": "2026-10-19",
        "url": "https://eplus.jp/sf/detail/0273960001-P0030153P021001"
      },
      {
        "type": "先着一般発売（広島 11/6公演）〜11/5 18:00",
        "date": "2026-11-05",
        "url": "https://eplus.jp/sf/detail/0273960001-P0030144P021001"
      },
      {
        "type": "一般発売（宮城 12/4公演）〜11/25 23:59",
        "date": "2026-11-25",
        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2625757"
      },
      {
        "type": "一般発売（栃木 12/6公演）〜11/19 23:59",
        "date": "2026-11-19",
        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2618730"
      },
      {
        "type": "先着一般発売（栃木 12/6公演）〜12/2 18:00",
        "date": "2026-12-02",
        "url": "https://eplus.jp/sf/detail/0273960001-P0030154P021001"
      },
      {
        "type": "一般発売（北海道 12/10公演）〜12/1 23:59",
        "date": "2026-12-01",
        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2621618"
      },
      {
        "type": "一般発売（北海道 12/12公演）〜12/1 23:59",
        "date": "2026-12-01",
        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2621618"
      },
      {
        "type": "一般発売（東京 12/18公演）〜12/2 23:59",
        "date": "2026-12-02",
        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2618730"
      },
      {
        "type": "先着一般発売（東京 12/18公演）〜12/14 18:00",
        "date": "2026-12-14",
        "url": "https://eplus.jp/sf/detail/0273960001-P0030155P021001"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''

NEW[1691] = '''{
    "id": 1691,
    "artist": "『Yerma イェルマ』",
    "name": "『Yerma イェルマ』",
    "date": "2026-11-08",
    "dateLabel": "2026年9月21日(月)〜2026年11月8日(日) 全国ツアー",
    "venue": "全国ツアー（兵庫県立芸術文化センター 阪急 中ホール／シアタートラム／多賀城市民会館 大ホール／東海市芸術劇場 大ホール）",
    "prefecture": "全国",
    "genre": "engeki",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668064",
      "eplus": null
    },
    "tickets": [
      {
        "type": "一般発売【ファミリーマート支払い専用】（宮城 10/31〜11/1公演）〜8/10 23:59",
        "date": "2026-08-10"
      },
      {
        "type": "一般発売【ぴあ貸切公演】（東京 9/26〜10/5公演）〜10/2 23:59",
        "date": "2026-10-02"
      },
      {
        "type": "一般発売【追加公演】（東京 10/10公演）〜10/7 23:59",
        "date": "2026-10-07"
      },
      {
        "type": "一般発売（兵庫 10/17〜10/18公演）〜10/17 23:59",
        "date": "2026-10-17"
      },
      {
        "type": "一般発売（宮城 10/31〜11/1公演）〜10/29 23:59",
        "date": "2026-10-29"
      },
      {
        "type": "一般発売（愛知 11/7〜11/8公演）〜11/6 17:00",
        "date": "2026-11-06"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''

NEW[1619] = '''{
    "id": 1619,
    "artist": "826aska",
    "name": "826aska",
    "date": "2026-09-26",
    "dateLabel": "2026年8月23日(日)〜2026年9月26日(土) 全国ツアー",
    "venue": "全国ツアー（福井県県民ホール／和歌山 CLUB GATE／滋賀 U☆STONE／Club JAMMER’S TAKASAKI）",
    "prefecture": "全国",
    "genre": "jpop",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": null,
      "eplus": "https://eplus.jp/sf/detail/2582290001-P0030091P021001",
      "amazon": "https://www.amazon.co.jp/s?k=826aska%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
      {
        "type": "一般発売（福井 8/23公演）〜8/22 18:00",
        "date": "2026-08-22",
        "url": "https://eplus.jp/sf/detail/2582290001-P0030091P021001"
      },
      {
        "type": "一般発売＜昼公演＞（和歌山 9/5公演）〜9/4 18:00",
        "date": "2026-09-04",
        "url": "https://eplus.jp/sf/detail/2582290001-P0030092P021001"
      },
      {
        "type": "一般発売＜夜公演＞（和歌山 9/5公演）〜9/4 18:00",
        "date": "2026-09-04",
        "url": "https://eplus.jp/sf/detail/2582290001-P0030092P021002"
      },
      {
        "type": "一般発売＜昼公演＞（滋賀 9/6公演）〜9/5 18:00",
        "date": "2026-09-05",
        "url": "https://eplus.jp/sf/detail/2582290001-P0030093P021001"
      },
      {
        "type": "一般発売＜夜公演＞（滋賀 9/6公演）〜9/5 18:00",
        "date": "2026-09-05",
        "url": "https://eplus.jp/sf/detail/2582290001-P0030093P021002"
      },
      {
        "type": "一般発売＜昼公演＞（群馬 9/26公演）〜9/25 18:00",
        "date": "2026-09-25",
        "url": "https://eplus.jp/sf/detail/2582290001-P0030094P021001",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      },
      {
        "type": "一般発売＜夜公演＞（群馬 9/26公演）〜9/25 18:00",
        "date": "2026-09-25",
        "url": "https://eplus.jp/sf/detail/2582290001-P0030094P021002",
        "soldout": true,
        "soldoutSince": "2026-08-10"
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


def main():
    shutil.copyfile(P, BAK)
    src = open(P, "rb").read().decode("utf-8")
    for eid in sorted(NEW):
        i, j = entry_span(src, eid)
        body = NEW[eid].replace("\r\n", "\n").replace("\n", "\r\n")
        src = src[:i] + body + src[j:]
        print("id=%d 置換 %d→%d文字" % (eid, j - i, len(body)))
    out = src.encode("utf-8")
    assert len(re.findall(rb"(?<!\r)\n", out)) == 0, "単独LFが混ざった"
    open(P, "wb").write(out)
    print("書き込み完了 (backup: %s)" % BAK)


main()
