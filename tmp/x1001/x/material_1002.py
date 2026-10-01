# -*- coding: utf-8 -*-
"""10/2(金)発売のX投稿の「まとめ枠」素材（x0928/x/material_0929.py の日付違い＋行のまとめを機械で済ませる版）。
・枠の県は券種の「（県 …公演）」から取る（エントリの県ではない）
・先行＝券種に 先行/抽選/プレリザーブ/プレオーダー/リザーブ を含む
・1行＝（時刻・名前・先行かどうか）が同じもの。県は出た順に「・」でつなぐ（X_SCRIPT 4番）
・主役（stars.json の id）はまとめから外す
出力: tmp/x1001/x/material.md
"""
import io, json, re, sys
from collections import defaultdict, OrderedDict
sys.path.insert(0, 'tmp/x1001/x')
import ev
TOM, D2, D3 = '2026-10-02', '2026-10-03', '2026-10-04'
STAR_IDS = set(json.load(io.open('tmp/x1001/x/stars.json', encoding='utf-8')))
PRE = re.compile(r'先行|抽選|プレリザーブ|プレオーダー|リザーブ|プリセール|プレセール|先着.*会員|会員')


def live(e):
    return [t for t in (e.get('tickets') or []) if not t.get('soldout') and not t.get('saleEnded')]


def hhmm(ty):
    m = re.search(r'(\d{1,2}):(\d{2})\s*発売', ty or '')
    return '%02d:%s' % (int(m.group(1)), m.group(2)) if m else '(時刻なし)'


def pref(ty, e):
    ms = re.findall(r'（([^（）\s]+?) [^（）]*公演', ty or '')
    p = ms[-1] if ms else ('全国' if ('（配信）' in (ty or '') or (ty or '').startswith('配信')) else (e.get('prefecture') or ''))
    if re.match(r'^[\d/〜~・]+$', p or ''):
        p = '全国' if (ty or '').startswith('配信') else (e.get('prefecture') or '')
    p = '・'.join(q[:-1] if q.endswith(('都', '府', '県')) and q != '京都' else q for q in p.split('・'))
    return '配信' if p == '全国' else p


def label(e):
    a = (e.get('artist') or '').strip()
    if not a or '決まり次第' in a or a in ('若手多数組',):
        return e.get('name')
    return a


def rough(n):
    if n < 5:
        return '数件'
    if n < 10:
        return '10件近く'
    base = (n // 10) * 10
    return '%d件以上' % base if n - base <= 4 else '%d件近く' % (base + 10)


def collect(day, skip_star):
    rows = []
    for e in ev.E:
        if e.get('genre') == 'new' or (skip_star and e['id'] in STAR_IDS):
            continue
        for t in live(e):
            if t.get('startDate') == day:
                rows.append((hhmm(t.get('type')), label(e), bool(PRE.search(t.get('type') or '')), pref(t.get('type'), e), e, t))
    return rows


def group(rows):
    g = OrderedDict()
    for tm, name, pre, pf, e, t in sorted(rows, key=lambda r: r[0]):
        k = (tm, name, pre)
        g.setdefault(k, {'prefs': [], 'ids': [], 'venues': [], 'types': []})
        if pf not in g[k]['prefs']:
            g[k]['prefs'].append(pf)
        if e['id'] not in g[k]['ids']:
            g[k]['ids'].append(e['id']); g[k]['venues'].append((e.get('venue') or '')[:30])
        g[k]['types'].append(t.get('type'))
    return g


def line(k, v):
    tm, name, pre = k
    ps = [p for p in v['prefs'] if p != '配信'] + [p for p in v['prefs'] if p == '配信']
    name = re.sub(r'^(\S+) ' + chr(92) + '1 ', lambda m: m.group(1) + ' ', name)   # 「甘い暴力 甘い暴力 …」の二重を1回に
    name = re.sub(r'\(お見立て費.*$', '', name)            # 料金を名前に含む登録は料金の部分を落とす
    pj = '・'.join(p for p in ps if p)
    return '%s %s%s%s' % (tm, name, ('／' + pj) if pj else '', '（先行）' if pre else '')


out = io.open('tmp/x1001/x/material.md', 'w', encoding='utf-8')
out.write('# 10/2(金)発売 X投稿の素材（ジャンル別まとめ枠）\n\n')
out.write('🚨1投稿＝1ジャンル。行は機械でまとめ済み（そのまま使う）。主役はここから外してある。\n\n')
tom = collect(TOM, True)
byg = defaultdict(list)
for r in tom:
    byg[r[4].get('genre')].append(r)
summary = {}
for gname in sorted(byg, key=lambda k: -len({r[4]['id'] for r in byg[k]})):
    g = group(byg[gname])
    nent = len({r[4]['id'] for r in byg[gname]})
    summary[gname] = (nent, len(g))
    out.write('## %s（エントリ%d件・行%d）\n' % (gname, nent, len(g)))
    for k, v in g.items():
        out.write('- %s    ｜id%s｜%s｜%s\n' % (line(k, v), ','.join(map(str, v['ids'])), ' / '.join(v['venues'][:3]), v['types'][0]))
    out.write('\n')
out.write('\n# 2〜3日後の発売（予告：1投稿に5件くらい＝箱の大きい順・並びは時刻順）\n\n')
for d in (D2, D3):
    rows = collect(d, False)
    byg2 = defaultdict(list)
    for r in rows:
        byg2[r[4].get('genre')].append(r)
    out.write('## %s\n' % d)
    for gname in sorted(byg2):
        g = group(byg2[gname])
        out.write('### %s（行%d → 5行載せたら残り「%s」）\n' % (gname, len(g), rough(max(0, len(g) - 5))))
        for k, v in g.items():
            out.write('- %s    ｜id%s｜%s\n' % (line(k, v), ','.join(map(str, v['ids'])), ' / '.join(v['venues'][:3])))
    out.write('\n')
out.close()
for k, v in summary.items():
    print(k, 'エントリ', v[0], '行', v[1])
