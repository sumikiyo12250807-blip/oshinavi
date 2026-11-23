# -*- coding: utf-8 -*-
# 11/23 抜き打ち 手で直す分（鍵の中）
#  37549 削除＝TIGET 531971 の開催日 2026-11-13・「このイベントはすでに終了しています」（係と自分で2回読んだ）
#  23411 出演者＝FANY［ネタ出演者］の並び
#  1934 出演者＝12/5・2/7 の回の出演者を足す（今の欄は消さない）
#  29800 出演者＝説明文のスペシャルゲスト Julan を足す
import io, os, sys, time, json
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
LK = 'tmp/x1112/index.lock'
out = io.open('tmp/x1123/spot/fix_spot.txt', 'w', encoding='utf-8')
ART = {
    23411: 'ケビンス／カベポスター／ミカボ／大王／テキセツの街／伝書鳩／パパパジャマ／あなたとネ',
}
ADD = {
    1934: ['林七奈', '江口純子', '豊嶋泰嗣', '田村響', '高木竜馬', '大石彩代', '江口陽子', '石畝馨'],
    29800: ['Julan（ジュラン）'],
}
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_spot23'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    by = {x['id']: x for x in E}
    gone = by[37549]
    assert gone['links'].get('tiget') == 'https://tiget.net/events/531971' and gone['date'] == '2026-12-05'
    E = [x for x in E if x['id'] != 37549]
    out.write('消した 37549 %s\n' % gone['name'])
    for i, a in ART.items():
        out.write('%d 出演 %s → %s\n' % (i, by[i]['artist'], a)); by[i]['artist'] = a
    for i, add in ADD.items():
        cur = by[i]['artist'].split('／')
        new = cur + [x for x in add if x not in cur]
        out.write('%d 出演 %s → %s\n' % (i, by[i]['artist'], '／'.join(new))); by[i]['artist'] = '／'.join(new)
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
lg = io.open('logs/removed_2026-11-23.md', 'a', encoding='utf-8')
lg.write('\n## 13時台 抜き打ちで見つけた終わった公演（1件）\n- 37549 DJダイノジ・大谷 ONE MAN DJ PARTY（カード 12/5 ⇔ 売り場の開催日 11/13・「このイベントはすでに終了しています」）\nhttps://tiget.net/events/531971\n')
lg.close()
out.close()
