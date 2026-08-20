# -*- coding: utf-8 -*-
"""8/8朝の削除候補を e+ の検索JSONで一括裏取りする。
「ぴあで0枠」は削除理由にならない（memory: feedback_delete_nonpia_blindspot）。
一覧のラベルは券種名であって販売中ではないので、ヒットしたら /sf/detail/ を個別に開いて確認すること。
"""
import re, sys, io, time, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGETS = [
    ('101',  'ONE SAMURAI'),
    ('361',  'ぎふ長良川花火大会'),
    ('900',  'DISCO Classics'),
    ('1037', 'みえるとか みえないとか'),
    ('1619', '826aska'),
    ('1627', '飯田洋輔'),
    ('1985', 'スマイルコンサート'),
    ('2688', '上野耕平'),
    ('2748', '熊本地震10年復興コンサート'),
    ('2982', '吉野敏明'),
    ('3729', '立川寸志'),
    ('2340', 'osage'),
]
TODAY = '20260808'


def fetch(kw):
    u = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')


def parse(h):
    objs, seen = [], set()
    for m in re.finditer(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h):
        blk = h[max(0, m.start() - 4000):min(len(h), m.end() + 4000)]

        def g(key):
            mm = re.search(r'"%s":"([^"]*)"' % key, blk)
            return mm.group(1).replace('\xa0', ' ') if mm else ''
        url = 'https://eplus.jp' + m.group(1)
        if url in seen:
            continue
        seen.add(url)
        objs.append({
            'url': url,
            'sub': g('kogyo_name_1') + ' ' + g('kogyo_name_2'),
            'koenbi': g('koenbi') or g('koen_start_datetime'),
            'venue': g('kaijo_name'),
            'pref': g('todofuken_name'),
            'status': g('uketsuke_name_pc'),
            'uke_end': g('uketsuke_end_datetime'),
        })
    objs.sort(key=lambda x: x['koenbi'])
    return objs


for eid, kw in TARGETS:
    print('=' * 70)
    print('id=%s  keyword=%s' % (eid, kw))
    try:
        rows = parse(fetch(kw))
    except Exception as ex:
        print('  ERROR %s' % ex)
        continue
    future = [o for o in rows if (o['koenbi'][:8] or '99999999') >= TODAY]
    if not rows:
        print('  e+ヒット0件')
    else:
        print('  e+ヒット %d件 / うち公演日が今日以降 %d件' % (len(rows), len(future)))
        for o in future:
            print('   %s | %s | %s %s | %s | 受付〜%s' % (
                o['koenbi'][:8], o['sub'][:38], o['pref'][:5], o['venue'][:20],
                o['status'][:14], o['uke_end'][:12]))
            print('      %s' % o['url'])
    time.sleep(2)
