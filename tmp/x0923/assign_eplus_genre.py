# -*- coding: utf-8 -*-
"""新着プールの e+ エントリを、売り場（e+）の申告どおりに振り分ける。2026-09-23 夜。

出どころ＝個別ページ本文の `/sf/live/<cat>` リンク（= e+ 自身がその公演を置いているカテゴリ）。
  実測で裏が取れた例＝モーニング娘。'26→idol／福田こうへい→enka／レキシ→j-pop／SEASONS→anime-song

🚨[[feedback_genre_pia_asis_and_other]]＝売り場の言う通りに機械で写す。人が最終判断する枠を作らない。
🚨[[feedback_genre_both_when_unclear]]＝カテゴリが2つ以上あるときは 主＝先頭・残り＝extraGenres。
🚨行き先が無いカテゴリは [[feedback_kaigai_is_area]] と ぴあの「民族音楽→yougaku」に合わせて
   「海外の音楽＝yougaku」に寄せる。それでも当たらないものは musicetc（その他＝最後の砦）。

使い方: python tmp/x0923/assign_eplus_genre.py [--apply]
"""
import collections
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
PATH = 'index.html'

# e+のカテゴリ → OSHINAVIジャンル
MAP = {
    'j-pop': 'jpop',
    'rock-indies': 'rock',
    'idol': 'idol',
    'jazz-fusion': 'jazz',
    'enka': 'enka',
    'anime-song': 'anime',
    'hiphop-rap': 'hiphop',
    'visual': 'rock',            # ヴィジュアル系＝ロックの下位
    'voiceactor-live': 'seiyuu',
    'popular-song': 'enka',      # 歌謡曲＝ぴあの「演歌・邦楽→enka」に合わせる
    'reggae': 'yougaku',         # 海外の音楽（ぴあの「民族音楽→yougaku」と同じ扱い）
    'bossanova-latin': 'yougaku',
    'world-music': 'yougaku',
    'classical': 'classic',
    'classic': 'classic',
    'kayokyoku': 'enka',
    'club-dj': 'club',
    'vocaloid': 'vocaloid',
    'kpop': 'kpop',
    'k-pop': 'kpop',
    'asian-pops': 'yougaku',
    'western-music': 'yougaku',
    'soul-rb': 'yougaku',
    'punk': 'rock',
    'metal': 'rock',
}

raw = {}
for p in ('tmp/x0923/eplus_genre_raw.json', 'tmp/x0923/eplus_genre_retry.json', 'tmp/x0923/eplus_genre_retry2.json'):
    try:
        d = json.load(io.open(p, encoding='utf-8'))
    except Exception:
        continue
    for k, v in d.items():
        if v.get('cats'):
            raw[str(k)] = v['cats']

text = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)

log, unknown, skipped = [], collections.Counter(), []
n = 0
cnt = collections.Counter()
for ev in events:
    if ev.get('genre') != 'new':
        continue
    cats = raw.get(str(ev['id']))
    if not cats:
        continue                      # 取れなかった＝触らない
    gs, bad = [], []
    for c in cats:
        g = MAP.get(c)
        if g:
            if g not in gs:
                gs.append(g)
        else:
            bad.append(c)
            unknown[c] += 1
    if bad:                            # 知らないカテゴリが混ざる件は触らず報告
        skipped.append((ev['id'], ev.get('name') or ev.get('artist') or '', cats))
        continue
    ev['genre'] = gs[0]
    if len(gs) > 1:
        ev['extraGenres'] = gs[1:]
    n += 1
    cnt[gs[0]] += 1
    url = (ev.get('links') or {}).get('eplus') or ''
    log.append('%s\t%s\t%s\t%s\t%s' % (ev['id'], gs[0], ','.join(cats),
                                       (ev.get('name') or ev.get('artist') or ''), url))

pool = set(e['id'] for e in events if e.get('genre') == 'new')
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', text)
arr = [int(x) for x in mo.group(1).split(',') if x.strip()]
kept = [i for i in arr if i in pool]

rep = io.open('tmp/x0923/assign_eplus_genre.txt', 'w', encoding='utf-8')
rep.write('e+ 振り分け %d件（売り場のカテゴリをそのまま写した）\n' % n)
rep.write('新着プール 残り %d件 ／ NEW_ORDER %d→%d\n\n' % (len(pool), len(arr), len(kept)))
rep.write('== ジャンル別 ==\n')
for k, c in cnt.most_common():
    rep.write('  %-12s %4d\n' % (k, c))
if unknown:
    rep.write('\n== 対応表に無いカテゴリ（触らなかった）==\n')
    for k, c in unknown.most_common():
        rep.write('  %-20s %4d\n' % (k, c))
    for i, nm, cs in skipped:
        rep.write('  id=%-6s %-40s %s\n' % (i, nm[:40], ','.join(cs)))
rep.write('\n== 明細（id / ジャンル / e+のカテゴリ / 公演名 / URL）==\n')
rep.write('\n'.join(log) + '\n')
rep.close()

sys.stdout.write('assigned=%d pool=%d NEW_ORDER=%d->%d unknown_cats=%d skipped=%d\n'
                 % (n, len(pool), len(arr), len(kept), len(unknown), len(skipped)))
sys.stdout.write('by_genre=%s\n' % dict(cnt.most_common()))
sys.stdout.write('report: tmp/x0923/assign_eplus_genre.txt\n')

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
