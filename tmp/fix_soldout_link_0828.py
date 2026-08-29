# -*- coding: utf-8 -*-
"""予定枚数終了／販売終了の枠も、タップで売り場へ飛べるようにする（2026-08-28 ユーザー指示）。

Why: 売り切れでも「どこで売っていたか」を見に行けるべき。買える枠は既に
     <a class="ticket-item-link"> になっているのに、soldout だけ <div> でタップできなかった。
     リンク先の決め方は買える枠と同じ＝ t.url（会場別）優先、無ければ ev.links の優先順。
🚨 index.html は CRLF。パターン側の改行を実ファイルに合わせてから置換する。
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
s = io.open(P, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s[:4000] else '\n'

OLD = '''      if (t.soldout) {
        if (parseDateStr(ev.date) < today) return "";
        return `
          <div class="ticket-item soldout">
            <div class="ticket-type">
              <span class="ticket-dot"></span>
              <span class="ticket-type-text">${highlightShowDate(shrinkPrefList(badgeType))}</span>
            </div>
            <div class="ticket-date">${formatDate(t.date)}</div>
            <div class="ticket-soldout-badge${t.saleEnded ? " saleended" : ""}">${t.saleEnded ? "販売終了" : "予定枚数終了"}</div>
          </div>`;
      }'''

NEW = '''      if (t.soldout) {
        if (parseDateStr(ev.date) < today) return "";
        // 売り切れ・販売終了でも「どこで売っていたか」を見に行けるようにする（ユーザー指示 2026-08-28）。
        // リンク先の決め方は買える枠と同じ＝会場別 t.url を優先、無ければカード共通リンク。
        const soldLinkUrl = t.url || (ev.links && (ev.links.rakuten || ev.links.pia || ev.links.eplus || ev.links.lawson || ev.links.fany || ev.links.yoshimoto || ev.links.tvasahi || ev.links.shochiku || ev.links.official));
        const soldInner = `
            <div class="ticket-type">
              <span class="ticket-dot"></span>
              <span class="ticket-type-text">${highlightShowDate(shrinkPrefList(badgeType))}</span>
            </div>
            <div class="ticket-date">${formatDate(t.date)}</div>
            <div class="ticket-soldout-badge${t.saleEnded ? " saleended" : ""}">${t.saleEnded ? "販売終了" : "予定枚数終了"}</div>`;
        return soldLinkUrl
          ? `<a class="ticket-item soldout ticket-item-link" href="${soldLinkUrl}" target="_blank" rel="noopener">${soldInner}</a>`
          : `<div class="ticket-item soldout">${soldInner}</div>`;
      }'''

old = OLD.replace('\n', nl)
new = NEW.replace('\n', nl)
assert s.count(old) == 1, '置換対象が%d個' % s.count(old)
io.open(P, 'w', encoding='utf-8', newline='').write(s.replace(old, new))
print('renderCard の soldout をリンク化した')
