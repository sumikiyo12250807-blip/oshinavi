# -*- coding: utf-8 -*-
"""仕分けで「名前が同じ既存が複数」になった組み上がりの行き先の案を出す（読むだけ・2026-09-15）。
考え方（9/13〜9/14 に1件ずつ決めた型をそのまま機械で並べるだけ・書き込みはしない）:
  A＝既存の中に「その公演日が会期（初日〜千秋楽）の中に入るエントリ」が1つだけ → そこへ畳む案
  B＝どの既存の会期にも入らず、既存が全部「1会場のエントリ」 → 同じ形で新規の案（伊波杏樹・鳥肌実の形）
  C＝それ以外（会期に入るエントリが2つ以上／ツアーのエントリがあるのに会期の外）→ 人が見る
会期の初日は dateLabel の最初の日付、千秋楽は date。
使い方: python tmp/multi_match_plan_0915.py
出力: tmp/multi_match_plan_ps0915.txt
"""
import datetime
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_presale_0915.json', encoding='utf-8'))}
src = io.open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
lines = [l for l in io.open('tmp/split_built_ps0915.txt', encoding='utf-8').read().splitlines() if l.startswith('👀複数')]


def first_day(e):
    m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or '')
    return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))) if m else (e.get('date') or '')


def show_days(b):
    """組み上がりの枠の（…公演）から公演日を拾う。R9年＝2027。"""
    out = []
    for t in b.get('tickets') or []:
        mm = re.search(r'（([^（）]*)公演）', t.get('type') or '')
        if not mm:
            continue
        y = 2026
        for r9, mo, dd in re.findall(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', mm.group(1)):
            if r9:
                y = 2027
            out.append('%04d-%02d-%02d' % (y, int(mo), int(dd)))
    return sorted(set(out))


def one_venue(e):
    v = e.get('venue') or ''
    return not v.startswith('全国ツアー') and '／' not in v and '・' not in (e.get('prefecture') or '')


res = {'A': [], 'B': [], 'C': []}
for l in lines:
    nid = int(re.search(r'new(\d+)', l).group(1))
    ids = [int(x) for x in re.findall(r'\d+', l.split('→')[1].split(']')[0])]
    b = built[nid]
    days = show_days(b)
    inside = [i for i in ids if days and all(first_day(ev[i]) <= d <= (ev[i].get('date') or '') for d in days)]
    if len(inside) == 1:
        k, why = 'A', '→ id%s に畳む（会期 %s〜%s の中）' % (inside[0], first_day(ev[inside[0]]), ev[inside[0]].get('date'))
    elif not inside and all(one_venue(ev[i]) for i in ids):
        k, why = 'B', '→ 新規（既存 %d件とも1会場のエントリ）' % len(ids)
    else:
        k, why = 'C', '→ 人が見る（会期に入る %s）' % inside
    res[k].append(nid)
    desc = ' ／ '.join('id%s %s〜%s %s' % (i, first_day(ev[i]), ev[i].get('date'), (ev[i].get('venue') or '')[:24]) for i in ids)
    res.setdefault('lines', []).append('%s new%-6s %s 公演%s %s\n      既存: %s' % (k, nid, (b.get('artist') or '')[:20], days, why, desc))

out = ['複数一致 %d件 ＝ A 畳む %d ／ B 新規 %d ／ C 人が見る %d' % (len(lines), len(res['A']), len(res['B']), len(res['C']))]
out += res['lines']
out += ['', 'A=' + ','.join(map(str, res['A'])), 'B=' + ','.join(map(str, res['B'])), 'C=' + ','.join(map(str, res['C']))]
io.open('tmp/multi_match_plan_ps0915.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(out[0])
