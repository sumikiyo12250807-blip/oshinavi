# -*- coding: utf-8 -*-
"""X投稿の「書き方の形」が数字に効いているかを測る（2026-09-16 新設・ユーザー依頼
「時間と文字数以外にも、ささる文章や伸びる書き方を考えて試してほしい」）。

判定の手すりは tools/x_analyze.py と同じものを import して使う＝
  ・投稿から2日以上たったものだけ数える
  ・母数15本未満の群では勝ち負けを言わない
  ・いちばん跳ねた1本を外した検算を必ず並べる（両方が同じ向きの時だけ結論にする）
形の判定には全文が要るので、全文が手元にある投稿だけを対象にする。

使い方: python tools/x_features.py tmp/x_content_0916.csv [--out tmp/x_features_0916.md]
"""
from __future__ import division

import argparse
import io
import os
import re
import sys
from datetime import timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import x_analyze as xa  # noqa: E402

sys.stdout.reconfigure(encoding='utf-8')

YOU = re.compile(u'あなた')
Q = re.compile(u'[？?]')
KASHIRA = re.compile(u'かしら|でしょう|わよね')
NEXT_POST = re.compile(u'このあとの投稿|次の投稿|フォローして待って')
ACCESS = re.compile(u'行き方|最寄り|駅から|乗り換え|所要|アクセス|までの道')
PLAN = re.compile(u'祝日|平日|土曜|日曜|連休|仕事帰り|学校帰り|有給|休みをやりくり')
SENSE = re.compile(u'声|音|光|匂い|風|息|指|足音|拍手|静けさ|ざわめき')
SLOTBLOCK = re.compile(u'^【.*発売】', re.M)
EMOJI = re.compile(u'[\U0001F000-\U0001FAFF☀-➿]')
SENT = re.compile(u'[。！？]')


def feats(r):
    b = r['full_text']
    lines = [ln for ln in b.splitlines()]
    body_lines = [ln for ln in lines if ln.strip()]
    nsent = max(1, len(SENT.findall(b)))
    return {
        'you': len(YOU.findall(b)),
        'q_end': bool(Q.search(u'\n'.join(lines[-6:])) or KASHIRA.search(u'\n'.join(lines[-6:]))),
        'q_any': len(Q.findall(b)),
        'next_post': bool(NEXT_POST.search(b)),
        'access': bool(ACCESS.search(b)),
        'plan': bool(PLAN.search(b)),
        'sense': len(SENSE.findall(b)),
        'slotblock': bool(SLOTBLOCK.search(b)),
        'emoji': len(EMOJI.findall(b)),
        'para': sum(1 for i, ln in enumerate(lines) if not ln.strip()),
        'linelen': len(b) / max(1, len(body_lines)),
        'sentlen': len(b) / nsent,
        'tags': b.count(u'#'),
    }


def compare2(name, groups, min_n, out):
    """x_analyze.compare と同じ形＋**クリックの外れ値検算**の列を足す。
    インプだけ外れ値を外しても「1本あたりclk」は跳ねた1本で動く＝形の話では効きが逆に見える。
    """
    out.append(u'')
    out.append(u'### %s' % name)
    thin = [label for label, g in groups if len(g) < min_n]
    out.append(u'| 群 | 本数 | 中央インプ | CTR | 1本あたりclk | 外れ値除き中央インプ | 外れ値除き1本あたりclk |')
    out.append(u'|---|---|---|---|---|---|---|')
    for label, g in groups:
        if not g:
            continue
        s = xa.stats(g)
        si = xa.stats(xa.drop_top(g, 'imp'))
        sc = xa.stats(xa.drop_top(g, 'clicks'))
        out.append(u'| %s | %d | %s | %.2f%% | %.2f | %s | %.2f |' % (
            label, s['n'], xa.fmt(s['imp_median']), s['ctr'] * 100,
            s['clicks_per_post'], xa.fmt(si['imp_median']), sc['clicks_per_post']))
    if thin:
        out.append(u'')
        out.append(u'🚨**まだ判定しない**（母数%d本未満）＝ %s' % (min_n, u'／'.join(thin)))
    return out


xa.compare = compare2


