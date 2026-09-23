# -*- coding: utf-8 -*-
"""e+ のエントリに、**売り場（e+）が言っているジャンル**を付ける恒久ツール。2026-09-23 新設。

  python tools/eplus_genre.py              … 新着プール(genre:"new")の e+ を全部調べる（書かない）
  python tools/eplus_genre.py --apply      … 調べて genre を入れ替える
  python tools/eplus_genre.py --ids 1,2    … id を絞る
  python tools/eplus_genre.py --selftest   … 対応表と抽出の回帰テスト

## なぜ要るか

e+ だけ `_genre` を付けずに投入していたので、**新着プールに272件が振り分けられないまま溜まっていた**
（TIGET・ZAIKO・FANY・楽天はビルダーが `_genre` を付けている）。
e+ も売り場としてジャンルを言っている＝**個別ページ本文の `/sf/live/<slug>` リンク**がそれ。

- 🎯実測271件で対応表に無いカテゴリは0件。裏取り＝モーニング娘。'26→idol／福田こうへい→enka／
  レキシ→j-pop／ヴィジュアル系のワンマン92件→visual（生誕単独・痛服限定ワンマン）
- ⚠️パンくずにジャンルは無い（TOP > ライブ･コンサート > <名前> チケット > 詳細）。JSON-LDにも無い
- 🚨**e+は叩きすぎると503**＝0.4秒だと272件中112件が失敗。**3秒間隔なら112件中111件が通った**
- 🚨取れなかった件は**触らない**（推測で埋めない）

🚨[[feedback_genre_pia_asis_and_other]]＝売り場の言う通りに機械で写す。人が最終判断する枠を作らない。
🚨[[feedback_genre_both_when_unclear]]＝カテゴリが2つ以上なら 主＝先頭・残り＝extraGenres。
🚨[[feedback_nonpia_user_eyes_until_gate]]＝ぴあ以外なので**振り分けはユーザーの確認後**。
🚨[[feedback_index_html_crlf_preserve]]＝CRLFのまま書き戻す（指紋が合わなければ書かない）。
"""
import argparse
import collections
import io
import json
import re
import sys
import time
import urllib.request

PATH = 'index.html'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/129.0 Safari/537.36'}
RX_LIVE = re.compile(r'/sf/live/([a-z0-9_-]+)')

# e+のカテゴリ → OSHINAVIジャンル。
# 行き先が無いカテゴリは ぴあの「民族音楽→yougaku」に合わせて「海外の音楽＝yougaku」へ寄せる
# （[[feedback_kaigai_is_area]]）。それでも当たらないものは表に足す＝**黙って musicetc に倒さない**。
EPLUS_GENRE = {
    'j-pop': 'jpop',
    'rock-indies': 'rock',
    'visual': 'rock',            # ヴィジュアル系＝ロックの下位
    'punk': 'rock',
    'metal': 'rock',
    'idol': 'idol',
    'voiceactor-live': 'seiyuu',
    'anime-song': 'anime',
    'vocaloid': 'vocaloid',
    'hiphop-rap': 'hiphop',
    'jazz-fusion': 'jazz',
    'enka': 'enka',
    'popular-song': 'enka',      # 歌謡曲＝ぴあの「演歌・邦楽→enka」に合わせる
    'kayokyoku': 'enka',
    'classical': 'classic',
    'classic': 'classic',
    'club-dj': 'club',
    'kpop': 'kpop',
    'k-pop': 'kpop',
    'k-pop-asian': 'kpop',
    'reggae': 'yougaku',
    'bossanova-latin': 'yougaku',
    'world-music': 'yougaku',
    'asian-pops': 'yougaku',
    'western-music': 'yougaku',
    'soul-rb': 'yougaku',
}


def cats_of(html):
    """本文に出てくる `/sf/live/<slug>` を出現順・重複除去で返す。"""
    seen, out = set(), []
    for m in RX_LIVE.finditer(html or ''):
        c = m.group(1)
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def fetch(url, tries=3, sleep=3.0):
    """取れなければ None（**嘘の空配列を返さない**）。e+は叩きすぎると503。"""
    for i in range(tries):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(sleep * (i + 2))
    return None


