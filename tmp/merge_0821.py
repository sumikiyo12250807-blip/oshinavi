# -*- coding: utf-8 -*-
"""新着プールと既存エントリの重複を統合する（2026-08-21 朝）。

① 4765＋4766 スターダンサーズ・バレエ団「くるみ割り人形」全2幕
   ＝同じ団体・同じ演目の巡演を「神奈川公演」「埼玉公演」で2エントリに割ってしまっていた。
     神奈川 12/5〜12/6 昭和音楽大学テアトロ・ジーリオ・ショウワ
     埼玉   12/26〜12/27 彩の国さいたま芸術劇場 大ホール
   → 4765 に寄せて 4766 は欠番にする（[[feedback_tour_consolidate]]／id振り直し禁止）。

② 3566（既存・八王子南大沢のみ）＋4786（新着・両会場のbundle）「ルーマニアのクリスマス」
   ＝同じ興行。4786 のほうが会場2つぶん揃っているので、3566 を bundle 版に作り替えて
     4786 を欠番にする。
       八王子市南大沢文化会館 主ホール 12/19（一般発売〜12/18 23:59・受付中）
       城西大学紀尾井町キャンパス多目的ホール 12/20（一般発売 8/25 10:00〜）
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

# ① スターダンサーズ
a, b = by[4765], by[4766]
seen = {(t.get('type'), t.get('url')) for t in a['tickets']}
add = [t for t in b['tickets'] if (t.get('type'), t.get('url')) not in seen]
a['name'] = 'スターダンサーズ・バレエ団公演「くるみ割り人形」全2幕'
a['artist'] = 'スターダンサーズ・バレエ団'
a['venue'] = '全国ツアー（昭和音楽大学 テアトロ・ジーリオ・ショウワ／彩の国さいたま芸術劇場 大ホール）'
a['prefecture'] = '神奈川・埼玉'
a['date'] = '2026-12-27'
a['dateLabel'] = '2026年12月5日(土)〜2026年12月27日(日) 神奈川・埼玉'
for t in add:
    t = dict(t)
    t.setdefault('url', (b.get('links') or {}).get('pia'))
    a['tickets'].append(t)
a['verifiedAt'] = '2026-08-21'
print('① 4765 枠%d / date=%s / %s' % (len(a['tickets']), a['date'], a['venue']))
for t in a['tickets']:
    print('    -', t['type'], '|', t.get('date'))

# ② ルーマニアのクリスマス
c, d = by[3566], by[4786]
c['name'] = 'ルーマニアのクリスマス'
c['artist'] = 'ルーマニアのクリスマス'
c['venue'] = d['venue']
c['prefecture'] = d['prefecture']
c['date'] = d['date']
c['dateLabel'] = d.get('dateLabel')
c['links'] = dict(c.get('links') or {}, pia=(d.get('links') or {}).get('pia'))
c['tickets'] = d['tickets']
c['verifiedAt'] = '2026-08-21'
print('② 3566 枠%d / date=%s / %s' % (len(c['tickets']), c['date'], c['venue']))
for t in c['tickets']:
    print('    -', t['type'], '|', t.get('date'))

KEEP = [e for e in EVENTS if e['id'] not in (4766, 4786)]
assert len(KEEP) == len(EVENTS) - 2
shutil.copyfile('index.html', 'index.html.bak_0821_merge')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 → %d件（4766・4786 を欠番に） ===' % (len(EVENTS), len(KEEP)))
