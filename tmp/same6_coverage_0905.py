# -*- coding: utf-8 -*-
"""「公演は全部載っている」と判定した6件について、**枠の数**まで足りているか見る。

公演が載っていても、e+ にしかない先行枠が抜けていることがある（＝買える枠の取りこぼし）。
公演(県,M/D)ごとに 候補の枠数 と 既存の枠数 を並べて出す。ネットは使わない。
"""
import json, io, re, unicodedata

PREF = ('北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|'
        '山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|'
        '愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄')
PREF_SET = set(PREF.split('|'))
RE_SLOT = re.compile(r'[（(]\s*((?:%s)(?:都|府|県)?)[^）)]*?(\d{1,2})/(\d{1,2})' % PREF)
SAME = {6960: 1477, 6965: 2325, 6976: 4240, 6981: 5784, 6984: 5762, 6987: 5766}


def nz(s):
    return re.sub(r'[\s　・･／/,、]', '', unicodedata.normalize('NFKC', s or '')).lower()


def perf_of(t):
    out = set()
    for m in RE_SLOT.finditer(t.get('type') or ''):
        p = m.group(1)
        if p not in PREF_SET:
            p = re.sub(r'[都府県]$', '', p)
        out.add((p, int(m.group(2)), int(m.group(3))))
    return out


def count(e):
    c = {}
    for t in (e.get('tickets') or []):
        for k in perf_of(t):
            c.setdefault(k, []).append(t.get('type'))
    return c


hh = io.open('index.html', encoding='utf-8', newline='').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}
built = {b['id']: b for b in json.load(io.open('tmp/eplus_batch2_0905.json', encoding='utf-8'))}

out = io.open('tmp/same6_coverage_0905.txt', 'w', encoding='utf-8')
short = 0
for cid, tid in SAME.items():
    b, e = built[cid], db[tid]
    cb, ce = count(b), count(e)
    out.write('■ 既存 id%d %s ／ %s\n' % (tid, e.get('artist'), e.get('name')))
    for k in sorted(cb):
        n_c, n_e = len(cb[k]), len(ce.get(k, []))
        mark = '  ' if n_e >= n_c else '🚨'
        if n_e < n_c:
            short += 1
        out.write('   %s %s 候補%d枠 / 既存%d枠\n' % (mark, k, n_c, n_e))
        if n_e < n_c:
            out.write('        候補: %s\n' % ' ｜ '.join(cb[k]))
            out.write('        既存: %s\n' % ' ｜ '.join(ce.get(k, []) or ['(なし)']))
    out.write('\n')
out.write('枠が足りない公演 %d件\n' % short)
out.close()
print('SHORT=%d' % short)
