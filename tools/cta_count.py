# -*- coding: utf-8 -*-
"""X投稿のCTAリンクが、着地先で**何件出すのか**を数える恒久ツール。2026-09-23 新設。

  python tools/cta_count.py                       … 主なジャンルの件数を一覧
  python tools/cta_count.py --url "oshinavi.jp/?genre=kids&status=urgent"
  python tools/cta_count.py --posts tmp/x0923     … そのフォルダの post*.txt からURLを拾って全部数える
  python tools/cta_count.py --selftest

## なぜ要るか（2026-09-23 ユーザー指摘）

> 「**５件しか出てこない**」「**下に出した絞ったURL かえって使いにくい**」
> 「**絞り込みが何の絞り込みか　分かりにくいとクリックした後しんどい**」

`&status=urgent` は画面の「🔴 今週発売」＝**発売開始日が7日以内の枠を持つ公演だけ**。
まとめ投稿は「明日発売」を並べているのに、着地先が「今週発売」で絞られてほとんど消えていた。
実測＝kids 233→10／seiyuu 23→3／fanevent 236→17／全体 16,298→808。
→ [[feedback_x_cta_wording]]＝**まとめ枠は `?genre=xxx` だけ。`status` は書かない。**

🚨**文面をユーザーに見せる前にこれを回して、10件を切るリンクが無いか見る。**
画面のロジック（`eventReleaseStatus` / `matchGenre`）を写してあるので、実物と同じ数が出る。
"""
import argparse
import datetime
import glob
import io
import json
import os
import re
import sys
import urllib.parse

# 🚨Windowsのcp932では絵文字が書けずに落ちる＝出口をUTF-8に固定する
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PATH = 'index.html'
WARN = 10          # これを切ったら「絞りすぎ」と鳴らす


def load():
    text = io.open(PATH, encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    events, _ = json.JSONDecoder().raw_decode(text, m.start(1))
    return events


def _d(s):
    try:
        return datetime.date(*map(int, (s or '').split('-')))
    except Exception:
        return None


def rel_status(ev, today):
    """発売前（発売開始日が今日以降）の枠だけを見て urgent/soon/normal。無ければ None。"""
    best = None
    for t in ev.get('tickets') or []:
        sd = _d(t.get('startDate'))
        if not sd or sd < today:
            continue
        diff = (sd - today).days
        s = 'urgent' if diff <= 7 else ('soon' if diff <= 31 else 'normal')
        rank = {'urgent': 0, 'soon': 1, 'normal': 2}[s]
        if best is None or rank < best[0]:
            best = (rank, s)
    return best[1] if best else None


def match_genre(ev, g):
    if g == 'all':
        return True
    if ev.get('genre') == g or g in (ev.get('extraGenres') or []):
        return True
    if g == 'engeki' and ev.get('genre') in ('2.5ji', 'seiyuu', 'musical'):
        return True
    if g == 'anime' and ev.get('genre') == 'seiyuu':
        return True
    return False


def count(events, today, genre='all', status='all', q=''):
    n = 0
    ql = (q or '').lower()
    for ev in events:
        if ev.get('verified') is not True:
            continue
        if ql:                        # ?q= は絞り込みを外して名前で探す（画面と同じ）
            hay = ((ev.get('artist') or '') + ' ' + (ev.get('name') or '')).lower()
            if ql not in hay:
                continue
        else:
            if not match_genre(ev, genre):
                continue
            if status != 'all':
                r = rel_status(ev, today)
                if status == 'urgent' and r != 'urgent':
                    continue
                if status == 'soon' and r not in ('urgent', 'soon'):
                    continue
                if status == 'upcoming' and r != 'normal':
                    continue
        n += 1
    return n


def parse_url(u):
    qs = urllib.parse.parse_qs(urllib.parse.urlparse('https://' + u.replace('https://', '')).query)
    return (qs.get('genre', ['all'])[0], qs.get('status', ['all'])[0],
            urllib.parse.unquote(qs.get('q', [''])[0]))


def _selftest():
    ev = [{'verified': True, 'genre': 'kids', 'artist': 'A', 'name': 'a',
           'tickets': [{'startDate': '2026-09-25', 'date': '2026-09-25'}]},
          {'verified': True, 'genre': 'kids', 'artist': 'B', 'name': 'b',
           'tickets': [{'startDate': '2026-11-01', 'date': '2026-11-01'}]},
          {'verified': False, 'genre': 'kids', 'artist': 'C', 'name': 'c', 'tickets': []}]
    t = datetime.date(2026, 9, 23)
    assert count(ev, t, 'kids', 'all') == 2, '未確認は数えない'
    assert count(ev, t, 'kids', 'urgent') == 1, '7日以内だけ'
    assert count(ev, t, 'kids', 'soon') == 1, '31日以内'
    assert count(ev, t, 'all', 'all') == 2
    assert count(ev, t, 'all', 'all', 'A') == 1, 'q は名前で探す'
    assert parse_url('oshinavi.jp/?genre=kids&status=urgent') == ('kids', 'urgent', '')
    assert parse_url('oshinavi.jp/?q=%E5%9D%8246')[2] == '坂46'
    print('selftest OK')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default='')
    ap.add_argument('--posts', default='')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    today = datetime.date(*map(int, a.today.split('-')))
    events = load()
    bad = 0

    def show(u):
        nonlocal bad
        g, s, q = parse_url(u)
        n = count(events, today, g, s, q)
        # 🚨主役枠（?q=）は**1組に絞るのが目的**なので件数が少なくて正常＝鳴らさない。
        #    鳴らすのはまとめ枠（?genre= / ?status=）だけ。
        warn = (not q) and n < WARN
        mark = '🚨' if warn else ('👤' if q else '  ')
        sys.stdout.write('%s %6d件  %s\n' % (mark, n, u))
        if warn:
            bad += 1

    if a.url:
        show(a.url)
    elif a.posts:
        seen = []
        for f in sorted(glob.glob(os.path.join(a.posts, 'post*.txt'))):
            for u in re.findall(r'oshinavi\.jp/\?\S+', io.open(f, encoding='utf-8').read()):
                u = u.rstrip('。、」）)')
                if u not in seen:
                    seen.append(u)
                    show(u)
    else:
        for g in ('all', 'kids', 'idol', 'jpop', 'rock', 'classic', 'jazz', 'owarai',
                  'enka', 'seiyuu', 'fanevent', 'event', 'engeki', 'sports', 'movie'):
            sys.stdout.write('%-10s 絞りなし %6d / urgent %5d / soon %5d\n'
                             % (g, count(events, today, g, 'all'),
                                count(events, today, g, 'urgent'),
                                count(events, today, g, 'soon')))
    if bad:
        sys.stdout.write('\n🚨 %d本が %d件未満＝絞りすぎ。status を外すか、ジャンルを広げる\n' % (bad, WARN))
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
