# -*- coding: utf-8 -*-
"""ぴあ生HTMLの券種カードを、状態テキストの**前後**を付けて出す。

🚨 `parse_cards` が拾えていないカードを見つけるための道具（2026-09-05 id2254 の3次受付で必要になった）。
   生HTMLに [抽選受付中] が2枚あるのに parse_cards は1枚しか返さなかった＝**買える枠を落としている**。

使い方: python tmp/status_ctx_0905.py <eventCd> [文脈の文字数]
"""
import re, io, sys
sys.path.insert(0, "tools")
from build_pia_entries import fetch

cd = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 700
url = "https://t.pia.jp/pia/event/event.do?eventCd=%s" % cd
h = fetch(url)


def strip(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", s).strip()


buf = ["■ %s  （HTML %d文字）" % (url, len(h)), ""]
for n, m in enumerate(re.finditer(r'__status\s+(is-[\w-]+)"[^>]*>(.*?)(?:<br|</p>|</span>)', h, re.S), 1):
    cls, txt = m.group(1), strip(m.group(2))
    before = strip(h[max(0, m.start() - N):m.start()])
    after = strip(h[m.end():m.end() + N])
    buf.append("── カード%d  [%s] %s" % (n, txt, cls))
    buf.append("   前： …%s" % before[-N // 2:])
    buf.append("   後： %s…" % after[:N // 2])
    buf.append("")

io.open("tmp/status_ctx_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("wrote tmp/status_ctx_0905.txt (%d lines)" % len(buf))
