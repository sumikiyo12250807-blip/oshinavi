# -*- coding: utf-8 -*-
# 11/23 すちこ「なんか違う」→「会場近くのホテルを探す　で」＝宿の帯を、いつもの画像のボタン「会場近くのホテルを探す」を横に大きくした形に
#   行き先は会場名＋公演日の Expedia のまま・場所は売り場のバッジのすぐ下のまま
import io, os, re, time
R = 'C:/Users/user/oshinavi/'
P = R + 'index.html'
LK = R + 'tmp/x1112/index.lock'
OLD_HTML = '''`<a class="hotel-strip" href="${hotelHref}" target="_blank" rel="nofollow noopener"><span class="hs-ico">🏨</span><span class="hs-txt"><b>${hotelDest}</b>の近くの宿${hotelNight ? `（${hotelNight}泊）` : ""}を探す</span><span class="hs-go">›</span></a>`'''
NEW_HTML = '''`<div class="hotel-wide"><a class="ticket-link-btn btn-hotel${btnImgCls("会場近くのホテルを探す")}" href="${hotelHref}" target="_blank" rel="nofollow noopener" title="${hotelDest}の近くの宿${hotelNight ? `（${hotelNight}泊）` : ""}">${btnInner("🏨", "会場近くのホテルを探す")}</a></div>`'''
NEW_CSS = '''.hotel-wide{margin:4px 24px 8px}
.hotel-wide .ticket-link-btn{display:block;width:100%;text-align:center}
.hotel-wide .ticket-link-btn img{width:100%;max-width:560px;height:auto}'''
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'hotel_strip4'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open(P, encoding='utf-8', newline='').read()
    n1 = t.count(OLD_HTML)
    t = t.replace(OLD_HTML, NEW_HTML)
    m = re.search(r'\.hotel-strip\{display:flex.*?\.hotel-strip:hover\{[^}]*\}', t, re.S)
    nl = '\r\n' if '\r\n' in m.group(0) else '\n'
    t = t[:m.start()] + NEW_CSS.replace('\n', nl) + t[m.end():]
    if n1 == 1:
        io.open(P, 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
io.open(R + 'tmp/x1123/hotel_strip4.txt', 'w', encoding='utf-8').write('HTML %d・CSS 差し替え\n' % n1)
