# -*- coding: utf-8 -*-
# 11/24 朝 すちこ「ボタンの並び順がバラバラよね　チケット売り場の小さなボタンは下に　大きなボタンは上の方に」
# ＝カードの下のボタンを「横長の大きいボタン（btn-wide）→ 小さいボタン」の順に並べ直す（同じ組の中の順はこれまでどおり）
import io, os, time
os.chdir('C:/Users/user/oshinavi')
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'order_btns'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    a = ('      .map(btnHTML)\r\n'
         '      .join("") + amazonMusicBtn + hotelBtn + kidsWorkBtn + wrestlingBtn + genreAmazonBtn + piaBtn;\r\n')
    b = ('      .map(btnHTML)\r\n'
         '      .concat([amazonMusicBtn, hotelBtn, kidsWorkBtn, wrestlingBtn, genreAmazonBtn, piaBtn])\r\n'
         '      .filter(Boolean)\r\n'
         '      // 🆕2026-11-24 すちこ「チケット売り場の小さなボタンは下に　大きなボタンは上の方に」＝横長（btn-wide）を先に・小さいボタンを後に\r\n'
         '      .sort((x, y) => (y.includes(" btn-wide") ? 1 : 0) - (x.includes(" btn-wide") ? 1 : 0))\r\n'
         '      .join("");\r\n')
    assert t.count(a) == 1, t.count(a)
    t = t.replace(a, b)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
    print('ok')
finally:
    os.remove(LK)
