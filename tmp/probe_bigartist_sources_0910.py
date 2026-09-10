# -*- coding: utf-8 -*-
"""「大物の公演」を売り場に依存せず知る情報源が、機械で読めるかを当たる。

きっかけ（2026-09-10 ユーザー）＝
  「昨日藤井風が oshinavi.jp に無かった件。大物で、みんなが行きたそうなコンサートで
   うちに無いものが無いか探してほしい。どこかから情報とれないかな」

🚨藤井風は **e+の独占**（eplus.jp/fujiikaze-pianorecital/）だったので、
  ぴあや楽天のランキングを見ても引っかからない。**売り場に依存しない一覧**が要る。
"""
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

CANDS = [
    ('ライブイベントカレンダー(全国)', 'https://live-events.a-jp.org/soko/cld/'),
    ('ライブイベント 東京', 'https://live-events.a-jp.org/soko/prf/13.html'),
    ('ぴあ 音楽トップ', 'https://t.pia.jp/music/'),
    ('ローチケ コンサート', 'https://l-tike.com/concert/'),
    ('音楽ナタリー ライブ情報', 'https://natalie.mu/music/schedule'),
    ('e+ 音楽ランキング', 'https://eplus.jp/sf/music/ranking'),
]

for name, u in CANDS:
    try:
        req = urllib.request.Request(u, headers=UA)
        r = urllib.request.urlopen(req, timeout=30)
        body = r.read().decode('utf-8', 'replace')
    except Exception as ex:
        print('%-26s ❌ %r' % (name, ex))
        continue
    txt = re.sub(r'<script.*?</script>', ' ', body, flags=re.S)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = re.sub(r'\s+', ' ', txt)
    dates = len(re.findall(r'20\d{2}[/年.-]\s?\d{1,2}[/月.-]\s?\d{1,2}', txt))
    links = len(re.findall(r'href="', body))
    print('%-26s ✅ status=%s len=%-7d 日付らしき %-4d リンク %-4d' % (name, r.status, len(body), dates, links))
    print('     %s' % txt[:220])
