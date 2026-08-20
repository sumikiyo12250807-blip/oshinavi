# -*- coding: utf-8 -*-
"""「販売終了」バッジを新設する（ユーザー選択 2026-08-14・選択肢2）。

なぜ:
  ぴあの実文言には「予定枚数終了（＝売り切れ）」と「販売終了（＝販売期間が終わっただけ）」の
  2種類があるのに、mark_soldout がエントリ単位で一括マークしていたため、売り切れていない枠まで
  「予定枚数終了」と表示していた（工藤静香4枠・原田知世1枠・宝塚3枠）。
  かといってマークを外すと「販売中 〜8/21」と出て、買えないのに買えるように見える（もっと悪い）。
  → 第3の状態 `saleEnded` を作り、グレーの「販売終了」バッジで正直に出す。

やること（3面ぜんぶ）:
  ① index.html の CSS に .ticket-saleended-badge を追加
  ② index.html の renderCard に t.saleEnded 分岐を追加（soldout と同じ安全弁＝公演日を過ぎたら消す）
  ③ データ側は別スクリプト（fix_saleended_0814.py）で付ける
CRLF維持（feedback_index_html_crlf_preserve）。"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'index.html'
h = open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
orig = h

def sub1(pat, rep, why):
    """index.html は CRLF なので、パターン中の \n を \r?\n として当てる。"""
    global h
    rx = re.escape(pat).replace('\\\n', '\\r?\\n')
    h2, n = re.subn(rx, lambda _m: rep.replace('\n', NL), h, count=1)
    assert n == 1, '%s: 置換%d件' % (why, n)
    h = h2
    print('  ✓', why)

# ① CSS
CSS_ANCHOR = '''    .ticket-item.soldout .ticket-date { color: var(--text-muted); text-decoration: line-through; }'''
CSS_NEW = CSS_ANCHOR + '''

    /* 販売終了＝売り切れではなく「販売期間が終わった」枠（2026-08-14 ユーザー選択）。
       予定枚数終了と別バッジにする。消すと「載ってなかった」と誤解されるので出し続ける。 */
    .ticket-saleended-badge {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      padding: 2px 7px;
      border-radius: 4px;
      display: inline-block;
      width: fit-content;
      white-space: nowrap;
      background: rgba(120, 130, 150, 0.16);
      color: var(--text-muted);
      border: 1px dashed rgba(120, 130, 150, 0.5);
    }
    .ticket-item.saleended { opacity: 0.6; border-color: rgba(120,130,150,0.3); }
    .ticket-item.saleended .ticket-dot { background: var(--text-muted); }
    .ticket-item.saleended .ticket-date { color: var(--text-muted); text-decoration: line-through; }'''
sub1(CSS_ANCHOR, CSS_NEW, 'CSS に .ticket-saleended-badge を追加')

# ② renderCard
RC_ANCHOR = '''            <div class="ticket-soldout-badge">予定枚数終了</div>
          </div>`;
      }'''
RC_NEW = RC_ANCHOR + '''
      // 【販売終了】売り切れではなく販売期間が終わった枠（ユーザー選択 2026-08-14）。
      //   ぴあの実文言が「販売終了／受付終了」で、予定枚数終了ではないもの。
      //   外すと「販売中 〜M/D」と出て買えないのに買えるように見えるので、専用バッジで正直に出す。
      //   安全弁は soldout と同じ＝公演日を過ぎたら出さない。
      if (t.saleEnded) {
        if (parseDateStr(ev.date) < today) return "";
        return `
          <div class="ticket-item saleended">
            <div class="ticket-type">
              <span class="ticket-dot"></span>
              <span class="ticket-type-text">${highlightShowDate(shrinkPrefList(badgeType))}</span>
            </div>
            <div class="ticket-date">${formatDate(t.date)}</div>
            <div class="ticket-saleended-badge">販売終了</div>
          </div>`;
      }'''
sub1(RC_ANCHOR, RC_NEW, 'renderCard に t.saleEnded 分岐を追加')

# ③ 並び・状態判定でも saleEnded を soldout と同じ扱いにする
for old, new, why in [
    ('      if (t.soldout) return [3, "9999-99-99", 1];              // 売切=最下',
     '      if (t.soldout || t.saleEnded) return [3, "9999-99-99", 1];  // 売切/販売終了=最下',
     'ソートキーで saleEnded を最下へ'),
]:
    sub1(old, new, why)

n_null = 0
for _ in range(2):
    h2, k = re.subn(r'    if \(t\.soldout\) return null;', '    if (t.soldout || t.saleEnded) return null;', h, count=1)
    if k:
        h = h2
        n_null += 1
print('  ✓ ticketKind/カウントダウン判定で saleEnded を除外 (%d箇所)' % n_null)
h2, k = re.subn(r'        if \(t\.soldout\) continue;', '        if (t.soldout || t.saleEnded) continue;', h, count=1)
assert k == 1
h = h2
print('  ✓ 次アクション算出で saleEnded を除外')

open('index.html.bak_0814_saleended', 'w', encoding='utf-8', newline='').write(orig)
open(P, 'w', encoding='utf-8', newline='').write(h)
print('→ 適用（backup index.html.bak_0814_saleended）')
