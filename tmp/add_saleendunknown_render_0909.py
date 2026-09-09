# -*- coding: utf-8 -*-
"""締切が「実ページに書かれていない」枠を、発売日に〜を付けて『販売中』で出せるようにする。

ユーザー決定（2026-09-09 夜）＝
「カウントダウンは発売までのこと。いつまでか分からないのは発売日を表示して〜を付けて、
　ヒールでその売り場がなくなるまで表示すればいい。販売中の表示をするの」

きっかけ＝id7502 ラフ×ラフ47都道府県巡業。楽天の実ページの販売期間は
「2026/08/17(月) 12:00 〜」で**終わりが書かれていない**のに、
ビルドが最終公演日(4/3)を締切に流用して「〜R9年 4/3 17:00」と嘘を出していた。

`saleEndUnknown` はデータには入っていたが、renderCard でも build_ai_page でも
**1度も使われていなかった**。ここで表示につなぐ。

🚨並び順のロジック（EVENTS.sort / ticketSortKey / saleStartPending）には一切触らない
  （sort_guard フックがブロックするため。2026-08-14 の設計と同じ考え方）。
CRLFを壊さないよう newline='' で読み書きする。
"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'index.html'
h = io.open(P, encoding='utf-8', newline='').read()
orig = h

# --- ① 状態判定に saleEndUnknown の枝を足す（saleUntilSoldOut の直後）------------
OLD1 = ('      if (t.saleUntilSoldOut) {\r\n'
        '        status = "selling";\r\n'
        '        label  = "販売中";\r\n'
        '        displayDate = null;\r\n'
        '      } else if (saleStartPending(t)) {\r\n')
NEW1 = ('      if (t.saleUntilSoldOut) {\r\n'
        '        status = "selling";\r\n'
        '        label  = "販売中";\r\n'
        '        displayDate = null;\r\n'
        '      } else if (t.saleEndUnknown && t.startDate && parseDateStr(t.startDate) <= today) {\r\n'
        '        // 売り場に「いつまで」が書かれていない枠。発売日は分かっているので\r\n'
        '        // 「M/D発売〜」とだけ出して販売中にする（嘘の締切を作らない）。\r\n'
        '        // 売り場が消えたらヒール／削除ゲートで落ちる。ユーザー決定 2026-09-09。\r\n'
        '        status = "selling";\r\n'
        '        label  = "販売中";\r\n'
        '        displayDate = t.startDate;\r\n'
        '      } else if (saleStartPending(t)) {\r\n')
assert h.count(OLD1) == 1, '状態判定の場所が見つからない（%d件）' % h.count(OLD1)
h = h.replace(OLD1, NEW1)

# --- ② 日付の行＝「〜」を前でなく後ろに付ける ------------------------------------
OLD2 = ('      const datePrefix = (status === "selling" || (label === "本日発売" && displayDate === t.date)) ? "〜" : "";\r\n')
NEW2 = ('      const endUnknown = !!(t.saleEndUnknown && t.startDate && parseDateStr(t.startDate) <= today && !t.saleUntilSoldOut);\r\n'
        '      // 締切が分かっている枠は「〜M/D」。締切が書かれていない枠は「M/D発売〜」と後ろに付ける\r\n'
        '      const datePrefix = endUnknown ? "" : ((status === "selling" || (label === "本日発売" && displayDate === t.date)) ? "〜" : "");\r\n'
        '      const dateSuffix = endUnknown ? "発売〜" : "";\r\n')
assert h.count(OLD2) == 1, 'datePrefix の場所が見つからない'
h = h.replace(OLD2, NEW2)

OLD3 = ('        : `<div class="ticket-date">${datePrefix}${formatDate(displayDate)}${timeHTML}</div>`;\r\n')
NEW3 = ('        : `<div class="ticket-date">${datePrefix}${formatDate(displayDate)}${timeHTML}${dateSuffix}</div>`;\r\n')
assert h.count(OLD3) == 1, 'dateLine の場所が見つからない'
h = h.replace(OLD3, NEW3)

print('差分: %+d バイト' % (len(h) - len(orig)))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('書き込み完了')
