# -*- coding: utf-8 -*-
"""push前の照合（21:33・reconcile_pia --ids）の引っかかりを、ぴあの生の行（tmp/raw_rows_2133_0914.md）どおりに直す（2026-09-14 夜）。
・2127 ナイロン100℃＝本多劇場の一般発売〜9/24 がぴあで「販売期間中」に戻っていた＝今夜付けた売り切れの印を外す
                     当日引換券販売＝「〜9/27 10:00」で受付中＝発売日の形のまま隠れていた枠に締切を入れる
・3875 タイムトラベラーズ・ワイフ＝当日券キャンセル待ち整理券が予定枚数終了＝売り切れの印
・7165 天神落語まつり＝11/1 FFGホール（F-5）が今夜のうちに予定枚数終了＝売り切れの印
・5044 打首獄門同好会＝ev.date が 12/3 のまま（本当はこれからの公演が R9年 1/31 福岡まで）＝画面から先に消える（QC-EVDATE）
    → 会期を「これから行われる全公演」（9/24 東京〜R9年 1/31 福岡・19会場）に。場所の欄も岡山・広島だけ→全国
    → 11/27 東京 追加発売（予定枚数終了）＝売り切れの印／「2027／1／16」の全角の二重（同じ売り場・同じ締切）を1枠に
使い方: python tmp/fix_2133_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
from build_pia_entries import norm_fw

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}


def tk(i, ty):
    hit = [t for t in by[i]['tickets'] if t.get('type') == ty]
    assert len(hit) == 1, 'id%s の枠が1つに決まらない（%d）: %s' % (i, len(hit), ty)
    return hit[0]


def sold(t):
    t['soldout'] = True
    t['soldoutSince'] = TODAY


# 2127
t = tk(2127, '一般発売（東京 9/5〜9/27公演）〜9/24 23:59')
t.pop('soldout', None)
t.pop('soldoutSince', None)
t = tk(2127, '当日引換券販売（東京 9/15〜9/27公演）9/13 10:00発売')
t['type'] = '当日引換券販売（東京 9/15〜9/27公演）〜9/27 10:00'
t['date'] = '2026-09-27'
t['startDate'] = '2026-09-13'
# 3875
sold(tk(3875, '当日券キャンセル待ち整理券（東京 9/5〜9/24公演）〜9/15 10:00'))
# 7165
sold(tk(7165, '一般発売【FFGホール】（福岡 11/1公演）〜10/31 23:59'))
# 5044
e = by[5044]
sold(tk(5044, '追加発売（東京 11/27公演）9/12 10:00発売'))
dup = tk(5044, '2027／1／16（土）公演 一般発売（宮城 R9年 1/16公演）〜12/23 23:59')
keep = tk(5044, '2027/1/16（土）公演 一般発売（宮城 R9年 1/16公演）〜12/23 23:59')
assert dup.get('url') == keep.get('url') and dup['date'] == keep['date']
e['tickets'] = [x for x in e['tickets'] if x is not dup]
VENUES = ['ＥＸ ＴＨＥＡＴＥＲ ＲＯＰＰＯＮＧＩ', '桜坂セントラル', 'ＣＲＡＺＹＭＡＭＡ ＫＩＮＧＤＯＭ', 'ＧＯＲＩＬＬＡ ＨＡＬＬ ＯＳＡＫＡ',
          '金沢ＥＩＧＨＴ ＨＡＬＬ', 'ペニーレーン２４', 'ＤＲＵＭ ＬＯＧＯＳ', 'ＷｓｔｕｄｉｏＲＥＤ', 'ダイアモンドホール',
          'Ｃｌｕｂ ＳＷＩＮＤＬＥ', 'ＳＥＮＤＡＩ ＧＩＧＳ', 'Ｓｈｉｂｕｙａ ＬＯＶＥＺ', '広島ＪＭＳアステールプラザ 大ホール',
          'カナモトホール', '新潟テルサ', '神戸国際会館こくさいホール', 'トークネットホール仙台 大ホール',
          'Ｎｉｔｅｒｒａ日本特殊陶業市民会館 フォレストホール', '福岡国際会議場 メインホール']
e['date'] = '2027-01-31'
e['dateLabel'] = '2026年9月24日(木)〜2027年1月31日(日) 全国ツアー'
e['venue'] = norm_fw('全国ツアー（' + '／'.join(VENUES) + '）')
e['prefecture'] = '全国'
for i in (2127, 3875, 7165, 5044):
    x = by[i]
    print('## id%s %s ｜date %s ｜%s' % (i, x['name'], x['date'], x['dateLabel']))
    for t in x['tickets']:
        print('   %s ｜締切 %s%s' % (t['type'], t['date'], '｜売り切れ' if t.get('soldout') else ''))
print('5044 venue＝%s' % by[5044]['venue'])
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
