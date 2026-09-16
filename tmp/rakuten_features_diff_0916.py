# -*- coding: utf-8 -*-
"""楽天の特設ページから辿れる公演ページのうち、①うちに未登録 ②発売前ハーベスト（post-sitemap26/27）でも
見ていない ものだけを取り出し、rakuten_harvest のパーサで読んで「これからの公演があるか」を分ける（読むだけ）。
9/10 の実測では、特設ページからしか辿れない公演は全部が過去公演だった＝値打ちは「新しいツアーが特設ページ先行で出た時」。
使い方: python tmp/rakuten_features_diff_0916.py
出力: tmp/rakuten_features_diff_0916.txt ／ tmp/rakuten_features_new_0916.json（これからの公演がある分＝build_rakuten_entries に渡せる形）
"""
import datetime
import io
import json
import re
import sys
import time
import urllib.parse

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R  # noqa: E402

TODAY = datetime.date.today().isoformat()
feat = json.load(io.open('tmp/rakuten_features.json', encoding='utf-8'))
seen = json.load(io.open('tmp/rakuten_presale.json', encoding='utf-8'))
src = urllib.parse.unquote(io.open('index.html', encoding='utf-8').read())


def code(u):
    m = re.search(r'/(rt[0-9a-z]+)/?$', u or '')
    return m.group(1) if m else ''


seen_codes = {code(r.get('url')) for k in ('presale', 'onsale', 'soldout', 'past', 'error')
              for r in seen.get(k) or [] if isinstance(r, dict)}
links = sorted({u for p in feat['pages'] for u in p.get('events') or []})
todo = [u for u in links if code(u) and ('/%s/' % code(u)) not in src and code(u) not in seen_codes]
print('特設ページから辿れる公演 %d本 → 未登録かつ発売前ハーベストで見ていない %d本' % (len(links), len(todo)))

out, fut = [], []
for i, u in enumerate(todo, 1):
    try:
        rec = R.parse_page(u, R.fetch(u))
    except Exception as ex:
        out.append('❌ 読めない %s … %s' % (u, str(ex)[:50]))
        continue
    if not rec:
        out.append('⏭ 解析できない形式 %s' % u)
        continue
    days = sorted(p.get('date') or '' for p in rec.get('perfs') or [])
    last = days[-1] if days else ''
    if last and last >= TODAY:
        fut.append(rec)
        out.append('🎯 これからの公演あり %s〜%s | %s | %s' % (days[0], last, (rec.get('name') or '')[:40], u))
    else:
        out.append('   過去 %s | %s' % (last, (rec.get('name') or '')[:40]))
    time.sleep(1.2)
io.open('tmp/rakuten_features_diff_0916.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
json.dump(fut, io.open('tmp/rakuten_features_new_0916.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('これからの公演がある %d本 / 過去・読めない %d本 → tmp/rakuten_features_diff_0916.txt' % (len(fut), len(out) - len(fut)))
for l in out:
    if l.startswith('🎯'):
        print(l)
