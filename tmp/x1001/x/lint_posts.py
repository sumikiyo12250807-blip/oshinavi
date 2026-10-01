"""10/2発売のX本文（post01〜10.txt）の機械検品。
 ①1行目＝OSHINAVIの"9/30チケット発売"ピックアップ🎫 ②▼チケット情報はこちら の次の行が oshinavi.jp で始まる
 ③タグ #OSHINAVI #明日発売 #チケット ④「。」の直後は改行（閉じカッコ等は許す）
 ⑤封印語（生で浴び／動く系／続く系） ⑥件数の実数（\\d+件）＝丸めの「◯件以上/◯件近く/数件」以外
 ⑦M/D(曜) の曜日を実カレンダーで照合 ⑧同じバッチ内で同じ締め文が2回出ていないか"""
import datetime, glob, re, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
WD = '月火水木金土日'
BLACK = [r'生で浴び', r'動く|動き出|動いて|動いた', r'続く|続いて', r'ひと押し|一押し', r'手帳', r'あんた', r'悪くない', r'トークショー']
bad = 0
lasts = Counter()
for p in sorted(glob.glob('tmp/x1001/x/post*.txt')):
    s = open(p, encoding='utf-8').read().replace('\r\n', '\n')
    L = s.split('\n')
    errs = []
    if L[0].strip() != 'OSHINAVIの"10/2チケット発売"ピックアップ🎫':
        errs.append('1行目: ' + L[0][:40])
    k = [i for i, l in enumerate(L) if l.strip() == '▼チケット情報はこちら']
    if not k or not L[k[0] + 1].strip().startswith('oshinavi.jp'):
        errs.append('CTAの次の行がoshinavi.jpでない')
    if '#OSHINAVI #明日発売 #チケット' not in s:
        errs.append('タグ')
    for m in re.finditer(r'。(?![\n」』）)】])', s):
        errs.append('「。」の後が改行でない: …' + s[max(0, m.start() - 12):m.end() + 6].replace('\n', '⏎'))
    for b in BLACK:
        for m in re.finditer(b, s):
            errs.append('封印語: ' + m.group(0))
    for m in re.finditer(r'(\d+)件(?!以上|近く)', s):
        errs.append('件数の実数: ' + s[max(0, m.start() - 8):m.end() + 4].replace('\n', '⏎'))
    for m in re.finditer(r'(\d{1,2})/(\d{1,2})[（(]([月火水木金土日])', s):
        mo, d, w = int(m.group(1)), int(m.group(2)), m.group(3)
        y = 2026 if mo >= 9 else 2027
        real = WD[datetime.date(y, mo, d).weekday()]
        if real != w:
            errs.append('曜日: %s/%s(%s) は実際は%s' % (mo, d, w, real))
    body = [l for l in L if l.strip() and not l.startswith('#')]
    if body:
        lasts[body[-1].strip()] += 1
    print(p.split('\\')[-1].split('/')[-1], len(s), '字', 'OK' if not errs else 'NG')
    for e in errs:
        print('   ', e)
    bad += len(errs)
for t, n in lasts.items():
    if n > 1:
        print('同じ締めが%d本: %s' % (n, t)); bad += 1
print('NG合計', bad)
sys.exit(1 if bad else 0)
