# -*- coding: utf-8 -*-
"""18時のあとのヒールで止まった26件のうち、ぴあが「予定枚数終了」を出している枠に売り切れの印を付ける（2026-09-14 夜）。
根拠＝tmp/heal_blocked_slotstatus_1805.md（枠ごとに券種名・会場まで合わせて読んだ行）。消さない＝画面には「予定枚数終了」で出し続ける。
印の形は tools/mark_soldout.py と同じ（soldout:true＋soldoutSince）。ぴあ以外の枠には付けない。
使い方: python tmp/mark_sold_1805_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
MARKS = {
    1334: ['一般発売（京都・兵庫・奈良 9/15〜10/17公演）〜10/16 23:59'],
    1772: ['一般発売（愛知 9/25公演）〜9/23 23:59'],
    2127: ['一般発売（東京 9/5〜9/27公演）〜9/24 23:59'],              # 本多劇場の回（配信は別の枠で受付中）
    2990: ['一般発売（新潟 11/29公演）〜11/12 23:59', '一般発売（滋賀 10/24公演）〜10/8 23:59',
           '一般発売（大阪 10/25公演）〜10/8 23:59', '一般発売（滋賀 10/24公演・他の日程も見る）〜10/8 23:59'],
    3053: ['一般発売（三重 10/11公演）〜9/24 23:59'],
    3533: ['一般発売（新潟 9/26公演）〜9/17 23:59', '一般発売（山形 11/28公演）〜11/18 23:59'],
    3722: ['一般発売（東京 R9年 3/26公演）〜3/25 23:59'],
    4246: ['一般発売（東京 11/12〜11/14公演）〜11/13 23:59'],
    4489: ['一般発売（山形/紙チケット）（山形 12/13公演）〜11/5 23:59', '一般発売（山形/電子チケット）（山形 12/13公演）〜11/5 23:59',
           '一般発売【電子チケット】（茨城 12/10公演）〜11/3 23:59', '一般発売【紙チケット】（茨城 12/10公演）〜11/10 23:59'],
    4500: ['一般発売（大阪 11/2公演）〜10/22 23:59', '一般発売（埼玉 R9年 2/20公演）〜2/19 23:59'],
    4634: ['一般発売【10/1（木）～10/12（月）】（千葉 10/1〜10/12公演）〜9/17 23:59'],
    5044: ['一般発売（愛知 11/8公演）〜10/29 23:59'],
    6138: ['一般発売【ファミリーシート】（神奈川 R9年 1/3公演）9/14 12:00発売'],
    8353: ['一般発売（東京 9/29公演）9/14 10:00発売'],                  # 草月ホールの回（配信は受付中）
}
OTHER = re.compile(r'(eplus\.jp|rakuten|l-tike\.com|lawson)')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
done = miss = 0
for i, types in MARKS.items():
    e = by[i]
    for ty in types:
        hit = [t for t in e['tickets'] if t.get('type') == ty and not OTHER.search(t.get('url') or '')]
        if not hit:
            print('❌ id%s 枠が見つからない：%s' % (i, ty))
            miss += 1
            continue
        for t in hit:
            if not t.get('soldout'):
                t['soldout'] = True
                t['soldoutSince'] = TODAY
                done += 1
        print('✅ id%-5s %s ｜%s（%d枠）' % (i, (e.get('name') or '')[:20], ty, len(hit)))
print('\n印を付けた %d枠／見つからない %d' % (done, miss))
if '--apply' not in sys.argv or miss:
    print('(--apply で書き込み・見つからない枠があれば書かない)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
