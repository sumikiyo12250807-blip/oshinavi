# -*- coding: utf-8 -*-
"""e+ 検索ページ(/sf/search?keyword=)に埋め込まれたJSONから公演を機械抽出する。
検索結果はJSレンダリングだが、データ本体は生HTMLのJSONに入っている（2026-08-03 発見）。
ぴあ外チャネルの取りこぼし確認用。memory: feedback_tour_cross_channel_blindspot
"""
import re, sys, io, json, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

kw = sys.argv[1]
u = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
h = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}),
                           timeout=60).read().decode('utf-8', 'replace')
print('len=%d' % len(h))

# 各公演オブジェクトは koen_detail_url_pc を1つ持つ。その周辺のキーを拾う
objs = []
for m in re.finditer(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h):
    s = max(0, m.start() - 4000)
    e = min(len(h), m.end() + 4000)
    blk = h[s:e]

    def g(key):
        mm = re.search(r'"%s":"([^"]*)"' % key, blk)
        return mm.group(1).replace('\xa0', ' ') if mm else ''
    objs.append({
        'url': 'https://eplus.jp' + m.group(1),
        'kogyo': g('kogyo_name_1'),
        'sub': g('kogyo_name_2'),
        'koenbi': g('koenbi') or g('koen_start_datetime') or g('koenbi_hyoji'),
        'venue': g('kaijo_name') or g('venue_name') or g('kaijyo_name'),
        'pref': g('todofuken_name') or g('ken_name'),
        'status': g('uketsuke_name_pc'),
        'uke_end': g('uketsuke_end_datetime'),
    })

seen, rows = set(), []
for o in objs:
    if o['url'] in seen:
        continue
    seen.add(o['url'])
    rows.append(o)
rows.sort(key=lambda x: x['koenbi'])
for o in rows:
    print('%s | %s | %s | %s | %s | 受付〜%s | %s' % (
        o['koenbi'][:8], o['sub'][:34], o['venue'][:22], o['pref'][:6],
        o['status'][:12], o['uke_end'][:12], o['url']))
print('--- e+公演 %d件 ---' % len(rows))
