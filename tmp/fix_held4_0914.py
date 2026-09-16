# -*- coding: utf-8 -*-
"""ヒールの安全弁で止まった4件を、単発で確かめたうえで手で当てる（2026-09-14 朝）。
取り直しの中身＝tmp/heal_ids_held4_0914.json（heal_stale_deadlines --ids 615,4412,5016,5193 --build の控え）。
🚨 heal の --apply は --ids を付けても控えの中身を全部当てる作りなので、ここで1件ずつ決めて当てる。

  615 稲垣潤一＝取り直し10枠に入れ替え。千葉11/28（eventCd=2627762）はぴあから消えたが、
       生HTMLで「予定枚数終了」（tools/pia_statustext.py）＝消さずに soldout の印で残す（DELETE_GATE 1.）。
  4412 T.M.Revolution＝取り直しの枠はURLが付いていない＝そのまま当てると飛び先が壊れる。
       いまのプレリザーブ枠の券種名だけ「〜9/17 23:59」の締切形に直し、startDate を外す（url は残す）。
  5016 TJHiroshima＝「9月号」の文字が落ちるだけ＋一般発売2枠（〜9/30）が増える＝取り直しをそのまま当てる。
  5193 新感線＝飛び先が bundle→eventCd に変わるだけ・3次受付の締切時刻が正しくなる＝取り直しをそのまま当てる。

使い方: python tmp/fix_held4_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids_held4_0914.json', encoding='utf-8'))}

src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

# 615：取り直し10枠＋千葉を売り切れで残す
e = by[615]
chiba = [t for t in e['tickets'] if '（千葉 11/28公演）' in (t.get('type') or '')]
assert len(chiba) == 1, '千葉の枠が1本でない %d' % len(chiba)
chiba[0]['soldout'] = True
chiba[0]['soldoutSince'] = TODAY
new615 = list(built[615]['tickets']) + chiba
print('615: %d枠 → %d枠（千葉は売り切れの印）' % (len(e['tickets']), len(new615)))
e['tickets'] = new615

# 4412：プレリザーブの券種名だけ締切形に
e = by[4412]
hit = [t for t in e['tickets'] if (t.get('type') or '').startswith('プレリザーブ（愛知 12/26公演）')]
assert len(hit) == 1, 'プレリザーブ枠が1本でない %d' % len(hit)
print('4412: %s → プレリザーブ（愛知 12/26公演）〜9/17 23:59（url=%s）' % (hit[0]['type'], hit[0].get('url')))
hit[0]['type'] = 'プレリザーブ（愛知 12/26公演）〜9/17 23:59'
hit[0]['date'] = '2026-09-17'
hit[0].pop('startDate', None)

# 5016・5193：取り直しをそのまま（非ぴあ枠は無いことを確かめる）
for i in (5016, 5193):
    e = by[i]
    assert not [t for t in e['tickets'] if (t.get('url') or '') and 'pia.jp' not in t['url']], 'id%s に非ぴあ枠がある' % i
    print('%s: %d枠 → %d枠' % (i, len(e['tickets']), len(built[i]['tickets'])))
    e['tickets'] = list(built[i]['tickets'])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
io.open('index.html', 'w', encoding='utf-8', newline='').write(src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():])
print('書き込み完了')
