# -*- coding: utf-8 -*-
"""「販売終了」バッジを新設（ユーザー選択 2026-08-14・選択肢2）＝**並び順ロジックには一切触らない版**。

設計:
  枠は今までどおり `soldout: true` を持つ（＝並び・カウントダウン除外・非表示の安全弁は全部そのまま）。
  そこに `saleEnded: true` を足した枠だけ、**バッジの文言を「販売終了」に切り替える**。
  こうすると EVENTS.sort / ticketKind / getSortDate を1文字も変えずに済む（sort_guard に触らない）。

なぜ2種類要るか:
  ぴあの実文言には「予定枚数終了（売り切れ）」と「販売終了（販売期間が終わっただけ）」がある。
  一緒くたに「予定枚数終了」と出すのは嘘（工藤静香4枠・原田知世1枠・宝塚3枠）。
  かといってマークを外すと「販売中 〜8/21」と出て、買えないのに買えるように見える＝もっと悪い。

CRLF維持（feedback_index_html_crlf_preserve）。"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'index.html'
h = open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
orig = h


def sub1(pat, rep, why):
    global h
    rx = re.escape(pat).replace('\\\n', '\\r?\\n')
    h2, n = re.subn(rx, lambda _m: rep.replace('\n', NL), h, count=1)
    assert n == 1, '%s: 置換%d件' % (why, n)
    h = h2
    print('  ✓', why)


# ① CSS（点線枠で「予定枚数終了」と見分ける）
CSS_ANCHOR = '    .ticket-item.soldout .ticket-date { color: var(--text-muted); text-decoration: line-through; }'
sub1(CSS_ANCHOR, CSS_ANCHOR + '''

    /* 販売終了＝売り切れではなく「販売期間が終わった」枠（ユーザー選択 2026-08-14）。
       予定枚数終了(実線)と区別できるよう点線枠にする。データ上は soldout のままなので
       並び順・カウントダウン除外・公演日を過ぎたら消える安全弁は共通。 */
    .ticket-item.soldout .ticket-soldout-badge.saleended {
      border-style: dashed;
      background: rgba(120, 130, 150, 0.14);
    }''', 'CSS に .ticket-soldout-badge.saleended を追加')

# ② renderCard のバッジ文言だけ切り替え（分岐そのものは既存の t.soldout ブロックのまま）
sub1('            <div class="ticket-soldout-badge">予定枚数終了</div>',
     '            <div class="ticket-soldout-badge${t.saleEnded ? " saleended" : ""}">'
     '${t.saleEnded ? "販売終了" : "予定枚数終了"}</div>',
     'renderCard のバッジ文言を saleEnded で切り替え')

open('index.html.bak_0814_saleended2', 'w', encoding='utf-8', newline='').write(orig)
open(P, 'w', encoding='utf-8', newline='').write(h)
print('→ 適用（並び順ロジックは無変更・backup index.html.bak_0814_saleended2）')