def _selftest():
    assert cats_of('<a href="/sf/live/j-pop">x</a>') == ['j-pop']
    assert cats_of('<a href="/sf/live/j-pop">x</a><a href="/sf/live/j-pop">y</a>') == ['j-pop']
    assert cats_of('a/sf/live/enka b/sf/live/popular-song') == ['enka', 'popular-song']
    assert cats_of('') == [] and cats_of(None) == []
    # 実測で裏が取れた対応（2026-09-23）
    for slug, want in (('j-pop', 'jpop'), ('enka', 'enka'), ('idol', 'idol'),
                       ('visual', 'rock'), ('voiceactor-live', 'seiyuu'),
                       ('rock-indies', 'rock'), ('anime-song', 'anime')):
        assert EPLUS_GENRE[slug] == want, slug
    # 🚨行き先が無いカテゴリを黙って musicetc に倒していないこと
    assert 'musicetc' not in EPLUS_GENRE.values()
    print('selftest OK')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--ids', default='')
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--report', default='tmp/eplus_genre_report.txt')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None
    text = io.open(PATH, encoding='utf-8', newline='').read()
    m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
    start = m.start(1)
    events, end = json.JSONDecoder().raw_decode(text, start)

    targets = [e for e in events
               if e.get('genre') == 'new' and (e.get('links') or {}).get('eplus')
               and (not want or e['id'] in want)]
    log, unknown, skipped = [], collections.Counter(), []
    n = err = 0
    cnt = collections.Counter()
    for i, e in enumerate(targets, 1):
        url = e['links']['eplus']
        html = fetch(url)
        if html is None:
            err += 1
            log.append('%s\tFETCH_ERR\t\t\t%s' % (e['id'], url))
            continue
        cats = cats_of(html)
        if not cats:
            log.append('%s\t(申告なし)\t\t%s\t%s' % (e['id'], (e.get('name') or ''), url))
            continue
        gs, bad = [], []
        for c in cats:
            g = EPLUS_GENRE.get(c)
            if g:
                if g not in gs:
                    gs.append(g)
            else:
                bad.append(c)
                unknown[c] += 1
        if bad:                        # 知らないカテゴリが混ざる件は触らず報告（表に足してから入れる）
            skipped.append((e['id'], e.get('name') or e.get('artist') or '', cats))
            continue
        e['genre'] = gs[0]
        if len(gs) > 1:
            e['extraGenres'] = gs[1:]
        n += 1
        cnt[gs[0]] += 1
        log.append('%s\t%s\t%s\t%s\t%s' % (e['id'], gs[0], ','.join(cats),
                                           (e.get('name') or e.get('artist') or ''), url))
        if i % 25 == 0:
            sys.stdout.write('%d/%d\n' % (i, len(targets)))
            sys.stdout.flush()
        time.sleep(a.sleep)

    pool = set(x['id'] for x in events if x.get('genre') == 'new')
    mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', text)
    arr = [int(x) for x in mo.group(1).split(',') if x.strip()]
    kept = [x for x in arr if x in pool]

    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('e+ ジャンル写し %d件 / 読めず %d / 対象 %d\n' % (n, err, len(targets)))
    rep.write('新着プール 残り %d件 ／ NEW_ORDER %d→%d\n\n' % (len(pool), len(arr), len(kept)))
    for k, c in cnt.most_common():
        rep.write('  %-12s %4d\n' % (k, c))
    if unknown:
        rep.write('\n== 対応表に無いカテゴリ（触らなかった）==\n')
        for k, c in unknown.most_common():
            rep.write('  %-20s %4d\n' % (k, c))
        for i2, nm, cs in skipped:
            rep.write('  id=%-6s %-40s %s\n' % (i2, nm[:40], ','.join(cs)))
    rep.write('\n== 明細（id / ジャンル / e+のカテゴリ / 公演名 / URL）==\n')
    rep.write('\n'.join(log) + '\n')
    rep.close()

    sys.stdout.write('eplus_genre: assigned=%d err=%d unknown_cats=%d skipped=%d apply=%s -> %s\n'
                     % (n, err, len(unknown), len(skipped), a.apply, a.report))
    if not a.apply:
        return 0

    body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
    newtext = text[:start] + body + text[end:]
    newtext = re.sub(r'const NEW_ORDER = \[[^\]]*\];',
                     'const NEW_ORDER = [%s];' % ', '.join(str(x) for x in kept), newtext, count=1)
    data = newtext.encode('utf-8')
    if data.count(b'\r\n') != data.count(b'\n'):
        sys.stdout.write('ABORT: CRLF broken\n')
        return 1
    io.open(PATH, 'wb').write(data)
    sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
