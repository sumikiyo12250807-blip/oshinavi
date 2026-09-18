# -*- coding: utf-8 -*-
"""演劇(02)・スポーツ(03)・イベント(06)の「本当の抜け」から候補リストを作る（2026-09-18 夜）。

make_cands.py と同じ作り。違いは
 ① 複数のジャンルの報告をまとめて読む
 ② **同じ興行の別会場ページ（天皇杯）は、名前が一致しなくても既存エントリに足す**
    ＝報告の「名前の一致も無し」でも、ツアー名の頭が既存と同じなら既存へ寄せる
    （[[feedback_tour_consolidate]]＝ツアー・複数会場は1エントリ）
 ③ 🚫**駐車場だけの売り場は入れない**（[[feedback_oshinavi_concept]]＝推しに会いに行く枠だけ）

  python tmp/x0919/make_cands2.py
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}

PARK = re.compile(r'駐車場|駐輪')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


# 既存エントリを「名前の頭」でも引けるようにする（天皇杯の別会場ページ用）
heads = {}
for e in EV.values():
    k = norm(e.get('artist') or e.get('name'))
    if len(k) >= 8:
        heads.setdefault(k[:14], set()).add(e['id'])

merge, new, skipped = {}, {}, []
for lg in ('02', '03', '06'):
    p = 'tmp/x0919/pia_days_%s_real.txt' % lg
    try:
        txt = io.open(p, encoding='utf-8').read().split('=== 見かけ')[0]
    except FileNotFoundError:
        print('%s が無い＝とばす' % p)
        continue
    for iso, artist, note_tail, note in re.findall(
            r'^(\d{4}-\d{2}-\d{2}) (.*?) \| .*?\n    (.*?)\n    (.*?)$', txt, re.M):
        if PARK.search(artist):
            skipped.append((lg, iso, artist))
            continue
        m = re.search(r'id([\d,]+)', note)
        url = re.search(r'(https?://\S+)', note_tail)
        tgt = None
        if m:
            tgt = int(m.group(1).split(',')[0])
        else:
            k = norm(artist)
            cand = heads.get(k[:14])
            if cand:
                tgt = sorted(cand)[0]
        if tgt:
            d = merge.setdefault(tgt, {'newid': tgt, 'artist': EV[tgt].get('artist') or artist, 'urls': []})
            for u in [(EV[tgt].get('links') or {}).get('pia') or ''] + \
                     [t.get('url') or '' for t in EV[tgt].get('tickets') or []]:
                if u and u not in d['urls']:
                    d['urls'].append(u)
            if url and url.group(1) not in d['urls']:
                d['urls'].append(url.group(1))
        elif url:
            d = new.setdefault(artist, {'newid': 910000 + len(new), 'artist': artist, 'urls': []})
            if url.group(1) not in d['urls']:
                d['urls'].append(url.group(1))

io.open('tmp/x0919/cands2_merge.json', 'w', encoding='utf-8').write(
    json.dumps(list(merge.values()), ensure_ascii=False, indent=1))
io.open('tmp/x0919/cands2_new.json', 'w', encoding='utf-8').write(
    json.dumps(list(new.values()), ensure_ascii=False, indent=1))
print('足し込み %d件（URL計%d）／新規 %d件／🚫駐車場だけで外した %d件'
      % (len(merge), sum(len(v['urls']) for v in merge.values()), len(new), len(skipped)))
for k, v in merge.items():
    print('  足し込み id%d %s（URL%d本）' % (k, v['artist'][:30], len(v['urls'])))
for v in new.values():
    print('  新規 %s | %s' % (v['artist'][:40], v['urls'][0]))
for lg, iso, a in skipped:
    print('  🚫外した lg=%s %s %s' % (lg, iso, a[:60]))
