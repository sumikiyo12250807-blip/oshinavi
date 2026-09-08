# -*- coding: utf-8 -*-
"""迷った候補だけ、ぴあの実ページの og:description（ツアーの説明文）と公演期間を取る。
<title> は出演者名しか入っていなかったので、同じツアーかの見分けはこちらで行う。
🚨 ぴあを叩きすぎないよう 3秒あける。取れなかったものは「取れなかった」と書く。
"""
import io, re, sys, time, html as _html

sys.path.insert(0, 'tools')
from build_pia_entries import fetch, PiaSorry, is_error_page  # noqa: E402

PAIRS = [
    ("7417 9mm候補(秋田岩手10/3-4)", "2627496"),
    ("4366 9mm既存ツアー(11/7-1/31)", "2627501"),
    ("7360 サニーデイ候補(9/18-9/27)", "b2563931"),
    ("1236 サニーデイ既存(東京10/14)", "2623747"),
    ("7362 バンアパ候補(10/4-12/6)", "b2669905"),
    ("5846 バンアパ既存(新潟10/3)", "2630843"),
    ("7377 ねぐせ候補(北海道11/15)", "2633271"),
    ("4883 ねぐせ既存(福岡11/22)", "2633085"),
    ("7381 PassCode候補(9/24-11/28)", "2624372"),
    ("6923 PassCode既存(東京12/17-18)", "2634920"),
    ("7383 ビッケ候補(北海道9/19)", "2626792"),
    ("5781 ビッケ既存(10/2-10/25)", "2616397"),
    ("7394 摩天楼候補(北海道12/18-19)", "2623366"),
    ("3139 摩天楼既存(8/11-10/31)", "2623237"),
    ("7418 近藤真彦候補(10/31-11/1)", "2618751"),
    ("7423 PEDRO候補(12/19-1/8)", "2627966"),
    ("3126 PEDRO既存(10/17-1/10)", "b2669770"),
    ("7432 Guiano候補(宮城9/25)", "2624486"),
    ("5791 Guiano既存(10/2-10/30)", "2617973"),
    ("7435 高瀬候補(宮城11/29)", "2628826"),
    ("3130 高瀬既存(9/22-12/12)", "2628024"),
    ("7436 ちゃくら候補(宮城9/18)", "2621227"),
    ("5284 ちゃくら既存(東京12/3)", "2626475"),
    ("7405 和田唱候補(北海道10/12)", "2633419"),
]

o = io.open("tmp/ogdesc0908.txt", "w", encoding="utf-8")
for label, cd in PAIRS:
    key = "eventBundleCd" if cd.startswith("b") else "eventCd"
    url = "https://t.pia.jp/pia/event/event.do?%s=%s" % (key, cd)
    try:
        h = fetch(url)
        if is_error_page(h):
            o.write("%s\t%s\t取れなかった（ご確認ください＝eventCd無効）\n" % (label, cd))
        else:
            m = re.search(r'og:description"\s+content="([^"]*)"', h)
            desc = _html.unescape(m.group(1)).strip() if m else "(og:descriptionなし)"
            # 公演期間の欄も拾う
            mp = re.search(r'公演期間</\w+>\s*<\w+[^>]*>(.*?)</', h, re.S)
            per = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", mp.group(1))).strip() if mp else ""
            o.write("%s\t%s\t%s\t[期間] %s\n" % (label, cd, re.sub(r"\s+", " ", desc), per))
    except PiaSorry:
        o.write("%s\t%s\t取れなかった（ぴあ混雑ページ）\n" % (label, cd))
    except Exception as ex:
        o.write("%s\t%s\t取れなかった（%s）\n" % (label, cd, type(ex).__name__))
    o.flush()
    time.sleep(3)
o.close()
print("done -> tmp/ogdesc0908.txt")
