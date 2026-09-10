# -*- coding: utf-8 -*-
"""楽天の特設ページ（/features/…）を総ざらいして、そこからしか辿れない公演を拾う。

  python tools/rakuten_features_sweep.py --out tmp/rakuten_features.json
  python tools/rakuten_features_sweep.py --selftest

## なぜ要るか（2026-09-10 ユーザーが見つけた）

ユーザーが https://ticket.rakuten.co.jp/features/sada-tour-2026/ を持ってきて
「これちがうの？」。調べたら**この形はハーベストの入口に1本も入っていなかった**。

🚨入口は2つある:
   post-sitemap26,27        → `/rtXXXX/` 形の公演ページ 1,262本（今まで見ていた）
   **static_event-sitemap.xml → `/features/…` 形の特設ページ 849本（見ていなかった）**

特設ページは**ツアーの全日程を1枚に並べる**形で、行ごとに状態が違う:
   「取り扱いなし」＝**楽天では売っていない**（ここに楽天リンクを貼ってはいけない）
   日付が書いてある＝その日から楽天で一般発売
   「SOLD OUT」＝売り切れ
そして**そのページからしか辿れない公演ページ**（/rtXXXX/）が張ってあることがある。
さだまさしは 12/2・12/3 大阪が特設ページ経由でしか出てこなかった。
"""
import argparse
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_perf_status as P

SITEMAP = 'https://ticket.rakuten.co.jp/static_event-sitemap.xml'
EVENT = re.compile(r'https://ticket\.rakuten\.co\.jp/[^\s"\'<>]*?/rt[0-9a-z]{4,8}/')
# 日程表の1行＝「11月19日(木) 東京 東京国際フォーラム ホールA 17:00 18:00 10月9日(金)」
ROW = re.compile(r'(\d{1,2})月(\d{1,2})日\([日月火水木金土祝・]+\)\s*([^\s]{2,6})\s+(.{2,40}?)\s+'
                 r'(?:\d{1,2}:\d{2}\s+\d{1,2}:\d{2}\s+)?'
                 r'(取り扱いなし|SOLD\s*OUT|\d{1,2}月\d{1,2}日\([日月火水木金土祝・]+\))')


def feature_urls():
    body = P.fetch(SITEMAP)
    return sorted({l for l in re.findall(r'<loc>([^<]+)</loc>', body) if '/features/' in l})


def parse_feature(url, body):
    """特設ページから ①中の公演ページURL ②日程表の行（状態つき）を取り出す。"""
    txt = re.sub(r'\s+', ' ', P.strip_tags(body))
    rows = []
    for m in ROW.finditer(txt):
        rows.append({'md': '%d/%d' % (int(m.group(1)), int(m.group(2))),
                     'pref': m.group(3), 'venue': m.group(4).strip()[:40],
                     'state': re.sub(r'\s+', '', m.group(5))})
    return {'url': url,
            'events': sorted(set(EVENT.findall(body))),
            'rows': rows,
            'handled': sum(1 for r in rows if r['state'] not in ('取り扱いなし',)),
            'notsold': sum(1 for r in rows if r['state'] == '取り扱いなし')}


def _selftest():
    txt = ('11月19日(木) 東京 東京国際フォーラム ホールA 17:00 18:00 10月9日(金) '
           '11月24日(火) 愛知 Niterra日本特殊陶業市民会館フォレストホール 17:00 18:00 取り扱いなし '
           '5月16日(土) 千葉 市川市文化会館 大ホール 16:00 17:00 SOLD OUT')
    ms = list(ROW.finditer(txt))
    assert len(ms) == 3, [m.group(0) for m in ms]
    sts = [re.sub(r'\s+', '', m.group(5)) for m in ms]
    assert sts == ['10月9日(金)', '取り扱いなし', 'SOLDOUT'], sts
    body = ('<a href="https://ticket.rakuten.co.jp/music/rtkbsdt/">申込</a>'
            '<a href="https://ticket.rakuten.co.jp/notice/">お知らせ</a>')
    assert EVENT.findall(body) == ['https://ticket.rakuten.co.jp/music/rtkbsdt/']
    print('selftest OK: 日程表の状態3種 / 公演ページURLだけ拾う')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/rakuten_features.json')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--sleep', type=float, default=0.3)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return 0

    urls = feature_urls()
    sys.stderr.write('特設ページ %d本\n' % len(urls))
    if a.limit:
        urls = urls[:a.limit]

    out, bad = [], []
    for i, u in enumerate(urls, 1):
        try:
            body = P.fetch(u)
        except Exception as ex:
            bad.append({'url': u, 'why': repr(ex)[:70]})
            continue
        r = parse_feature(u, body)
        if r['events'] or r['rows']:
            out.append(r)
        if i % 100 == 0:
            sys.stderr.write('  [%d/%d] 中身のあるページ %d / 読めない %d\n'
                             % (i, len(urls), len(out), len(bad)))
        time.sleep(a.sleep)

    ev = sorted({e for r in out for e in r['events']})
    json.dump({'pages': out, 'errors': bad, 'events': ev},
              open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('特設ページ %d本を見た' % len(urls))
    print('  中身のあるページ %d本 / 読めない %d本' % (len(out), len(bad)))
    print('  そこから辿れる公演ページ %d本' % len(ev))
    print('  日程表の行 %d（うち楽天で扱う %d / 取り扱いなし %d）'
          % (sum(len(r['rows']) for r in out),
             sum(r['handled'] for r in out), sum(r['notsold'] for r in out)))
    print('→ %s' % a.out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
