# -*- coding: utf-8 -*-
"""動画の背景用に、index.html の複製から「化けたら困る数字」を隠した版を作る。
🚨 本物の index.html は触らない（ユーザーが見ている画面そのものなので＝
   feedback_never_toggle_state_on_users_file）。複製だけを加工する。

消すもの＝最終更新の日時／今週のピックアップ（記事の日付）／広告バナー／
          フィルタボタンの件数（2,812 などのカッコ書き）。
ぼかすもの＝カード一覧（#eventList）＝日付を読めなくする。
残すもの＝ロゴ・見出し・検索窓・ジャンル/ステータス/エリアのボタン。
"""
import io, re, os

src = io.open("index.html", encoding="utf-8", newline="").read()

CSS = """
<style id="video-bg-mask">
  /* 動画の背景用。H3が数字を描き直しても嘘にならないよう、日付と件数を隠す */
  #lastUpdated, .last-updated, .update-stamp { visibility: hidden !important; }
  .pickup, #pickup, .pickup-box, .weekly-pickup { display: none !important; }
  /* カード一覧はぼかす＝「たくさん並んでいる」ことだけ伝わればよく、
     個々の日付が読めるとH3に描き変えられたとき嘘になる（2026-08-23の実例） */
  #eventList { filter: blur(3.5px); opacity: .85; }
  #fixedBanner { display: none !important; }
  .gg-count { visibility: hidden !important; }
  .result-meta { visibility: hidden !important; }
</style>
"""

out = src.replace("</head>", CSS + "</head>", 1)
assert out != src, "</head> が見つからない"

os.makedirs("tmp/promo0908", exist_ok=True)
io.open("tmp/promo0908/site_for_video.html", "w", encoding="utf-8", newline="").write(out)
print("wrote tmp/promo0908/site_for_video.html (%d bytes)" % len(out))
