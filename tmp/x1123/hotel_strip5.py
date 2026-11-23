# -*- coding: utf-8 -*-
# 11/23 すちこ「これを押すと沈む様にして」＝すちこがくれた横長の宿ボタン（img/btn_hotel_wide.png）に替え、押している間だけ3px下へ・下の影を浅く
import io, os, re, time
R = 'C:/Users/user/oshinavi/'
P = R + 'index.html'
LK = R + 'tmp/x1112/index.lock'
OLD = '''`<div class="hotel-wide"><a class="ticket-link-btn btn-hotel${btnImgCls("会場近くのホテルを探す")}" href="${hotelHref}" target="_blank" rel="nofollow noopener" title="${hotelDest}の近くの宿${hotelNight ? `（${hotelNight}泊）` : ""}">${btnInner("🏨", "会場近くのホテルを探す")}</a></div>`'''
NEW = '''`<div class="hotel-wide"><a class="hotel-wide-btn" href="${hotelHref}" target="_blank" rel="nofollow noopener" title="${hotelDest}の近くの宿${hotelNight ? `（${hotelNight}泊）` : ""}"><img src="img/btn_hotel_wide.png" alt="会場近くのホテルを探す" width="1000" height="124" loading="lazy" decoding="async"></a></div>`'''
CSS_RE = r'\.hotel-wide\{margin:4px 24px 8px\}.*?\.hotel-wide \.ticket-link-btn img\{[^}]*\}'
NEW_CSS = '''.hotel-wide{margin:4px 24px 10px}
.hotel-wide-btn{display:block;max-width:560px;margin:0 auto;line-height:0;transition:transform .06s ease,filter .06s ease;filter:drop-shadow(0 5px 0 rgba(0,0,0,.55)) drop-shadow(0 0 10px rgba(80,140,255,.35));-webkit-tap-highlight-color:transparent}
.hotel-wide-btn img{width:100%;height:auto;display:block}
.hotel-wide-btn:active{transform:translateY(3px);filter:drop-shadow(0 2px 0 rgba(0,0,0,.55)) drop-shadow(0 0 6px rgba(80,140,255,.3))}'''
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'hotel_strip5'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open(P, encoding='utf-8', newline='').read()
    n1 = t.count(OLD)
    m = re.search(CSS_RE, t, re.S)
    if n1 == 1 and m:
        t = t.replace(OLD, NEW)
        m = re.search(CSS_RE, t, re.S)
        nl = '\r\n' if '\r\n' in m.group(0) else '\n'
        t = t[:m.start()] + NEW_CSS.replace('\n', nl) + t[m.end():]
        io.open(P, 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
io.open(R + 'tmp/x1123/hotel_strip5.txt', 'w', encoding='utf-8').write('HTML %d・CSS %s\n' % (n1, bool(m)))
