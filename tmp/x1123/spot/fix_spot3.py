# -*- coding: utf-8 -*-
# 11/23 TIGET 全件見直しの消す候補（自分で売り場を読んだ）
#  30822 削除＝TIGET 528904 開催日 2026年11月07日・「このイベントはすでに終了しています」⇔ カード 2027-11-07
#  16922 公演名＝売り場の今の名前（前の名前に主催者のメールアドレスが入っていた）
#  17058（ツアー・11/07〜12/17 で続いている）・38780（受付終了・四夜は 12/31 まで続くかもしれない）は触らない
import io, os, sys, time
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
LK = 'tmp/x1112/index.lock'
out = io.open('tmp/x1123/spot/fix_spot3.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_spot3_23'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    by = {x['id']: x for x in E}
    g = by[30822]
    assert g['links'].get('tiget') == 'https://tiget.net/events/528904' and g['date'] == '2027-11-07'
    E = [x for x in E if x['id'] != 30822]
    out.write('消した 30822 %s\n' % g['name'])
    by[16922]['name'] = '※追加席発売致します！男のロマンLIVE! イヤー・エンドin代官山2026'
    out.write('16922 公演名を売り場の今の名前に\n')
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
io.open('logs/removed_2026-11-23.md', 'a', encoding='utf-8').write(
    '\n## 15時台 TIGET 全件見直しで見つけた終わった公演（1件）\n- 30822 2分15秒で強制暗転するネタバトル vol.8（カード 2027/11/7 ⇔ 売り場の開催日 2026/11/7・「このイベントはすでに終了しています」）\nhttps://tiget.net/events/528904\n')
out.close()
