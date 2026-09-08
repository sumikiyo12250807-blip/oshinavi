# -*- coding: utf-8 -*-
"""迷った候補だけ、ぴあの実ページの <title>（＝公演名／ツアー名）を取ってくる。
🚨 ぴあを叩きすぎないよう 3秒あける。混雑ページ(sorry)やエラーは「取れなかった」と書く。
結果は UTF-8 でファイルに書く（端末は cp932 で化けるため）。
"""
import io, re, sys, time, html as _html

sys.path.insert(0, 'tools')
from build_pia_entries import fetch, PiaSorry, is_error_page  # noqa: E402

PAIRS = [
    ("7354 9mm候補(北海道10月)", "2626860"),
    ("7417 9mm候補(秋田岩手10月)", "2627496"),
    ("4366 9mm既存ツアー", "2627501"),
    ("7360 サニーデイ候補", "b2563931"),
    ("1236 サニーデイ既存", "2623747"),
    ("7362 バンアパ候補", "b2669905"),
    ("5846 バンアパ既存", "2630843"),
    ("7377 ねぐせ候補", "2633271"),
    ("4883 ねぐせ既存", "2633085"),
    ("7381 PassCode候補", "2624372"),
    ("6923 PassCode既存", "2634920"),
    ("7383 ビッケ候補", "2626792"),
    ("5781 ビッケ既存", "2616397"),
    ("7394 摩天楼候補", "2623366"),
    ("3139 摩天楼既存", "2623237"),
    ("7418 近藤真彦候補", "2618751"),
    ("7423 PEDRO候補", "2627966"),
    ("3126 PEDRO既存", "b2669770"),
    ("7432 Guiano候補", "2624486"),
    ("5791 Guiano既存", "2617973"),
    ("7435 高瀬候補", "2628826"),
    ("3130 高瀬既存", "2628024"),
    ("7436 ちゃくら候補", "2621227"),
    ("5284 ちゃくら既存", "2626475"),
    ("7405 和田唱候補", "2633419"),
    ("4612 和田唱既存", "2632972"),
]

o = io.open("tmp/titles0908.txt", "w", encoding="utf-8")
for label, cd in PAIRS:
    key = "eventBundleCd" if cd.startswith("b") else "eventCd"
    url = "https://t.pia.jp/pia/event/event.do?%s=%s" % (key, cd)
    try:
        h = fetch(url)
        if is_error_page(h):
            o.write("%s\t%s\t取れなかった（ご確認ください＝eventCd無効）\n" % (label, cd))
        else:
            m = re.search(r"<title>([^<]*)</title>", h)
            t = _html.unescape(m.group(1)).strip() if m else "(titleなし)"
            o.write("%s\t%s\t%s\n" % (label, cd, re.sub(r"\s+", " ", t)))
    except PiaSorry:
        o.write("%s\t%s\t取れなかった（ぴあ混雑ページ）\n" % (label, cd))
    except Exception as ex:
        o.write("%s\t%s\t取れなかった（%s）\n" % (label, cd, type(ex).__name__))
    o.flush()
    time.sleep(3)
o.close()
print("done -> tmp/titles0908.txt")
