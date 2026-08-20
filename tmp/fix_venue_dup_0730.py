"""既存データの2型を直す（2026-07-30 id3229で発覚・ビルダー側は同日恒久修正済み）。
  ①「全国ツアー（同じ会場が表記ゆれで複数）」＝表記ゆれを吸収すると1会場に落ちるもの
  ②dateLabel が「M月D日(x)〜同じM月D日(x)」の冗長な範囲形（実質単日）
①で1会場に落ちた時は venue を単一会場名にし、dateLabel も単日/範囲の正しい形に組み直す。

  python tmp/fix_venue_dup_0730.py            # 差分表示のみ
  python tmp/fix_venue_dup_0730.py --apply
"""
import json
import re
import sys
import unicodedata

sys.path.insert(0, 'tools')
from build_rakuten_entries import venue_key   # 判定を本番ビルダーと同一化

APPLY = '--apply' in sys.argv
JP = r'\d{4}年\d{1,2}月\d{1,2}日\([月火水木金土日祝・]+\)'

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))

out, n1, n2 = [], 0, 0
for e in EVENTS:
    v = e.get('venue') or ''
    dl = e.get('dateLabel') or ''
    tour = re.match(r'^全国ツアー（(.+)）$', v)
    # ①同じ会場が表記ゆれで並んでいる
    if tour:
        parts = [p.strip() for p in tour.group(1).split('／') if p.strip()]
        pick = {}
        order = []
        for p in parts:
            k = venue_key(p)
            if k not in pick:
                pick[k] = p
                order.append(k)
            elif len(p) < len(pick[k]):
                pick[k] = p
        uniq = [pick[k] for k in order]
        if len(uniq) < len(parts):
            n1 += 1
            newv = uniq[0] if len(uniq) == 1 else '全国ツアー（%s）' % '／'.join(uniq)
            out.append('id%s (genre=%s) %s' % (e.get('id'), e.get('genre'), e.get('name')))
            out.append('  ①会場 %d→%d' % (len(parts), len(uniq)))
            out.append('    venue 旧: %s' % v)
            out.append('    venue 新: %s' % newv)
            # dateLabel に旧venue文字列がそのまま入っている形なら差し替える
            newdl = dl.replace(v, newv) if v in dl else dl
            # 1会場に落ちた時は本番ビルダーと同じ「日付 県 会場」形に組み直す（県名を落とさない）
            if len(uniq) == 1 and (e.get('prefecture') or '全国') != '全国':
                dm = re.match(r'^(%s(?:〜%s)?)' % (JP, JP), newdl)
                if dm:
                    newdl = '%s %s %s' % (dm.group(1), e['prefecture'], uniq[0])
            if newdl != dl:
                out.append('    dateLabel 旧: %s' % dl)
                out.append('    dateLabel 新: %s' % newdl)
            e['venue'], e['dateLabel'] = newv, newdl
            v, dl = newv, newdl

    # ②「同じ日〜同じ日」の冗長な範囲形
    mm = re.match(r'^(%s)〜(%s)(.*)$' % (JP, JP), dl)
    if mm and mm.group(1) == mm.group(2):
        n2 += 1
        newdl = (mm.group(1) + mm.group(3)).strip()
        out.append('id%s (genre=%s) %s' % (e.get('id'), e.get('genre'), e.get('name')))
        out.append('  ②単日なのに範囲形')
        out.append('    dateLabel 旧: %s' % dl)
        out.append('    dateLabel 新: %s' % newdl)
        e['dateLabel'] = newdl

out.insert(0, '①会場の表記ゆれ重複 %d件 / ②単日なのに範囲形 %d件' % (n1, n2))

if APPLY and (n1 or n2):
    open('index.html.bak_0730_venuedup', 'w', encoding='utf-8').write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    out.append('=== 適用した (backup: index.html.bak_0730_venuedup) ===')
else:
    out.append('=== 表示のみ。適用するなら --apply ===')

open('tmp/fix_venue_dup_0730.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/fix_venue_dup_0730.txt (venue_dup=%d range_dup=%d apply=%s)' % (n1, n2, APPLY))
