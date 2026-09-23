# -*- coding: utf-8 -*-
"""新着プールのうち、**売り場がジャンルを言っている分**（_genre を持つ324件）を振り分ける。
2026-09-23 夜。ユーザー「新着ふりわけOKよ」。

🚨[[feedback_genre_pia_asis_and_other]]＝ジャンルは売り場の言う通りに機械で写す。
   人が最終判断する枠を作らない＝ここでは **_genre をそのまま genre に移すだけ**。推測は一切しない。
🚨[[feedback_nonpia_user_eyes_until_gate]]＝ぴあ以外は「振り分けだけユーザー確認後」＝今回のOKがそれ。
🚨[[feedback_new_order_array]]＝振り分けた分は NEW_ORDER からも外す。
🚨[[feedback_index_html_crlf_preserve]]＝CRLFのまま書き戻す（指紋が合わなければ書かない）。

対象＝TIGET263 / ZAIKO37 / FANY22 / 楽天2（_genre はビルダーが売り場の申告から決めた値）
対象外＝e+272件（ビルダーが _genre を付けていない＝売り場の申告が取れていない）→ そのままプールに残す

使い方: python tmp/x0923/assign_newpool_0923pm.py [--apply]
"""
import collections
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

text = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)


def vendor(e):
    links = e.get('links') or {}
    for k in ('tiget', 'zaiko', 'fany', 'eplus', 'rakuten', 'lawson', 'pia'):
        if links.get(k):
            return k
    return '(no-link)'


# 🚨対象は「この夜のドライランで数えた324件」に固定する。
#    あとから投入する新着（ユーザーがまだ見ていない分）を巻き込まないため。
#    --fix-list を付けると、いまの index.html から対象を数え直して一覧を作る（初回だけ）。
LIST = 'tmp/x0923/assign_newpool_0923pm_ids.txt'
if '--fix-list' in sys.argv:
    ids0 = [str(e['id']) for e in events if e.get('genre') == 'new' and e.get('_genre')]
    io.open(LIST, 'w', encoding='utf-8').write(','.join(ids0))
    sys.stdout.write('fixed list: %d ids -> %s\n' % (len(ids0), LIST))
TARGET = set(int(x) for x in io.open(LIST, encoding='utf-8').read().split(',') if x.strip())

log = []
n = 0
cnt = collections.Counter()
by_vendor = collections.Counter()
for ev in events:
    if ev.get('genre') != 'new':
        continue
    if ev['id'] not in TARGET:
        continue                      # この夜の対象外（あとから入った新着）
    g = ev.get('_genre')
    if not g:
        continue                      # e+＝売り場の申告が無い。触らない
    src = ev.pop('_srcgenre', None)
    ev.pop('_genre', None)
    ev['genre'] = g
    ex = ev.pop('_extraGenres', None)
    if ex:
        ev['extraGenres'] = ex
    n += 1
    cnt[g] += 1
    v = vendor(ev)
    by_vendor[v] += 1
    url = (ev.get('links') or {}).get(v) or ''
    log.append('%s\t%s\t%s\t%s\t%s' % (ev['id'], g, src or '', (ev.get('name') or ev.get('artist') or ''), url))

# NEW_ORDER から外す
pool = set(e['id'] for e in events if e.get('genre') == 'new')
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', text)
arr = [int(x) for x in mo.group(1).split(',') if x.strip()]
kept = [i for i in arr if i in pool]

rep = io.open('tmp/x0923/assign_newpool_0923pm.txt', 'w', encoding='utf-8')
rep.write('振り分け %d件（売り場の申告どおり・推測ゼロ）\n' % n)
rep.write('新着プール %d→%d件 ／ NEW_ORDER %d→%d\n\n' % (len(pool) + n, len(pool), len(arr), len(kept)))
rep.write('== 売り場別 ==\n')
for k, c in by_vendor.most_common():
    rep.write('  %-8s %4d\n' % (k, c))
rep.write('\n== ジャンル別 ==\n')
for k, c in cnt.most_common():
    rep.write('  %-12s %4d\n' % (k, c))
rep.write('\n== 明細（id / ジャンル / 売り場の申告 / 公演名 / URL）==\n')
rep.write('\n'.join(log))
rep.write('\n')
rep.close()

sys.stdout.write('assigned=%d pool=%d NEW_ORDER=%d->%d\n' % (n, len(pool), len(arr), len(kept)))
sys.stdout.write('by_vendor=%s\n' % dict(by_vendor))
sys.stdout.write('by_genre=%s\n' % dict(cnt.most_common()))
sys.stdout.write('report: tmp/x0923/assign_newpool_0923pm.txt\n')

if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)

body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
newtext = text[:start] + body + text[end:]
newtext = re.sub(r'const NEW_ORDER = \[[^\]]*\];',
                 'const NEW_ORDER = [%s];' % ', '.join(str(i) for i in kept), newtext, count=1)
data = newtext.encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open(PATH, 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
