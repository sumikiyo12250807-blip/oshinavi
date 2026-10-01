# -*- coding: utf-8 -*-
"""dup_merge で畳んだ「名前が少し違う組」の後始末（10/1昼）
 ① 親の名前に残った1回目の部・時刻の印を外す（怪獣酒場【11:00入店】・へドニア【①13：00】など）
 ② 同じ文字のバッジが並ぶ組に、元のカードの部の印を付ける（Galaxy 昼部/夜部・Odd3Piece 昼/夜など）＝_parts にも入れてヒール後も戻る
 ③ ラフいいね！Z の見出しの「23:59開演」（配信の締切が混ざった）を直す
 ④ 山本達彦 21214（12/5 1st・2nd）を 21218（12/5 夜・12/6）へ寄せる＝同じ名前のツアーは1つ
使い方: python tmp/x1001/fix_merged_names.py [--apply] → tmp/x1001/fix_merged_names.txt"""
import io, json, re, sys
root = 'C:/Users/user/oshinavi/'
APPLY = '--apply' in sys.argv
NAMES = {
    12381: '「Star’s light at Stage Vol.104」 〜天使降臨⁈ 天使の日ライブ in NAGOYA 〜',
    12604: 'Galaxy Festival vol.1 Trick or Galaxy!',
    13093: 'レディオサイエンス・東京ファンミ＠ギブハーツ',
    13211: '小池雅也生誕祭2027「Say 全 魂-soul-」',
    14855: '実りの秋！ぶちぬき魂！',
    15349: '上間江望バースデーイベント Barえみりー 1012',
    15562: 'Odd3Piece 全国Tour 「Oddsession」〜福岡編〜',
    16238: 'Odd3Piece 全国Tour 「Oddsession」〜静岡編〜',
    16826: '喜劇衆ギガンティックシアター 第9回公演『夜更けのチンパンジー』',
    16868: '喜劇衆ギガンティックシアター 第9回公演『夜更けのチンパンジー』',
    20538: 'ラフいいね！Z',
    21050: '「 共鳴 」 #2 ~閃光の架け橋~',
    21218: '山本達彦 <Live en Quatre Saisons・Hiver>',
    22967: '「ＲＥＳＥＴ」公演',
    22985: '「ＲＥＳＥＴ」公演',
    23786: '水槽とクレマチス全国ツアー「誰かの庭で」松山公演',
    24796: '<無銭>His あまふわ ラブホリ',
    24812: '<無銭>His あまふわ ラブホリ',
    25430: 'THE MEATLES 10/11',
    25591: '『 夢喰充電中vol.141・142 』( 夢喰NEON単独公演 )',
    25765: '水槽とクレマチス全国ツアー「誰かの庭で」高知公演',
    26169: '鬼滅の刃フェアコーナー【当日入店申込・先着】10月9日(金)JUMP SHOP大阪梅田店',
    26244: '★With Allen★BD2026 1on1オンライントーク！10/25★FC先行',
    26445: '怪獣酒場新橋蒸溜所”怪獣襲来!”ババルウ星人登場',
    26518: 'へドニアキュクロスアフターイベント',
}
LABELS = {12604: '夜部', 12605: '昼部', 13093: '夜', 13094: '昼', 14855: '1部', 14856: '2部',
          15562: '夜', 15563: '昼', 16238: '夜', 16239: '昼', 16826: '②', 16827: '③', 16868: '④', 16869: '⑤',
          21214: '1st', 21217: '2nd', 21218: '夜公演',
          23786: '第1部', 23787: '第2部', 25765: '第1部', 25766: '第2部'}
DATELABEL = {20538: '2026年9月26日(土) 12:00／15:00／18:00開演（配信は10月3日(土) 23:59まで）',
             21218: '2026年12月5日(土)〜2026年12月6日(日) 東京都 南青山マンダラ'}
pm = json.load(io.open(root + 'tmp/x1001/premerge_map.json', encoding='utf-8'))
url2orig = {u: int(i) for u, i in pm['url2orig'].items()}
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
by = {e['id']: e for e in E}
out = io.open(root + 'tmp/x1001/fix_merged_names.txt', 'w', encoding='utf-8')
gone = set()
# ④ 山本達彦
if 21214 in by and 21218 in by:
    by[21218]['tickets'] = by[21214]['tickets'] + by[21218]['tickets']
    for k in ('extraGenres', '_extraGenres'):
        if by[21214].get(k):
            by[21218][k] = list(dict.fromkeys((by[21218].get(k) or []) + by[21214][k]))
    gone.add(21214)
    out.write('④ 21214 → 21218 へ寄せた\n')
for i, nm in NAMES.items():
    e = by.get(i)
    if not e:
        out.write(f'{i} 無い\n'); continue
    out.write(f"{i} 名前 {e.get('name')} → {nm}\n")
    e['name'] = nm
    if i in DATELABEL:
        out.write(f"   見出し {e.get('dateLabel')} → {DATELABEL[i]}\n")
        e['dateLabel'] = DATELABEL[i]
    parts = dict(e.get('_parts') or {})
    for t in e.get('tickets') or []:
        o = url2orig.get(t.get('url') or '')
        lab = LABELS.get(o)
        if lab and not (t.get('type') or '').startswith('【'):
            t['type'] = '【%s】%s' % (lab, t['type'])
            parts[t['url']] = lab
            out.write(f"   印 {t['type'][:50]}\n")
    if parts:
        e['_parts'] = parts
if APPLY:
    E2 = [e for e in E if e['id'] not in gone]
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E2) + '\n]'
    text = text[:st] + body.replace('\n', '\r\n') + text[end:]
    mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
    ids = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in gone]
    text = text[:mo.start(1)] + ','.join(ids) + text[mo.end(1):]
    io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))
    out.write('書いた\n')
