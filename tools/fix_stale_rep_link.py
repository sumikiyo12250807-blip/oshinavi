# -*- coding: utf-8 -*-
"""カードの大きいリンク（links.<売り場>）が「締切の過ぎた枠だけ」を指しているのを、同じ売り場のこれからの枠へ付け替える。

2026-11-20 抜き打ち 44612 つきみ（e+ 茨城 11/15 のページ＝もう404）・2831 Homecomings（ぴあのまとめページに9月の3公演だけ）。
ツアーの最初の会場で作ったカードは、最初の会場が終わると大きいリンクが「売っていない」「見つからない」ページになる。
枠ごとのリンクは正しいので画面のバッジからは買えるが、いちばん目立つボタンが行き止まりになる。468件たまっていた。

  python tools/fix_stale_rep_link.py            … 数えるだけ（見つかれば exit 1＝push 前の番人）
  python tools/fix_stale_rep_link.py --apply    … 付け替える（鍵は呼ぶ側で取る）
  python tools/fix_stale_rep_link.py --selftest

付け替える条件（どれか欠けたら触らない）：
  ・公演がこれから・新着ではない
  ・そのリンクと同じ URL の枠が1つ以上あり、全部締切が今日より前
  ・URL の無い枠が1つも無い（URL の無い枠は大きいリンクへ飛ぶ＝付け替えると行き先が変わる）
  ・同じ売り場（同じホスト）に締切が今日以降の枠がある → いちばん早い締切の枠の URL へ
"""
import datetime, io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compact_events as C  # noqa: E402

ROOT = 'C:/Users/user/oshinavi/'


def host(u):
    try:
        return u.split('/')[2]
    except IndexError:
        return ''


def plan(e, today):
    """付け替え [(key, 古い, 新しい)]"""
    if e.get('genre') == 'new' or (e.get('date') or '') < today:
        return []
    T = e.get('tickets') or []
    if not T or any(not t.get('url') for t in T):
        return []
    out = []
    for k, u in (e.get('links') or {}).items():
        if not u or k == 'amazon' or not isinstance(u, str):
            continue
        if 'eventBundleCd=' in u:
            # ぴあのまとめページはヒールが「後から足された会場」を拾う入口（heal_stale_deadlines.pia_urls）＝付け替えない
            continue
        same = [t for t in T if t.get('url') == u]
        if not same or any((t.get('date') or '') >= today for t in same):
            continue
        fut = sorted((t for t in T if (t.get('date') or '') >= today and host(t['url']) == host(u)), key=lambda t: (t['date'], t['url']))
        if fut:
            out.append((k, u, fut[0]['url']))
    return out


def _selftest():
    td = '2026-11-20'
    e = {'id': 1, 'date': '2027-01-17', 'genre': 'rock', 'links': {'eplus': 'https://eplus.jp/a', 'amazon': 'x'},
         'tickets': [{'date': '2026-11-14', 'url': 'https://eplus.jp/a'}, {'date': '2026-12-05', 'url': 'https://eplus.jp/c'},
                     {'date': '2026-11-21', 'url': 'https://eplus.jp/b'}]}
    assert plan(e, td) == [('eplus', 'https://eplus.jp/a', 'https://eplus.jp/b')], plan(e, td)
    e2 = json.loads(json.dumps(e)); e2['tickets'].append({'date': '2026-12-01'})
    assert plan(e2, td) == []                       # URL の無い枠がある
    e3 = json.loads(json.dumps(e)); e3['tickets'][0]['date'] = '2026-11-20'
    assert plan(e3, td) == []                       # 大きいリンクの枠がまだ生きている
    e4 = json.loads(json.dumps(e)); e4['tickets'] = [e4['tickets'][0], {'date': '2026-12-05', 'url': 'https://t.pia.jp/x'}]
    assert plan(e4, td) == []                       # 同じ売り場にこれからの枠が無い
    e5 = json.loads(json.dumps(e)); e5['genre'] = 'new'
    assert plan(e5, td) == []
    e6 = {'id': 2, 'date': '2027-01-17', 'links': {'pia': 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b1'},
          'tickets': [{'date': '2026-11-01', 'url': 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b1'},
                      {'date': '2026-12-01', 'url': 'https://t.pia.jp/pia/event/event.do?eventCd=2'}]}
    assert plan(e6, td) == []                       # ぴあのまとめページは触らない
    print('selftest OK')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if '--selftest' in sys.argv:
        return _selftest()
    today = datetime.date.today().isoformat()
    s = io.open(ROOT + 'index.html', encoding='utf-8', newline='').read()
    E = C.load(s)
    n = 0
    for e in E:
        for k, a, b in plan(e, today):
            n += 1
            if n <= 15:
                print('id%s %s %s\n   %s → %s' % (e['id'], k, (e.get('name') or '')[:30], a, b))
            if '--apply' in sys.argv:
                e['links'][k] = b
    print('fix_stale_rep_link: 付け替え %d%s' % (n, ' → 書いた' if n and '--apply' in sys.argv else ''))
    if n and '--apply' in sys.argv:
        st, en, _ = C.locate(s)
        body = C.dump(E, True, '\r\n')
        io.open(ROOT + 'index.html', 'w', encoding='utf-8', newline='').write(s[:st] + body + s[en:])
    if n and '--apply' not in sys.argv:
        sys.exit(1)


if __name__ == '__main__':
    main()
