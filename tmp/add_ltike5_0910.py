# -*- coding: utf-8 -*-
"""ローチケ 9/21-9/27発売の未登録5件を投入する（2026-09-10）。

ローチケの週スキャン（tools/ltike_week_scan.md）→ ぴあ総ざらいで「ぴあに無い」を確認済み。
素材は全部ローチケのチケット詳細ページを実ブラウザで開いて読んだもの。
URLは組み立てたあと**実際に開いて中身が出るのを確かめてある**。
"""
import io
import json
import re
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')


def u(lc, pk, mthd, sn, name, bv, cc='08'):
    return ('https://l-tike.com/order/?gLcode=' + lc + '&gPfKey=' + quote(pk, safe='')
            + '&gEntryMthd=' + mthd + '&gScheduleNo=' + sn + '&gCarrierCd=' + cc
            + '&gPfName=' + quote(name) + '&gBaseVenueCd=' + bv)


NG_KYUBAN = '東京キューバンボーイズ　コンサート　２０２６　ｉｎ　Ｔｏｋｙｏ'
NG_HAPPY = '長崎スタジアムシティ開業２周年記念　「ＨＡＰＰＩＮＥＳＳ　ＪＡＭ　２０２６」'
U_KYUBAN = u('71873', '20260904000002290127', '01', '1', NG_KYUBAN, '33375')
U_IWASAKI = u('62734', '20260703000002243050', '01', '1', '岩崎宏美＆国府弘子', '69371')
U_HAPPY1 = u('82218', '20260820000002275623', '02', '1', NG_HAPPY, '81620')
U_HAPPY3 = u('82218', '20260820000002275623', '02', '3', NG_HAPPY, '81620')
U_HOSHI = u('70604', '20260727000002258553,20260727000002258557,20260727000002258554',
            '01', '1', '星波', '30723')
U_UTAGOE = u('55628', '20260731000002263533', '01', '1', '歌声コンサート', '51531')
AMZ = 'https://www.amazon.co.jp/s?k=%s&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22'

NEW = [
    {
        "id": 7823,
        "artist": "新しい学校のリーダーズ／Klang Ruler／SWEET STEADY／水曜日のカンパネラ",
        "name": "長崎スタジアムシティ開業2周年記念「HAPPINESS JAM 2026」",
        "date": "2026-10-17",
        "dateLabel": "2026年10月17日(土)",
        "venue": "HAPPINESS ARENA",
        "prefecture": "長崎",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": U_HAPPY3, "pia": None, "eplus": None},
        "tickets": [
            {"type": "プレリク先行（長崎 10/17公演）〜9/11 23:59",
             "date": "2026-09-11", "url": U_HAPPY1},
            {"type": "一般発売（長崎 10/17公演）9/23 10:00発売",
             "startDate": "2026-09-23", "date": "2026-09-23", "url": U_HAPPY3},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
    {
        "id": 7824,
        "artist": "見砂和照と東京キューバンボーイズ",
        "name": "東京キューバンボーイズ コンサート 2026 in Tokyo",
        "date": "2026-12-23",
        "dateLabel": "2026年12月23日(水)",
        "venue": "新宿文化センター 大ホール",
        "prefecture": "東京",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": U_KYUBAN, "pia": None, "eplus": None},
        "tickets": [
            {"type": "一般発売（東京 12/23公演）9/24 10:00発売",
             "startDate": "2026-09-24", "date": "2026-09-24", "url": U_KYUBAN},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
    {
        "id": 7825,
        "artist": "岩崎宏美／国府弘子",
        "name": "岩崎宏美＆国府弘子 Piano Songs",
        "date": "2026-12-26",
        "dateLabel": "2026年12月26日(土)",
        "venue": "江津市総合市民センター",
        "prefecture": "島根",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": U_IWASAKI, "pia": None, "eplus": None,
                  "amazon": AMZ % quote('岩崎宏美')},
        "tickets": [
            {"type": "一般発売（島根 12/26公演）9/26 10:00発売",
             "startDate": "2026-09-26", "date": "2026-09-26", "url": U_IWASAKI},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
    {
        "id": 7826,
        "artist": "星波",
        # ローチケの詳細ページに「タイトル：」欄が無い＝公演名は出ていない。
        # 勝手に「ワンマンライブ」等と足さない（[[feedback_no_fake_info]]）
        "name": "星波",
        "date": "2026-10-18",
        "dateLabel": "2026年10月18日(日)",
        "venue": "原宿ストロボカフェ",
        "prefecture": "東京",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": U_HOSHI, "pia": None, "eplus": None,
                  "amazon": AMZ % quote('星波')},
        "tickets": [
            {"type": "一般発売（東京 10/18公演）9/23 10:00発売",
             "startDate": "2026-09-23", "date": "2026-09-23", "url": U_HOSHI},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
    {
        "id": 7827,
        "artist": "歌声コンサート",
        "name": "歌声コンサート",
        "date": "2026-12-05",
        "dateLabel": "2026年12月5日(土)",
        "venue": "野洲文化小劇場",
        "prefecture": "滋賀",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": U_UTAGOE, "pia": None, "eplus": None},
        "tickets": [
            {"type": "一般発売（滋賀 12/5公演）9/26 10:00発売",
             "startDate": "2026-09-26", "date": "2026-09-26", "url": U_UTAGOE},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
]

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
have = {e['id'] for e in events}
for e in NEW:
    if e['id'] in have:
        print('!! id%d は既にある。中止' % e['id'])
        sys.exit(1)
events.extend(NEW)
print('EVENTS %d → %d' % (len(events) - len(NEW), len(events)))
out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

ids = [e['id'] for e in NEW]
mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', out, re.S)
arr = json.loads(mo.group(2))
arr2 = ids + [i for i in arr if i not in ids]     # 新着のいちばん上へ
print('NEW_ORDER %d → %d / 先頭 %s' % (len(arr), len(arr2), arr2[:10]))
out = out[:mo.start()] + mo.group(1) + json.dumps(arr2) + mo.group(3) + out[mo.end():]

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)

h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
pool = {e['id'] for e in ev if e.get('genre') == 'new'}
no = json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h, re.S).group(1))
print('新着プール %d / NEW_ORDER %d / 差 %s %s'
      % (len(pool), len(no), sorted(pool - set(no))[:5], sorted(set(no) - pool)[:5]))
print('書き込み完了')