def bucket(rows, label_fn, order):
    g = {k: [] for k in order}
    for r in rows:
        k = label_fn(r)
        if k in g:
            g[k].append(r)
    return [(k, g[k]) for k in order]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv')
    ap.add_argument('--min-age', type=int, default=2)
    ap.add_argument('--min-n', type=int, default=15)
    ap.add_argument('--kind', help=u'型で絞る（まとめ／主役）＝型と字数の交絡を外すため')
    ap.add_argument('--min-chars', type=int, default=0)
    ap.add_argument('--max-chars', type=int, default=10 ** 6)
    ap.add_argument('--out')
    a = ap.parse_args()

    local = xa.load_local_texts()
    rows = xa.build_rows(a.csv, local)
    latest = max(r['date'] for r in rows if r['date'])
    cutoff = latest - timedelta(days=a.min_age)
    ripe = [r for r in rows if r['date'] and r['date'] <= cutoff]

    # 形を見るには全文が要る
    full = []
    for r in ripe:
        t = local.get(xa.norm_key(r['text']))
        if not t:
            continue
        if a.kind and r['kind'] != a.kind:
            continue
        if not (a.min_chars <= len(t) <= a.max_chars):
            continue
        r['full_text'] = t
        r.update(feats(r))
        full.append(r)

    out = [u'# Xの「書き方の形」の実測（%s 時点）' % latest.strftime('%Y-%m-%d'), u'']
    out.append(u'- 数えた投稿＝**%d本**（2日以上たった%d本のうち、全文が手元にある分）' % (len(full), len(ripe)))
    out.append(u'- 判定の決まり＝母数%d本未満は判定しない／外れ値1本を外した列と**同じ向き**の時だけ結論にする' % a.min_n)
    t = xa.stats(full)
    out.append(u'- 合計＝インプ中央 %s／クリック %d／1本あたり %.2f' % (
        xa.fmt(t['imp_median']), t['clicks'], t['clicks_per_post']))

    med = lambda key: xa.median([r[key] for r in full])  # noqa: E731

    xa.compare(u'二人称「あなた」を使ったか', bucket(
        full, lambda r: u'あなた入り' if r['you'] else u'なし', [u'あなた入り', u'なし']), a.min_n, out)

    xa.compare(u'結びが問いかけか（？・かしら・でしょう）', bucket(
        full, lambda r: u'問いかけで閉じる' if r['q_end'] else u'言い切りで閉じる',
        [u'問いかけで閉じる', u'言い切りで閉じる']), a.min_n, out)

    xa.compare(u'次の投稿の予告を入れたか', bucket(
        full, lambda r: u'予告あり' if r['next_post'] else u'なし', [u'予告あり', u'なし']), a.min_n, out)

    xa.compare(u'会場への行き方を書いたか', bucket(
        full, lambda r: u'行き方あり' if r['access'] else u'なし', [u'行き方あり', u'なし']), a.min_n, out)

    xa.compare(u'「その日に行けるか」の話（祝日・平日・仕事帰り）', bucket(
        full, lambda r: u'予定の話あり' if r['plan'] else u'なし', [u'予定の話あり', u'なし']), a.min_n, out)

    xa.compare(u'五感の言葉の数（声・音・光…）', bucket(
        full, lambda r: u'3語以上' if r['sense'] >= 3 else (u'1〜2語' if r['sense'] else u'0語'),
        [u'3語以上', u'1〜2語', u'0語']), a.min_n, out)

    xa.compare(u'【M/D発売】の一覧ブロックを置いたか', bucket(
        full, lambda r: u'一覧あり' if r['slotblock'] else u'なし', [u'一覧あり', u'なし']), a.min_n, out)

    m = med('linelen')
    xa.compare(u'1行の長さ（中央 %.0f字で二分）' % m, bucket(
        full, lambda r: u'短い行' if r['linelen'] < m else u'長い行', [u'短い行', u'長い行']), a.min_n, out)

    ms = med('sentlen')
    xa.compare(u'一文の長さ（中央 %.0f字で二分）' % ms, bucket(
        full, lambda r: u'短い文' if r['sentlen'] < ms else u'長い文', [u'短い文', u'長い文']), a.min_n, out)

    xa.compare(u'絵文字の数', bucket(
        full, lambda r: u'3個以上' if r['emoji'] >= 3 else (u'1〜2個' if r['emoji'] else u'0個'),
        [u'3個以上', u'1〜2個', u'0個']), a.min_n, out)

    xa.compare(u'タグの数', bucket(
        full, lambda r: u'4個以上' if r['tags'] >= 4 else u'3個まで', [u'4個以上', u'3個まで']), a.min_n, out)

    xa.compare(u'段落の数（空行）', bucket(
        full, lambda r: u'6段以上' if r['para'] >= 6 else u'5段まで', [u'6段以上', u'5段まで']), a.min_n, out)

    path = a.out or ('tmp/x_features_%s.md' % latest.strftime('%m%d'))
    io.open(path, 'w', encoding='utf-8').write(u'\n'.join(out) + u'\n')
    print('rows_ripe=%d rows_with_fulltext=%d report=%s' % (len(ripe), len(full), path))
    return 0


if __name__ == '__main__':
    sys.exit(main())
