# -*- coding: utf-8 -*-
# 11/23 抜き打ち ぴあ・e+ 分（鍵の中）
#  40637 LIVE DI:GA：ぴあ「プリセール＜12/30公演＞」「＜12/31公演＞」受付中〜12/3 23:59（reconcile_pia MISSING 2）を足す・出演者16組（係が売り場で読んだ）
#  54089 東京シティ・フィル：二重になった名前を直し、指揮・共演（係が e+ で読んだ）
#  2908 前橋汀子：大阪 1/11 の［指揮］太田弦［演奏］日本センチュリー交響楽団 を足す
#  4349 ジャック・ザ・リッパー：出演者（係がぴあで読んだ）
import io, os, sys, time, json, subprocess
os.chdir('C:/Users/user/oshinavi')
sys.path.insert(0, 'tools')
import compact_events as C
LK = 'tmp/x1112/index.lock'
out = io.open('tmp/x1123/spot/fix_spot2.txt', 'w', encoding='utf-8')
U = 'https://t.pia.jp/pia/event/event.do?eventCd=2641939'
ART = {
    40637: 'osage／キュウソネコカミ／kobore／四星球／トップシークレットマン／プッシュプルポット／WHITE ASH／夜の本気ダンス／iriencHy／9mm Parabellum Bullet／バックドロップシンデレラ／First Love is Never Returned／フルカワユタカ／Broken my toybox／Base Ball Bear／めっちゃ美人',
    54089: '東京シティ・フィルハーモニック管弦楽団／藤岡幸夫／坂田美子／久保田晶子／滝田美智子／西川浩平／稲葉明徳／中村華子／氏家克典',
    2908: '前橋汀子／ユベール・スダーン／東京交響楽団／太田弦／日本センチュリー交響楽団',
    4349: '木村達成／加藤和樹／松下優也／堂珍嘉邦／新納慎也／平間壮一',
}
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_spot2_23'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    E = C.load(t)
    by = {x['id']: x for x in E}
    e = by[40637]
    for d in ('12/30', '12/31'):
        ty = 'プリセール（東京 %s公演）〜12/3 23:59' % d
        if not any(x.get('type') == ty for x in e['tickets']):
            nt = {'type': ty, 'date': '2026-12-03', 'url': U}
            e['tickets'].insert(0, nt)
            out.write('足した枠 %s\n' % json.dumps(nt, ensure_ascii=False))
    for i, a in ART.items():
        out.write('%d 出演 %s → %s\n' % (i, by[i]['artist'], a)); by[i]['artist'] = a
    s, end, _ = C.locate(t)
    t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
finally:
    os.remove(LK)
r = subprocess.run([sys.executable, 'tools/reconcile_pia.py', '--ids', '40637'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=dict(os.environ, PYTHONIOENCODING='utf-8'))
out.write('=== reconcile_pia --ids 40637 rc=%d\n%s\n' % (r.returncode, r.stdout[-2000:]))
out.close()
