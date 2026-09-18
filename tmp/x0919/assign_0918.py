# -*- coding: utf-8 -*-
"""新着プールを下書きジャンル（_genre）どおりに振り分ける（2026-09-18 夜・ユーザー「振り分けて載せて頂戴」）。

やること＝genre を _genre に差し替え、下書き項目（_genre/_extraGenres/_piaSub）を消し、NEW_ORDER から外す。
JSONで読み書きする（**CRLFは自分で戻す**＝[[feedback_index_html_crlf_preserve]]）。
🚨 id は振り直さない・並び順は作り直さない（[[feedback_new_list_order_lock]]）。

## 保留する分（振り分けない＝プールに残す）

- 🚨**TIGETのカテゴリ41「アニメ／ゲーム／声優」** … OSHINAVIは anime / seiyuu / 2.5ji に分かれているので、
  機械では1つに決められない。ユーザーの返事待ち（[[feedback_genres_list]]＝勝手に判断しない）
- 下書きジャンルが画面のジャンル一覧（GENRE_LABEL）に無いもの … 表示できないので出さない

  python tmp/x0919/assign_0918.py            … 調べるだけ
  python tmp/x0919/assign_0918.py --apply
"""
import collections
import datetime
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

blk = re.search(r'GENRE_LABEL\s*=\s*\{(.*?)\n\s*\};', h, re.S).group(1)
LABELS = set(re.findall(r'["\']?([A-Za-z0-9_.]+)["\']?\s*:', blk)) - {'new'}

HOLD_TIGET_ANIME = True

done = collections.Counter()
hold = collections.Counter()
rows, holdrows = [], []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g = e.get('_genre')
    is_tiget = 'tiget.net' in json.dumps(e, ensure_ascii=False)
    if g not in LABELS:
        hold['下書きジャンルが画面に無い(%s)' % g] += 1
        holdrows.append((e['id'], e.get('name'), g, '画面のジャンル一覧に無い'))
        continue
    if HOLD_TIGET_ANIME and is_tiget and g == 'anime':
        hold['TIGETのアニメ/ゲーム/声優（分け方の返事待ち）'] += 1
        holdrows.append((e['id'], e.get('name'), g, 'anime/seiyuu/2.5ji のどれかが決まっていない'))
        continue
    rows.append((e['id'], e.get('name'), g, 'tiget' if is_tiget else 'other'))
    done[g] += 1
    if APPLY:
        e['genre'] = g
        for k in ('_genre', '_extraGenres', '_piaSub'):
            e.pop(k, None)

o = io.open('tmp/x0919/assign_0918.txt', 'w', encoding='utf-8')
o.write('振り分ける %d件 ／ プールに残す %d件\n\n' % (len(rows), len(holdrows)))
for g, n in done.most_common():
    o.write('  %-12s %d\n' % (g, n))
o.write('\n=== プールに残す理由 ===\n')
for k, n in hold.most_common():
    o.write('  %s … %d件\n' % (k, n))
o.close()

if APPLY:
    ids = {r[0] for r in rows}
    io.open('index.html.bak_0918_assign', 'w', encoding='utf-8', newline='').write(h)
    mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
    arr = [int(x) for x in re.findall(r'\d+', mo.group(2)) if int(x) not in ids]
    h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
                r'\g<1>' + '[' + ', '.join(map(str, arr)) + ']', h, count=1)
    m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(
        h2[:m2.start()] + m2.group(1)
        + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
        + m2.group(3) + h2[m2.end():])
    pool = {e['id'] for e in EVENTS if e.get('genre') == 'new'}
    b = open('index.html', 'rb').read()
    print('振り分け %d件 / プール %d / NEW_ORDER %d / 一致=%s / CRCRLF=%d 素のLF=%d'
          % (len(ids), len(pool), len(arr), pool == set(arr),
             b.count(b'\r\r\n'), b.count(b'\n') - b.count(b'\r\n')))
    lg = io.open('logs/assigned_%s.md' % datetime.date.today().isoformat(), 'w', encoding='utf-8')
    lg.write('# 振り分け %s（%d件）\n\n' % (datetime.date.today().isoformat(), len(rows)))
    lg.write('ユーザー「振り分けて載せて頂戴」。ジャンルは売り場のカテゴリを機械で写したもの。\n\n')
    for g, n in done.most_common():
        lg.write('## %s（%d件）\n\n' % (g, n))
        for i, nm, gg, v in rows:
            if gg == g:
                lg.write('- id%d %s ｜%s\n' % (i, nm, v))
        lg.write('\n')
    lg.write('## プールに残した %d件\n\n' % len(holdrows))
    for i, nm, gg, why in holdrows:
        lg.write('- id%d %s ｜下書き=%s ｜%s\n' % (i, nm, gg, why))
    lg.close()
else:
    print('振り分ける %d件 / 残す %d件（--apply で書き込み）' % (len(rows), len(holdrows)))
