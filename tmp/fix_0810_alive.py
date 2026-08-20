# -*- coding: utf-8 -*-
"""2026-08-10 朝ルーチン その2：期限切れ削除候補のうち「ぴあに生き枠がある」子を救済。
- 68  仮面ライダースーパーライブ … 宮崎8/9は終わったが大分8/11・長崎8/16・奈良8/23が受付中→ツアー形へ
- 99  舞台『HiGH&LOW THE 戦国 外伝』 … 愛知 御園座 8/14〜8/16 が受付中（〜8/15 23:59）＝追加公演
- 427 フラガリアメモリーズ【動画配信】 … アーカイブ配信3券種が〜8/23 17:00 受付中
- 883 The Right Light … 大阪8/9は終了、愛知8/11（ell.FITS ALL）が受付中
根拠＝tools/pia_tickets.py の実ページ機械パース（2026-08-10 取得）。
index.html は CRLF 維持（feedback_index_html_crlf_preserve）。
"""
import re
import sys
import shutil

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_alive"

NEW = {}

NEW[68] = '''{
    "id": 68,
    "artist": "仮面ライダースーパーライブ",
    "name": "仮面ライダースーパーライブ2026",
    "date": "2026-08-23",
    "dateLabel": "2026年8月11日(火)〜2026年8月23日(日) 全国ツアー",
    "venue": "全国ツアー（iichiko グランシアタ／なら100年会館 大ホール／ベネックス長崎ブリックホール 大ホール）",
    "prefecture": "全国",
    "genre": "kids",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2562549",
      "eplus": null,
      "amazonGoods": "https://amzn.to/49p7gPI",
      "amazonGoodsLabel": "仮面ライダーグッズ"
    },
    "tickets": [
      {
        "type": "一般発売（大分 8/11公演）〜8/10 23:59",
        "date": "2026-08-10"
      },
      {
        "type": "一般発売（奈良 8/23公演）〜8/13 23:59",
        "date": "2026-08-13"
      },
      {
        "type": "一般発売（長崎 8/16公演）〜8/15 23:59",
        "date": "2026-08-15"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''

NEW[99] = '''{
    "id": 99,
    "artist": "HiGH&LOW THE 戦国",
    "name": "舞台『HiGH&LOW THE 戦国 外伝』",
    "date": "2026-08-16",
    "dateLabel": "2026年8月14日(金)〜2026年8月16日(日) 愛知 御園座",
    "venue": "御園座",
    "prefecture": "愛知",
    "genre": "engeki",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2665739",
      "eplus": null
    },
    "tickets": [
      {
        "type": "一般発売（愛知 8/14〜8/16公演）〜8/15 23:59",
        "date": "2026-08-15"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''

NEW[427] = '''{
    "id": 427,
    "artist": "フラガリアメモリーズ",
    "name": "フラガリアメモリーズ CAST LIVE ～Luminous Moments～【動画配信】",
    "date": "2026-08-23",
    "dateLabel": "2026年8月9日(日)公演 ※動画配信 〜8/23",
    "venue": "PIA LIVE STREAM（動画配信）",
    "prefecture": "全国",
    "genre": "anime",
    "extraGenres": [
      "2.5ji"
    ],
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2563597",
      "eplus": null,
      "amazon": "https://www.amazon.co.jp/s?k=%E3%83%95%E3%83%A9%E3%82%AC%E3%83%AA%E3%82%A2%E3%83%A1%E3%83%A2%E3%83%AA%E3%83%BC%E3%82%BA&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
      {
        "type": "動画配信 一般発売〜8/23 17:00",
        "date": "2026-08-23"
      },
      {
        "type": "動画配信 一般発売〈通しスペシャルチケット〉〜8/23 17:00",
        "date": "2026-08-23"
      },
      {
        "type": "動画配信 一般発売〈通しチケット〉〜8/23 17:00",
        "date": "2026-08-23"
      }
    ],
    "verified": true,
    "verifiedAt": "2026-08-10"
  }'''

NEW[883] = '''{
    "id": 883,
    "artist": "The Right Light",
    "name": "The Right Light",
    "date": "2026-08-11",
    "dateLabel": "2026年8月11日(火) 愛知 ell.FITS ALL",
    "venue": "ell.FITS ALL",
    "prefecture": "愛知",
    "genre": "rock",
    "price": null,
    "links": {
      "rakuten": null,
      "lawson": null,
      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668941",
      "eplus": null,
      "amazon": "https://www.amazon.co.jp/s?k=The%20Right%20Light&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
      {
        "type": "一般発売.（愛知 8/11公演）〜8/10 23:59",
        "date": "2026-08-10"
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
    for eid in sorted(NEW):
        i, j = entry_span(src, eid)
        body = NEW[eid].replace("\r\n", "\n").replace("\n", "\r\n")
        src = src[:i] + body + src[j:]
        print("id=%d 置換 %d文字 → %d文字" % (eid, j - i, len(body)))
    out = src.encode("utf-8")
    lone_lf = len(re.findall(rb"(?<!\r)\n", out))
    print("単独LF %d" % lone_lf)
    assert lone_lf == 0, "単独LFが混ざった＝改行が壊れている"
    open(P, "wb").write(out)
    print("書き込み完了 (backup: %s)" % BAK)


main()
