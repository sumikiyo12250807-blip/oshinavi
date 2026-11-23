# -*- coding: utf-8 -*-
# 11/24 朝 すちこ「いいわね　これを押したら推した感じでお願いね」＝絵つきの横長ボタン（宿ボタンが型）をカードに出す・押すと3px沈む
# 対象＝うちわ・推し活グッズ・オペラグラス・耳栓・観戦グッズ・最新CD・Amazon Music・（会場が決まらないカードの）宿ボタン。ほかの画像ボタンは今のまま
import io, os, shutil, time
os.chdir('C:/Users/user/oshinavi')
for n in ['uchiwa', 'goods', 'operaglass', 'earplug', 'kansen', 'cd', 'amazonmusic']:
    shutil.copyfile('tmp/btn_tpl/wide_%s.png' % n, 'img/btn_wide_%s.png' % n)
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'wide_btns'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    a1 = '    const btnInner = (icon, label) => BTN_IMG[label]\r\n      ? `<img class="btn-img-pic" src="${BTN_IMG[label]}" alt="${label}" loading="lazy" decoding="async">`\r\n      : `${icon} ${label}`;\r\n    const btnImgCls = (label) => BTN_IMG[label] ? " btn-img" : "";\r\n'
    b1 = ('    // 🆕2026-11-24 すちこ「いいわね　これを押したら推した感じでお願いね」＝絵つきの横長ボタン（宿ボタンが型・tmp/btn/wide_icons_1124.py）。横いっぱい・押すと沈む\r\n'
          '    const BTN_WIDE = {\r\n'
          '      "推しうちわを作る": "img/btn_wide_uchiwa.png",\r\n'
          '      "推し活グッズ": "img/btn_wide_goods.png",\r\n'
          '      "オペラグラス": "img/btn_wide_operaglass.png",\r\n'
          '      "ライブ用耳栓": "img/btn_wide_earplug.png",\r\n'
          '      "観戦グッズ": "img/btn_wide_kansen.png",\r\n'
          '      "予習する（最新CD）": "img/btn_wide_cd.png",\r\n'
          '      "Amazon Musicで聴く": "img/btn_wide_amazonmusic.png",\r\n'
          '      "会場近くのホテルを探す": "img/btn_hotel_wide.png",\r\n'
          '    };\r\n'
          '    const btnInner = (icon, label) => BTN_WIDE[label]\r\n'
          '      ? `<img class="btn-wide-pic" src="${BTN_WIDE[label]}" alt="${label}" width="1000" height="124" loading="lazy" decoding="async">`\r\n'
          '      : BTN_IMG[label]\r\n'
          '      ? `<img class="btn-img-pic" src="${BTN_IMG[label]}" alt="${label}" loading="lazy" decoding="async">`\r\n'
          '      : `${icon} ${label}`;\r\n'
          '    const btnImgCls = (label) => BTN_WIDE[label] ? " btn-img btn-wide" : BTN_IMG[label] ? " btn-img" : "";\r\n')
    a2 = '    .btn-img-pic { height: 36px; width: auto; display: block; }\r\n'
    b2 = (a2 + '    /* 🆕2026-11-24 絵つきの横長ボタン＝横いっぱい（最大560px）・押している間だけ3px沈む（宿の帯 .hotel-wide-btn と同じ） */\r\n'
          '    .ticket-link-btn.btn-wide { flex-basis: 100%; max-width: 560px; transition: transform .06s ease, filter .06s ease;'
          ' filter: drop-shadow(0 5px 0 rgba(0,0,0,.55)) drop-shadow(0 0 10px rgba(80,140,255,.35)); -webkit-tap-highlight-color: transparent; }\r\n'
          '    .ticket-link-btn.btn-wide:active { transform: translateY(3px); filter: drop-shadow(0 2px 0 rgba(0,0,0,.55)) drop-shadow(0 0 6px rgba(80,140,255,.3)); }\r\n'
          '    .btn-wide-pic { width: 100%; height: auto; display: block; }\r\n')
    assert t.count(a1) == 1 and t.count(a2) == 1, (t.count(a1), t.count(a2))
    t = t.replace(a1, b1).replace(a2, b2)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
    print('書いた')
finally:
    os.remove(LK)
