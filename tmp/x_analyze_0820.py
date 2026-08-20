# -*- coding: utf-8 -*-
"""X投稿の実測台帳(tmp/x_metrics.csv)を集計する。
数字はすべて memory (feedback_x_ctr_observations / project_x_post_analytics) に
ユーザー報告として残っている実測値のみ。推測値は入れていない。"""
import csv, io, sys, statistics as st
sys.stdout.reconfigure(encoding='utf-8')

rows = list(csv.DictReader(io.open('tmp/x_metrics.csv', encoding='utf-8')))


def num(r, k):
    v = (r.get(k) or '').strip()
    return int(v) if v.isdigit() else None


def agg(sel, label):
    imp = [num(r, 'impressions') for r in sel]
    imp = [x for x in imp if x is not None]
    eng = [(num(r, 'impressions'), num(r, 'engagements')) for r in sel]
    eng = [(i, e) for i, e in eng if i and e is not None]
    if not imp:
        print("%-28s n=0" % label)
        return
    line = "%-28s n=%-3d インプ 中央値%5.0f 平均%6.0f 最大%5d" % (
        label, len(imp), st.median(imp), sum(imp) / len(imp), max(imp))
    if eng:
        ti, te = sum(i for i, _ in eng), sum(e for _, e in eng)
        line += " | エンゲージ率 %.2f%% (n=%d)" % (100.0 * te / ti, len(eng))
    print(line)


print("=== 台帳 %d行 ===" % len(rows))
print()
print("【リンクの置き方（body=本文にURL / reply=セルフリプ / none=URL無し）】")
for k in ('body', 'reply', 'none'):
    agg([r for r in rows if r['body_url'] == k], k)
print()
print("【ジャンル別（n>=2のみ）】")
gs = {}
for r in rows:
    gs.setdefault(r['genre'], []).append(r)
for g, sel in sorted(gs.items(), key=lambda kv: -len(kv[1])):
    if g and len(sel) >= 2:
        agg(sel, g)
print()
print("【投稿日別】")
ds = {}
for r in rows:
    ds.setdefault(r['posted'], []).append(r)
for d, sel in sorted(ds.items()):
    agg(sel, d)
print()
print("【エンゲージ率トップ10（インプ30以上）】")
tbl = []
for r in rows:
    i, e = num(r, 'impressions'), num(r, 'engagements')
    if i and e is not None and i >= 30:
        tbl.append((100.0 * e / i, i, e, r['subject'], r['body_url']))
for rate, i, e, s, b in sorted(tbl, reverse=True)[:10]:
    print("  %5.2f%%  %5d imp / %3d eng  %-34s [%s]" % (rate, i, e, s[:34], b))
