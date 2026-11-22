# -*- coding: utf-8 -*-
# Suno のダウンロード残りの見当（2026-11-23 すちこ「これからはカウントしておいてほしい　後何本で終わりよ　一日1本のペースでもいいかも　とか　わたしに伝えて」）
#   Downloads の mp3 を「今の期間の始まり」から数える → 残り・次に戻る日までの日数・1日何本のペースなら足りるか
#   期間＝請求日（毎月28日・Premier 月60回）。画面の残り回数と食い違ったら画面が正（間違えた1回・消した曲は数えられない）
#   使い方: python tools/suno_count.py  → tmp/suno_count.txt にも書く
import os, glob, datetime, io
LIMIT = 60
RENEW_DAY = 28
today = datetime.date.today()
start = today.replace(day=RENEW_DAY) if today.day >= RENEW_DAY else (today.replace(day=1) - datetime.timedelta(days=1)).replace(day=RENEW_DAY)
nxt = (start.replace(day=1) + datetime.timedelta(days=32)).replace(day=RENEW_DAY)
used = []
for f in glob.glob('C:/Users/user/Downloads/*.mp3'):
    d = datetime.date.fromtimestamp(os.path.getctime(f))
    if d >= start:
        used.append(d)
n = len(used)
left = LIMIT - n
days = (nxt - today).days  # 今日から次に戻る日の前日まで
pace = left / days if days else left
if pace >= 2:
    adv = '1日2本のままで足りるわ'
elif pace >= 1:
    adv = '1日1本のペースにすれば足りるわ（2本の日を作ると足りなくなる）'
else:
    adv = '1日1本でも足りない＝%d日ぶん休みが要るわ' % (days - left)
msg = ('Suno のダウンロード：今の期間 %s〜（次に戻るのは %s）・使った %d 本・残り %d 本・戻るまで %d 日 → %s'
       % (start.strftime('%m/%d'), nxt.strftime('%m/%d'), n, left, days, adv))
print(msg)
io.open('C:/Users/user/oshinavi/tmp/suno_count.txt', 'w', encoding='utf-8').write(msg + '\n')
