# -*- coding: utf-8 -*-
# 11/24 抜き打ち 手で直す分（鍵の中）
#  🔴57757 B.LEAGUE ハーフシーズンシート＝売り場「1/19(火)に試合はございません」→ 試合の日に見える表示をやめる（名前・日付の欄・受付名）・締切の日をカードの日に
#  🔴33595 CONTI-NeW FeS＝三次先行は 10/21 で終了・いま受付中は ★一般発売（締切は同じ 12/4・12/5 20:00）→ 受付名を一般発売に・2日券は2日券と書く／出演者の崩れ（日付のかけら・IS:SUE・括弧のかけら）
#  🟠48862 出演者＝売り場の説明文「出演：松本健太／龍之介／高橋研」
#  🟠7140 出演者＝ぴあ［出演］しまじろう／みみりん／とりっぴい／にゃっきい／はなちゃん／ガオガオさん／まなお姉さん
#  🟠4194 ジャンル＝ぴあの札「演劇 バレエ・ダンス」→ dance を足す
#  🟡4507 終わった神奈川の2枠（9/11・11/6 締切）を外し、会期・会場・県を残る東京 12/18 に
import io, os, sys, time
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
LK = 'tmp/x1112/index.lock'
out = io.open('tmp/x1124/spot/fix_spot.txt', 'w', encoding='utf-8')
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_spot24'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    by = {x['id']: x for x in E}
    def setf(i, k, v):
        out.write('%d %s: %s → %s\n' % (i, k, by[i].get(k), v)); by[i][k] = v
    # 57757
    e = by[57757]
    assert 'ハーフシーズンシート' in e['name'] and len(e['tickets']) == 1
    setf(57757, 'artist', '鹿児島レブナイズ')
    setf(57757, 'name', '鹿児島レブナイズ 26-27 ハーフシーズンシート')
    setf(57757, 'dateLabel', '26-27シーズン ホームゲームのハーフシーズンシート（販売は 12/1 だけ）')
    setf(57757, 'date', '2026-12-01')
    e['tickets'][0]['type'] = '一般販売（ハーフシーズンシート）12/1 12:00発売〜12/1 23:59'
    out.write('57757 受付名 → %s\n' % e['tickets'][0]['type'])
    # 33595
    e = by[33595]
    assert all('三次先行' in x['type'] for x in e['tickets'])
    TY = {'P021003': '★一般発売（広島 12/5・12/6 2日券）〜12/4 20:00',
          'P021001': '★一般発売（広島 12/5公演）〜12/4 20:00',
          'P021002': '★一般発売（広島 12/6公演）〜12/5 20:00'}
    for x in e['tickets']:
        k = x['url'][-7:]
        out.write('33595 %s → %s\n' % (x['type'], TY[k])); x['type'] = TY[k]
    setf(33595, 'artist', 'きゃりーぱみゅぱみゅ／CUTIE STREET／KREVA／STARGLOW／flumpool／FRUITS ZIPPER／ベリーグッドマン／MORE STAR／IS:SUE／オーイシマサヨシ／Canna Lily／こっちのけんと／ゴールデンボンバー／水曜日のカンパネラ／トゲナシトゲアリ／fav me')
    setf(48862, 'artist', '松本健太／龍之介／高橋研')
    setf(7140, 'artist', 'しまじろう／みみりん／とりっぴい／にゃっきい／はなちゃん／ガオガオさん／まなお姉さん')
    xg = list(by[4194].get('extraGenres') or [])
    if 'dance' not in xg:
        xg.append('dance')
    setf(4194, 'extraGenres', xg)
    e = by[4507]
    before = len(e['tickets'])
    e['tickets'] = [x for x in e['tickets'] if x['date'] >= '2026-11-24']
    assert len(e['tickets']) == 1 and '12/18' in e['tickets'][0]['type']
    out.write('4507 枠 %d → %d\n' % (before, len(e['tickets'])))
    setf(4507, 'dateLabel', '2026年12月18日(金) 東京 Spotify O-EAST')
    setf(4507, 'venue', 'Spotify O-EAST')
    setf(4507, 'prefecture', '東京')
    for i in (57757, 33595, 48862, 7140, 4194, 4507):
        by[i]['verifiedAt'] = '2026-11-24'
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
out.close()
print('ok')
