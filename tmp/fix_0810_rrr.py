# -*- coding: utf-8 -*-
"""2026-08-10：2223 宝塚星組『RRR×TAKA"R"AZUKA』に e+貸切公演(9/9)の受付中3枠を追加。
根拠＝tools/eplus_detail.py で
https://eplus.jp/sf/detail/0015890190-P0030490P021001 を機械パース（2026/9/9 宝塚大劇場・受付中3/4）。
ぴあ枠(9/26・9/30)は予定枚数終了なので soldout のまま残す（feedback_soldout_keep_visible）。
"""
import re
import sys
import shutil

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0810_rrr"
U = "https://eplus.jp/sf/detail/0015890190-P0030490P021001"

OLD_TAIL = '''      {
        "type": "一般発売（兵庫 9/30公演）8/8 10:00発売",
        "date": "2026-08-08",
        "startDate": "2026-08-08",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      }
    ],'''

NEW_TAIL = '''      {
        "type": "一般発売（兵庫 9/30公演）8/8 10:00発売",
        "date": "2026-08-08",
        "startDate": "2026-08-08",
        "soldout": true,
        "soldoutSince": "2026-08-10"
      },
      {
        "type": "【スマチケ限定】特別プレオーダー（兵庫 9/9公演）〜8/12 18:00",
        "date": "2026-08-12",
        "url": "%s"
      },
      {
        "type": "【特別限定プラン/フェリエ】プレオーダー（兵庫 9/9公演）〜8/12 15:30",
        "date": "2026-08-12",
        "url": "%s"
      },
      {
        "type": "【特別限定プラン/くすのき】プレオーダー（兵庫 9/9公演）〜8/12 15:30",
        "date": "2026-08-12",
        "url": "%s"
      }
    ],''' % (U, U, U)

OLD_LINK = '''      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668844",
      "eplus": null'''
NEW_LINK = '''      "pia": "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668844",
      "eplus": "%s"''' % U


def crlf(s):
    return s.replace("\r\n", "\n").replace("\n", "\r\n")


def main():
    shutil.copyfile(P, BAK)
    src = open(P, "rb").read().decode("utf-8")
    for old, new in ((OLD_TAIL, NEW_TAIL), (OLD_LINK, NEW_LINK)):
        o, n = crlf(old), crlf(new)
        assert src.count(o) == 1, "一致数 %d（1件でないので中止）" % src.count(o)
        src = src.replace(o, n)
    out = src.encode("utf-8")
    assert len(re.findall(rb"(?<!\r)\n", out)) == 0, "単独LFが混ざった"
    open(P, "wb").write(out)
    print("2223 に e+貸切9/9の3枠を追加 (backup: %s)" % BAK)


main()
