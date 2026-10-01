# -*- coding: utf-8 -*-
"""試作（ユーザー「行き先が同じバッジをまとめたほうがいいよ　作ってみて」10/1）
26562 呪物メイト＝日付ごとの30枠を、飛び先（livePocketのページ）ごとに1枚へまとめる
  「各日の受付（東京 11/21〜11/27）〜11/27 10:59」＝その週の最後の日の締切。元の枠は _merged_from に残す（戻せるように）
使い方: python tmp/x1001/jubutsu_merge_badges.py [--apply] → tmp/x1001/jubutsu_merge_badges.txt"""
import io, json, re, sys
root = 'C:/Users/user/oshinavi/'
ID = 26562
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
e = next(x for x in E if x['id'] == ID)
md = lambda iso: '%d/%d' % (int(iso[5:7]), int(iso[8:10]))
by = {}
for t in e['tickets']:
    by.setdefault(t.get('url'), []).append(t)
new = []
for u, ts in by.items():
    ts = sorted(ts, key=lambda t: t['date'])
    first, last = ts[0]['date'], ts[-1]['date']
    tm = re.search(r'(\d{1,2}:\d{2})\s*$', ts[-1]['type'])
    nt = {'type': '各日の受付（東京 %s〜%s）〜%s%s' % (md(first), md(last), md(last), ' ' + tm.group(1) if tm else ''),
          'date': last, 'url': u}
    if all(t.get('soldout') for t in ts):
        nt['soldout'] = True
    new.append(nt)
new.sort(key=lambda t: t['date'])
out = io.open(root + 'tmp/x1001/jubutsu_merge_badges.txt', 'w', encoding='utf-8')
out.write('前 %d枠 → 後 %d枠\n' % (len(e['tickets']), len(new)))
for t in new:
    out.write('  %s | %s\n' % (t['type'], t['url']))
if '--apply' in sys.argv:
    e['_merged_from'] = e['tickets']
    e['tickets'] = new
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
    io.open(root + 'index.html', 'wb').write((text[:st] + body.replace('\n', '\r\n') + text[end:]).encode('utf-8'))
    out.write('書いた\n')
