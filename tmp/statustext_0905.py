# -*- coding: utf-8 -*-
"""ぴあの生HTMLから、券種ごとの状態テキストをそのまま抜き出す。

🚨 `pia_tickets.py` は「予定枚数終了」も「販売終了」も **"受付終了" に潰す**ので、
   売り切れなのか期間が終わったのかが分からない。DELETE_GATE 1. の打ち分けにはこれが要る。
     予定枚数終了（売り切れた）→ soldout:true ＋ バッジ「予定枚数終了」（実線）
     販売終了（期間が終わった）→ soldout:true ＋ saleEnded:true ＋ バッジ「販売終了」（点線）
   どちらも**消さない**。

使い方: python tmp/statustext_0905.py <eventCd> [<eventCd> ...]
"""
import re, io, sys, time
sys.path.insert(0, "tools")
from build_pia_entries import fetch          # sorry.pia 検出つきの fetch を使う

buf = []
for cd in sys.argv[1:]:
    url = "https://t.pia.jp/pia/event/event.do?eventCd=%s" % cd
    buf.append("■ %s" % url)
    try:
        h = fetch(url)
    except Exception as e:
        buf.append("   取得できなかった: %s: %s" % (e.__class__.__name__, e))
        buf.append("")
        continue
    # 券種カードごとに「状態テキスト」と、近くにある公演日・会場・券種名を拾う
    for m in re.finditer(r'__status\s+(is-[\w-]+)"[^>]*>(.*?)(?:<br|</p>|</span>)', h, re.S):
        cls, txt = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        txt = re.sub(r"\s+", " ", txt).strip()
        around = re.sub(r"<[^>]+>", " ", h[max(0, m.start() - 1400):m.start()])
        around = re.sub(r"\s+", " ", around)
        buf.append("   [%s] %s" % (txt, cls))
        buf.append("        …%s" % around[-160:])
    buf.append("")
    time.sleep(1.2)

io.open("tmp/statustext_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("wrote tmp/statustext_0905.txt (%d lines)" % len(buf))
