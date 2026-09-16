# -*- coding: utf-8 -*-
"""投稿のCTAの着地先（?q= と ?genre=）がOSHINAVIで本当に当たるかを手元のindexで数える（2026-09-16 夜）。

X投稿の誘導先は oshinavi.jp なので、着地したページに何も出ないのがいちばん損。
`?q=` は検索語、`?genre=&status=urgent` はタブと絞り込み＝index.html の EVENTS に当てて件数を出す。
判定は「0件なら文面を直す」。件数は投稿に書かない（feedback_x_no_counts_oshi_first）。
使い方: python tmp/x0917/check_cta.py
"""
import glob
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

src = io.open('index.html', encoding='utf-8').read()
events = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def norm(s):
    return re.sub(r'[\s　・]', '', unicodedata.normalize('NFKC', s or '')).lower()


out = []
for path in sorted(glob.glob('tmp/x0917/post*.txt')):
    body = io.open(path, encoding='utf-8').read()
    m = re.search(r'oshinavi\.jp/\?(\S+)', body)
    if not m:
        out.append('%s CTAのURLが無い' % path)
        continue
    q = m.group(1)
    if q.startswith('q='):
        word = norm(q[2:])
        hit = [e for e in events
               if word in norm((e.get('artist') or '') + (e.get('name') or ''))]
        out.append('%s  ?q=%s → %d件%s' % (
            path, q[2:], len(hit), '' if hit else '  🚨0件＝文面を直す'))
        for e in hit[:3]:
            out.append('        id%-6d %s' % (e['id'], (e.get('artist') or e.get('name'))[:40]))
    else:
        g = re.search(r'genre=([^&]+)', q)
        g = g.group(1) if g else ''
        hit = [e for e in events
               if e.get('genre') == g or g in (e.get('extraGenres') or [])]
        out.append('%s  ?genre=%s → %d件%s' % (
            path, g, len(hit), '' if hit else '  🚨0件＝文面を直す'))

io.open('tmp/x0917/check_cta.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/x0917/check_cta.txt (%d lines)' % len(out))
