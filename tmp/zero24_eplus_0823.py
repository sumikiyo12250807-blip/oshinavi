# -*- coding: utf-8 -*-
"""バッジ0の24件を e+ で裏取りする（feedback_delete_nonpia_blindspot）。
「ぴあで0枠」は削除理由にならない。e+ に受付終了日が今日以降の枠があれば
＝他社で買える＝削除でなく取り込み。結果はファイルに書く（コンソールに日本語を出さない）。
"""
import io, re, sys, json, time, urllib.parse, urllib.request

TODAY = '20260823'
TARGETS = [
    (43, 'シナモロールワンダートリップ'),
    (2748, '熊本地震10年復興コンサート'),
    (3085, '浦島坂田船'),
    (3696, 'Stray Kids'),
    (4035, '紫 今'),
    (4036, 'Little Parade'),
    (4051, 'K-Drama OST Tribute Concert'),
    (4066, '新サクラ大戦 the Stage'),
    (4080, '澤野弘之'),
    (4081, '梅田サイファー'),
    (4089, '花宮初奈'),
    (4094, 'KAWAII LAB.'),
    (4100, 'Khalid'),
    (4106, '徹子の部屋コンサート'),
    (4117, 'RAINCOVER'),
    (4150, 'FIVE O ONE'),
    (4156, 'IRIS MONDO'),
    (4165, 'ETERNAL FIGHTER TAKERU'),
    (4172, 'Bocchi'),
    (4420, 'Suchmos'),
    (4422, 'yeti let you notice'),
    (4423, 'The Performance Zero'),
    (4424, 'シャッポ'),
    (4425, 'スミワタルトリオ'),
]


def search(kw):
    u = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    h = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
    rows, seen = [], set()
    for m in re.finditer(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h):
        url = 'https://eplus.jp' + m.group(1)
        if url in seen:
            continue
        seen.add(url)
        blk = h[max(0, m.start() - 4000): m.end() + 4000]

        def g(key):
            mm = re.search(r'"%s":"([^"]*)"' % key, blk)
            return mm.group(1) if mm else ''
        rows.append({'url': url, 'venue': g('kaijo_name'), 'pref': g('todofuken_name'),
                     'status': g('uketsuke_name_pc'), 'end': g('uketsuke_end_datetime'),
                     'kogyo': g('kogyo_name_1')})
    return rows


o = io.open('tmp/zero24_eplus_0823.txt', 'w', encoding='utf-8')
o.write('# バッジ0の24件を e+ で裏取り（today=%s）\n\n' % TODAY)
for eid, kw in TARGETS:
    try:
        rows = search(kw)
    except Exception as e:
        o.write('id=%-5d %-26s ❌検索失敗 %s\n' % (eid, kw, e))
        continue
    alive = [r for r in rows if r['end'][:8] >= TODAY]
    if not alive:
        o.write('id=%-5d %-26s e+ヒット%d件 / 受付中0件 → e+にも買える枠なし\n' % (eid, kw, len(rows)))
    else:
        o.write('id=%-5d %-26s 🚨e+に生きている枠 %d件:\n' % (eid, kw, len(alive)))
        for r in alive:
            o.write('        %s | %s | %s | %s | 受付〜%s | %s\n' % (
                r['kogyo'][:34], r['venue'][:22], r['pref'][:6], r['status'][:14], r['end'][:12], r['url']))
    o.flush()
    time.sleep(1.0)
o.close()
print('done')
