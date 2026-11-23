# -*- coding: utf-8 -*-
# 11/23 すちこ「2と3を試してみて」
#  2＝会場が1つのカードは、売り場のバッジのすぐ下に「🏨 会場名の近くの宿（M/D泊）を探す」の帯（行き先は今の宿ボタンと同じ Expedia＋バリューコマース）。帯を出したカードは下のボタン列の宿ボタンを出さない（二重にしない）
#  3＝links.amazonDp（商品ページ）があれば「予習する（最新CD）」の飛び先をそちらに（tools/amazon_dp.py）
import io, os, time
R = 'C:/Users/user/oshinavi/'
P = R + 'index.html'
LK = R + 'tmp/x1112/index.lock'
REPL = [
    # hotelHref を「行き先・場所・日付」の組にする
    ('''    const hotelHref = (() => {
      const v = String(ev.venue || "").trim();
      if (!v || /全国ツアー|／|\\/|、|配信|オンライン|Zaiko Live|Streaming|未定|各地/i.test(v)) return "";
      let dest = v.replace(/[（(][^）)]*[）)]\\s*$/, "").trim();
      if (!dest) return "";''',
     '''    let hotelDest = "", hotelNight = "";   // 🆕11/23 すちこ「2と3を試してみて」＝売り場のすぐ下の宿の帯に使う
    const hotelHref = (() => {
      const v = String(ev.venue || "").trim();
      if (!v || /全国ツアー|／|\\/|、|配信|オンライン|Zaiko Live|Streaming|未定|各地/i.test(v)) return "";
      let dest = v.replace(/[（(][^）)]*[）)]\\s*$/, "").trim();
      if (!dest) return "";
      hotelDest = dest;'''),
    ('''        q += "&startDate=" + ev.date + "&endDate=" + n.toISOString().slice(0, 10);
      }''',
     '''        q += "&startDate=" + ev.date + "&endDate=" + n.toISOString().slice(0, 10);
        hotelNight = (+ev.date.slice(5, 7)) + "/" + (+ev.date.slice(8, 10));
      }'''),
    # 帯を出すカードは下の宿ボタンを出さない
    ('''    const hotelBtn = hotelHref
      ? `''',
     '''    const _hotelLive = !!hotelHref && (ev.tickets || []).some(t => !t.soldout && parseDateStr(t.date) >= today) && !(parseDateStr(ev.date) < today);
    const hotelStrip = _hotelLive
      ? `<a class="hotel-strip" href="${hotelHref}" target="_blank" rel="nofollow noopener"><span class="hs-ico">🏨</span><span class="hs-txt"><b>${hotelDest}</b>の近くの宿${hotelNight ? `（${hotelNight}泊）` : ""}を探す</span><span class="hs-go">›</span></a>`
      : "";
    const hotelBtn = _hotelLive ? "" : hotelHref
      ? `'''),
    # 帯はバッジの下
    ('''        <div class="ticket-section">${ticketsHTML}</div>
        <div class="card-footer">''',
     '''        <div class="ticket-section">${ticketsHTML}</div>${hotelStrip}
        <div class="card-footer">'''),
    # 3＝最新CD の飛び先
    ('''      return `<a class="ticket-link-btn ${d.cls}${btnImgCls(label)}" href="${ev.links[d.key]}" target="_blank" rel="noopener">${btnInner(d.icon, label)}</a>`;''',
     '''      const _href = (d.key === "amazon" && ev.links.amazonDp) ? ev.links.amazonDp : ev.links[d.key];   // 🆕11/23 商品ページがあればそちら（tools/amazon_dp.py）
      return `<a class="ticket-link-btn ${d.cls}${btnImgCls(label)}" href="${_href}" target="_blank" rel="noopener">${btnInner(d.icon, label)}</a>`;'''),
    # 見た目
    ('''.vc-banner{margin-top:12px;text-align:center}''',
     '''.hotel-strip{display:flex;align-items:center;gap:8px;margin:10px 0 2px;padding:10px 12px;border-radius:10px;background:rgba(0,200,135,.12);border:1px solid rgba(0,200,135,.55);color:inherit;text-decoration:none;font-size:13px;line-height:1.4}
.hotel-strip b{font-weight:700}
.hotel-strip .hs-ico{font-size:18px}
.hotel-strip .hs-txt{flex:1;min-width:0}
.hotel-strip .hs-go{font-size:20px;color:#00c887;font-weight:700}
.hotel-strip:hover{background:rgba(0,200,135,.2)}
.vc-banner{margin-top:12px;text-align:center}'''),
]
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'hotel_strip'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open(P, encoding='utf-8', newline='').read()
    log = []
    for a, b in REPL:
        a2, b2 = a.replace('\n', '\r\n'), b.replace('\n', '\r\n')
        if t.count(a2) == 1:
            t = t.replace(a2, b2); log.append('OK')
        elif t.count(a) == 1:
            t = t.replace(a, b); log.append('OK(LF)')
        else:
            log.append('見つからない %d/%d: %s' % (t.count(a2), t.count(a), a[:40]))
    if all(x.startswith('OK') for x in log):
        io.open(P, 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
io.open(R + 'tmp/x1123/hotel_strip.txt', 'w', encoding='utf-8').write('\n'.join(log))
