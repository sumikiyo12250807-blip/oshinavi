# -*- coding: utf-8 -*-
"""新着プール(genre:"new")を正式ジャンルへ振り分ける。
既定は _genre/_extraGenres をそのまま適用（[[project_vendor_genre_autoassign]]＝自分で再分類しない）。
ぴあがカテゴリを返さず名前fallbackになった7件だけ、裏取り結果で上書き（主+extraGenresの両方入れ）。
--apply を付けるまで書き換えない。CRLFは維持する。
"""
import io
import json
import re
import shutil
import sys

APPLY = '--apply' in sys.argv
P = 'index.html'
BK = 'index.html.bak_0813_assign'

# ぴあカテゴリが取れず名前fallbackだった7件＝人が決める枠。WebSearchで裏取り済み。
OVERRIDE = {
    4130: ('jpop', [],       'ユーザー確定'),
    4142: ('kpop', ['rock'], 'FNC所属の日韓5人組バンド(2023日韓同時デビュー)'),
    # 4144は同じアーティストが id4133(Age Factory／ENTH／Paledusk)にぴあカテゴリ付きで在り、
    # そこでは「音楽/J-POP・ROCK」＝jpop。ぴあの実カテゴリの証拠があるので自分の音楽知識で
    # rockに倒さず jpop主に揃える（[[project_vendor_genre_autoassign]]）。rockは追加で持たせる。
    4144: ('jpop', ['rock'], '奈良の3ピース オルタナロック／id4133のぴあカテゴリ(J-POP・ROCK)に合わせた'),
    4152: ('rock', ['jpop'], 'ヴィジュアル系ロック・結成15周年'),
    4159: ('idol', ['jpop'], 'エイベックス/iDOL Streetの4人組女性アイドル(2015結成)'),
    4163: ('idol', ['jpop'], 'アソビシステム所属7人組アイドル(2025結成)の生誕祭'),
    4167: ('rock', ['jpop'], 'Hi-STANDARD横山健の4ピース パンクロック'),
}

raw = open(P, 'rb').read()
if raw.count(b'\r\n') != raw.count(b'\n'):
    raise SystemExit('元ファイルがCRLF統一でない')
text = raw.decode('utf-8').replace('\r\n', '\n')

m = re.search(r'(const EVENTS\s*=\s*)(\[.*?\])(;)', text, re.S)
EVENTS = json.loads(m.group(2))

rows, changed = [], 0
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g = e.get('_genre')
    extra = list(e.get('_extraGenres') or [])
    why = 'ぴあカテゴリ(%s)' % (e.get('_piaSub') or '')
    if e['id'] in OVERRIDE:
        g, extra, why = OVERRIDE[e['id']]
        why = '⚠️名前fallback→裏取り: ' + why
    if not g:
        rows.append((e['id'], e.get('name'), '🚨下書き無し', '', why))
        continue
    rows.append((e['id'], e.get('name'), g, '+'.join(extra), why))
    if APPLY:
        e['genre'] = g
        if extra:
            e['extraGenres'] = extra
        else:
            e.pop('extraGenres', None)
        for k in ('_genre', '_extraGenres', '_piaSub'):
            e.pop(k, None)
        changed += 1

from collections import Counter
print('対象 %d件' % len(rows))
for i, name, g, ex, why in rows:
    print('  %-5s %-34s → %-8s %-6s %s' % (i, (name or '')[:34], g, ('+' + ex) if ex else '', why[:44]))
print('\n内訳:', dict(Counter(r[2] for r in rows)))

if not APPLY:
    print('\n（案のみ。適用するなら --apply）')
    sys.exit(0)

out = (text[:m.start(2)] + json.dumps(EVENTS, ensure_ascii=False, indent=2) + text[m.end(2):]).replace('\n', '\r\n')
shutil.copyfile(P, BK)
open(P, 'wb').write(out.encode('utf-8'))
r = open(P, 'rb').read()
print('\n=== %d件 適用 / CRLF %d = LF %d (backup: %s) ===' % (changed, r.count(b'\r\n'), r.count(b'\n'), BK))
if r.count(b'\r\n') != r.count(b'\n'):
    raise SystemExit('🚨 CRLFが壊れた')
