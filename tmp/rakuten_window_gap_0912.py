# -*- coding: utf-8 -*-
"""楽天の発売前ハーベスト（tmp/rakuten_presale.json）の「発売前の枠」が、登録済みエントリに入っているかを枠の単位で見る（読むだけ）。
ページが登録済みでも、発売前の枠だけ抜けている型がある（2026-09-10 理芽・KOKO・春猿火）。
突き合わせ＝同じ楽天ページ（rtXXXX）を持つエントリの tickets に、その枠の発売日（startDate）か
「M/D HH:MM発売」の表記があるか。
使い方: python tmp/rakuten_window_gap_0912.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('tmp/rakuten_presale.json', encoding='utf-8-sig'))
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def code_of(u):
    # 楽天リンクはDeep Link形式（中のURLが %2F で符号化されている）＝戻してから探す
    import urllib.parse
    u = urllib.parse.unquote(urllib.parse.unquote(u or ''))
    m = re.search(r'/(rt[0-9a-z]+)/?', u, re.I)
    return m.group(1).lower() if m else None


by_code = {}
for e in ev:
    us = list((e.get('links') or {}).values()) + [t.get('url') for t in e.get('tickets') or []]
    for u in us:
        c = code_of(u if isinstance(u, str) else '')
        if c:
            by_code.setdefault(c, {})[e['id']] = e

miss, ok = [], 0
for r in d.get('presale') or []:
    c = code_of(r.get('url'))
    ents = list((by_code.get(c) or {}).values())
    for w in r.get('presale_windows') or []:
        m = re.match(r'(\d{4})/(\d{2})/(\d{2})\S*\s+(\d{1,2}:\d{2})', w.get('timming') or '')
        if not m:
            miss.append((r['name'][:40], w.get('type'), w.get('timming'), '発売日が読めない', [x['id'] for x in ents]))
            continue
        iso = '%s-%s-%s' % m.group(1, 2, 3)
        md = '%d/%d' % (int(m.group(2)), int(m.group(3)))
        hit = False
        for e in ents:
            for t in e.get('tickets') or []:
                if t.get('startDate') == iso or (md + ' ' in (t.get('type') or '') and '発売' in (t.get('type') or '')):
                    hit = True
        if hit:
            ok += 1
        else:
            miss.append((r['name'][:40], w.get('type'), w.get('timming'), iso, [x['id'] for x in ents]))

print('発売前の枠 照合できた %d ／ 登録に見当たらない %d' % (ok, len(miss)))
for name, ty, tm, iso, ids in miss:
    print('  %s | %s | %s | 発売日%s | 登録id=%s' % (name, ty, tm, iso, ids))
