# -*- coding: utf-8 -*-
# 本人の作品と言い切れない2枚（55338 舟木一夫＝いろいろな歌手の集めた盤・52450 久末航＝CDか分からない）の商品ページを外す
import io, os, sys, time
R = 'C:/Users/user/oshinavi/'
sys.path.insert(0, R + 'tools')
import compact_events as C
LK = R + 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'dp_drop'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open(R + 'index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    n = 0
    for e in E:
        if e['id'] in (55338, 52450):
            e['links'].pop('amazonDp', None); e['links'].pop('amazonDpTitle', None); n += 1
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open(R + 'index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
io.open(R + 'tmp/x1123/dp_drop.txt', 'w', encoding='utf-8').write('外した %d\n商品ページの飛び先の差し替え入り=%s\n' % (n, '(d.key === "amazon" && ev.links.amazonDp)' in t))
