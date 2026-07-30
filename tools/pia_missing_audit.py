# -*- coding: utf-8 -*-
"""【ツアー取りこぼしの一括監査】登録済みアーティスト名でぴあを引き直し、**未登録のeventCd**を炙り出す。

【なぜ要るか＝reconcile_piaでは絶対に見つからない型】
reconcile_pia は「登録してあるURLの中身」しか見ない。だから **そもそも登録していないeventCd は
存在ごと機械に見えない**。2026-07-30、ユーザーが目で2件見つけた:
  - id3278 SPECIAL OTHERS ＝ 沖縄12/12・北海道11/3・高知11/21 の3枠が欠落
  - id2202 おいしくるメロンパン ＝ 北海道1公演しか無く、東京/広島/新潟/岩手/宮城/東京(千秋楽)を落としていた
    （ユーザーは**公式サイト**で気づいた。そして**全部ぴあに在った**＝harvestが拾えていないだけ）
どちらも harvest が「既存artist名で除外」するせいで同名の別公演を永久に拾えない型
([[feedback_harvest_name_dedup_blindspot]]) と、ツアーの別会場を拾えない型
([[feedback_tour_cross_channel_blindspot]]) の実害。

【やること】
  1. index.html の全エントリから **登録済みの全ぴあeventCd/eventBundleCd** を集める
     （links.pia だけでなく各 ticket.url も見る＝会場別URLを持つツアーを誤検出しない）
  2. artist名を重複排除してキーワード列を作る
  3. 各キーワードで `rlsInfo.do?kw=` を引く（pia_kw_search.search を再利用）
  4. ヒットしたeventCdのうち **どのエントリにも登録が無いもの** を「取りこぼし候補」として出す
     - harvest_exclude.json の「調べた上で対象外」は除外する
     - キーワードが公演名に入っていないヒットは `[別名義/フェス出演]` と印を付ける（本人名義でない可能性）

使い方:
  python tools/pia_missing_audit.py --count                # 何件のキーワードを引くかだけ表示(通信しない)
  python tools/pia_missing_audit.py --limit 40             # 先頭40キーワードだけ
  python tools/pia_missing_audit.py --genres jpop,yougaku  # ジャンル絞り(既定は音楽・ライブ系)
  python tools/pia_missing_audit.py --all-genres --all-keywords   # 全部(重い)
  python tools/pia_missing_audit.py --resume               # 前回の続きから(状態ファイルを使う)
  python tools/pia_missing_audit.py --selftest
  オプション: --wait 秒(キーワード間の間隔・既定5) / --out path / --state path

🚨ぴあ429対策＝キーワード間に既定5秒空ける。fetch失敗が5連続したら中断する
([[reference_pia_rate_limit_429]]＝429でゲートが静かに壊れる)。
出力はUTF-8ファイル（コンソールに日本語を出さない＝化け読み事故防止 [[feedback_no_mojibake_japanese_read]]）。
"""
import datetime
import io
import json
import os
import re
import sys
import time
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

_spec = importlib.util.spec_from_file_location('pks', os.path.join(HERE, 'pia_kw_search.py'))
pks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pks)

ARGS = sys.argv[1:]


def opt(name, default=None):
    if name in ARGS:
        i = ARGS.index(name)
        if i + 1 < len(ARGS) and not ARGS[i + 1].startswith('--'):
            return ARGS[i + 1]
        return True
    return default


# 音楽・ライブ系＝ツアーを回すのでいちばん取りこぼしやすい
DEFAULT_GENRES = ['jpop', 'yougaku', 'idol', 'jazz', 'anime', 'classic', 'dento', 'owarai', 'musical']

CD_RE = re.compile(r'event(?:Bundle)?Cd=(\w+)')


def cds(url):
    return CD_RE.findall(url or '')


def load_events(path=None):
    h = open(path or os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S)
    return json.loads(m.group(1))


def registered_cds(evs):
    """登録済みの全ぴあコード（links.pia＋各ticket.url）"""
    out = set()
    for ev in evs:
        p = (ev.get('links') or {}).get('pia') or ''
        if 'pia' in p:
            out.update(cds(p))
        for t in ev.get('tickets', []):
            u = t.get('url') or ''
            if 'pia' in u:
                out.update(cds(u))
    return out


def load_excluded():
    """harvest_exclude.json の「調べた上で対象外」コード集合"""
    p = os.path.join(HERE, 'harvest_exclude.json')
    if not os.path.exists(p):
        return set()
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception:
        return set()
    out = set()

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if re.fullmatch(r'b?\d{6,}', str(k)):
                    out.add(str(k))
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            if re.fullmatch(r'b?\d{6,}', x):
                out.add(x)
    walk(d)
    return out


# キーワードに向かないもの＝公演名/イベント名（引いても0件で通信の無駄）
BAD_KW = re.compile(r'第\s*\d|回\s*[記大]|大会|花火|祭|博覧|展\s*$|フェスティバル|コンサート20|公演|会場')


def rls_iso(rlsdate, today):
    """ぴあの発売日表記('2026/08/03' / 'TODAY' / '')をISOに。空(=受付中で既に買える)はNone。"""
    if not rlsdate:
        return None
    if rlsdate == 'TODAY':
        return today
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', rlsdate)
    if not m:
        return None
    return '%04d-%02d-%02d' % (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def in_scope(m, rls_from, today):
    """--rls-from 指定時、『発売日がその日以降』の候補だけを本命扱いにする。
    発売日が無い枠(=既に受付中)や今日/明日発売はカウントダウンにならないので対象外。"""
    if not rls_from:
        return True
    iso = rls_iso(m.get('rlsdate'), today)
    return bool(iso) and iso >= rls_from


def good_keyword(name, allow_all=False):
    n = (name or '').strip()
    if not n or len(n) < 2:
        return False
    if allow_all:
        return True
    if len(n) > 22:
        return False
    if BAD_KW.search(n):
        return False
    return True


def keywords(evs, genres, allow_all_kw):
    """artist名を重複排除。登録の多い順ではなく、ぴあリンクを持つものだけ。"""
    seen, out = set(), []
    for ev in evs:
        if not ((ev.get('links') or {}).get('pia') or ''):
            continue
        if genres is not None and ev.get('genre') not in genres:
            continue
        a = (ev.get('artist') or '').strip()
        if a in seen or not good_keyword(a, allow_all_kw):
            continue
        seen.add(a)
        out.append(a)
    return out


def audit(kws, reg, excl, wait, state_path, out_path, prior=None, rls_from=None, today=None):
    state = dict(prior or {})
    fails = 0
    results = state.setdefault('results', {})
    for i, kw in enumerate(kws):
        if kw in results:
            print('[%d/%d] skip (done)' % (i + 1, len(kws)))
            continue
        log = []
        try:
            found = pks.search(kw, log)
        except Exception as e:
            print('[%d/%d] FETCH-ERROR %s' % (i + 1, len(kws), type(e).__name__))
            fails += 1
            if fails >= 5:
                print('!! 5 consecutive fetch errors -> abort (suspect 429)')
                break
            time.sleep(wait * 4)
            continue
        if any('fetch失敗' in l for l in log):
            fails += 1
            if fails >= 5:
                print('!! 5 consecutive fetch failures -> abort (suspect 429)')
                break
        else:
            fails = 0

        miss = []
        for u, x in found.items():
            c = cds(u)
            if not c:
                continue
            code = c[0]
            if code in reg or code in excl:
                continue
            miss.append({
                'code': code, 'url': u, 'title': x['title'], 'status': x['status'],
                'perfdate': x['perfdate'], 'venue': x['venue'], 'rlsdate': x['rlsdate'],
                'own_name': kw in x['title'],
            })
        results[kw] = {'hits': len(found), 'missing': miss}
        print('[%d/%d] hits=%d missing=%d' % (i + 1, len(kws), len(found), len(miss)))

        json.dump(state, open(state_path, 'w', encoding='utf-8'), ensure_ascii=False)
        write_report(results, out_path, len(kws), rls_from, today)
        if i != len(kws) - 1:
            time.sleep(wait)
    return results


def write_report(results, out_path, total, rls_from=None, today=None):
    lines = ['ぴあ ツアー取りこぼし一括監査', '']
    lines.append('引いたキーワード: %d / 予定 %d' % (len(results), total))
    hot = {k: v for k, v in results.items() if v['missing']}
    if rls_from:
        lines.append('本命の条件: 発売日が %s 以降（それより前・既に受付中のものは末尾の「参考」へ）' % rls_from)
    lines.append('')
    lines.append('※「本人名義」＝ヒットした公演名にキーワードが入っているもの＝ツアーの取りこぼしの本命。')
    lines.append('※「別名義/フェス出演」＝サマソニ等に名前が出ただけの可能性。別エントリで持っている場合もある。')
    lines.append('')

    def block(title, pred):
        lines.append('=' * 72)
        lines.append('■ %s' % title)
        lines.append('=' * 72)
        n = 0
        for kw in sorted(hot):
            ms = [m for m in hot[kw]['missing'] if pred(m)]
            if not ms:
                continue
            lines.append('')
            lines.append('● %s  （ぴあのヒット %d 件・うち未登録 %d 件）' % (kw, hot[kw]['hits'], len(ms)))
            for m in sorted(ms, key=lambda x: (x['rlsdate'] or 'zzzz', x['perfdate'], x['code'])):
                n += 1
                lines.append('   [%s] %s' % (m['status'] or '状態不明', m['title']))
                lines.append('     公演日: %s ／ 会場: %s' % (m['perfdate'] or '(空)', m['venue'] or '(空)'))
                lines.append('     発売日: %s' % (m['rlsdate'] or '(空＝既に受付中)'))
                lines.append('     URL   : %s' % m['url'])
        if n == 0:
            lines.append('')
            lines.append('   （なし）')
        lines.append('')
        return n

    a = block('🎯本命＝本人名義の取りこぼし候補', lambda m: m['own_name'] and in_scope(m, rls_from, today))
    b = block('別名義・フェス出演の候補（本人のツアーではない可能性・別エントリ持ちかも）',
              lambda m: (not m['own_name']) and in_scope(m, rls_from, today))
    c = 0
    if rls_from:
        c = block('（参考・今回の対象外＝発売日が %s より前、または既に受付中）' % rls_from,
                  lambda m: not in_scope(m, rls_from, today))

    lines.insert(3, '候補件数: 本命(本人名義) %d ／ 別名義・フェス %d ／ 参考(対象外) %d' % (a, b, c))
    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


def selftest():
    # cds(): 両形式を拾う
    assert cds('https://t.pia.jp/pia/event/event.do?eventCd=2621430') == ['2621430']
    assert cds('https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669282') == ['b2669282']
    assert cds(None) == []

    # registered_cds(): ticket.url も必ず見る（会場別URLのツアーを取りこぼしと誤検出しない）
    evs = [{
        'artist': 'A', 'genre': 'jpop',
        'links': {'pia': 'https://t.pia.jp/pia/event/event.do?eventCd=111111'},
        'tickets': [
            {'url': 'https://t.pia.jp/pia/event/event.do?eventCd=222222'},
            {'url': 'https://eplus.jp/sf/detail/xxx'},
        ],
    }]
    reg = registered_cds(evs)
    assert reg == {'111111', '222222'}, reg

    # good_keyword(): 公演名っぽいものは引かない／アーティスト名は引く
    assert good_keyword('おいしくるメロンパン')
    assert good_keyword('SPECIAL OTHERS')
    assert not good_keyword('第56回田辺花火大会')
    assert not good_keyword('第39期竜王戦第2局三島対局 前夜祭')
    assert not good_keyword('')
    # --all-keywords なら通す
    assert good_keyword('第56回田辺花火大会', allow_all=True)

    # keywords(): ぴあリンク無しは対象外・重複排除・ジャンル絞り
    evs2 = [
        {'artist': 'XX', 'genre': 'jpop', 'links': {'pia': 'p?eventCd=1'}, 'tickets': []},
        {'artist': 'XX', 'genre': 'jpop', 'links': {'pia': 'p?eventCd=2'}, 'tickets': []},
        {'artist': 'YY', 'genre': 'sports', 'links': {'pia': 'p?eventCd=3'}, 'tickets': []},
        {'artist': 'ZZ', 'genre': 'jpop', 'links': {'pia': None}, 'tickets': []},
    ]
    assert keywords(evs2, ['jpop'], False) == ['XX'], keywords(evs2, ['jpop'], False)
    assert keywords(evs2, None, False) == ['XX', 'YY']
    # 1文字は引かない（ぴあが無関係な大量ヒットを返す）
    assert not good_keyword('X')

    # rls_iso / in_scope ＝「明後日発売以降だけ」の絞り込み
    assert rls_iso('2026/08/03', '2026-07-30') == '2026-08-03'
    assert rls_iso('2026/8/3', '2026-07-30') == '2026-08-03'
    assert rls_iso('TODAY', '2026-07-30') == '2026-07-30'
    assert rls_iso('', '2026-07-30') is None
    T = '2026-07-30'
    assert in_scope({'rlsdate': '2026/08/03'}, '2026-08-01', T) is True
    assert in_scope({'rlsdate': '2026/08/01'}, '2026-08-01', T) is True   # 境界=含む
    assert in_scope({'rlsdate': '2026/07/31'}, '2026-08-01', T) is False  # 明日発売は対象外
    assert in_scope({'rlsdate': 'TODAY'}, '2026-08-01', T) is False       # 本日発売は対象外
    assert in_scope({'rlsdate': ''}, '2026-08-01', T) is False            # 既に受付中は対象外
    assert in_scope({'rlsdate': ''}, None, T) is True                     # 未指定なら全部本命

    # 陽性テスト＝登録済みコードは候補に出ない／未登録だけ出る
    found = {
        'https://t.pia.jp/pia/event/event.do?eventCd=111111': {
            'title': 'A', 'status': '受付中', 'perfdate': '', 'venue': '', 'rlsdate': ''},
        'https://t.pia.jp/pia/event/event.do?eventCd=999999': {
            'title': 'A ツアー', 'status': '発売前', 'perfdate': '', 'venue': '', 'rlsdate': ''},
    }
    miss = [c for u, x in found.items() for c in cds(u) if c not in reg]
    assert miss == ['999999'], miss
    print('selftest OK (cds/registered_cds/good_keyword/keywords + positive case)')


def main():
    if '--selftest' in ARGS:
        return selftest()

    evs = load_events()
    reg = registered_cds(evs)
    excl = load_excluded()

    genres = None if '--all-genres' in ARGS else DEFAULT_GENRES
    g = opt('--genres')
    if isinstance(g, str):
        genres = [x.strip() for x in g.split(',') if x.strip()]

    kws = keywords(evs, genres, '--all-keywords' in ARGS)
    lim = opt('--limit')
    if isinstance(lim, str):
        kws = kws[:int(lim)]

    out_path = opt('--out') or os.path.join(ROOT, 'tmp', 'pia_missing_audit.txt')
    state_path = opt('--state') or os.path.join(ROOT, 'tmp', 'pia_missing_audit_state.json')
    wait = float(opt('--wait') or 5)
    today = datetime.date.today().isoformat()
    rf = opt('--rls-from')
    rls_from = rf if isinstance(rf, str) else None
    if rls_from:
        print('scope: only candidates whose sale-start date >= %s (today=%s)' % (rls_from, today))

    # pia_kw_search は既定で5フィルタのunionを引く（1キーワード≒10 fetch）。
    # 大量キーワードを回すと429を呼ぶので、監査では既定を「無フィルタ＋発売前(rlsIn=03)」に絞る。
    # 「発売日が先のもの」を探す用途なので rlsIn=03 が本命。--filters all で従来の5本に戻せる。
    fl = opt('--filters')
    if fl == 'all':
        pass
    elif isinstance(fl, str):
        pks.FILTERS = [x.strip() for x in fl.split(',')]
        pks.FILTERS = ['' if x in ('none', '(無)') else x for x in pks.FILTERS]
    else:
        pks.FILTERS = ['', 'rlsIn=03']
    print('pia filters per keyword: %s' % ','.join(f or '(none)' for f in pks.FILTERS))

    print('entries=%d  registered pia codes=%d  excluded=%d' % (len(evs), len(reg), len(excl)))
    print('keywords to query = %d  (genres=%s)' % (len(kws), 'ALL' if genres is None else ','.join(genres)))
    if '--count' in ARGS:
        print('(--count: no network access performed)')
        return 0

    prior = None
    if '--resume' in ARGS and os.path.exists(state_path):
        prior = json.load(open(state_path, encoding='utf-8'))
        print('resume: %d keywords already done' % len(prior.get('results', {})))

    est = len(kws) * (wait + 2.5) / 60.0
    print('rough ETA: %.0f min (wait=%.1fs/keyword)' % (est, wait))
    results = audit(kws, reg, excl, wait, state_path, out_path, prior, rls_from, today)
    write_report(results, out_path, len(kws), rls_from, today)
    hot = sum(1 for v in results.values() if v['missing'])
    n = sum(len(v['missing']) for v in results.values())
    print('done. queried=%d  keywords_with_missing=%d  candidate_codes=%d' % (len(results), hot, n))
    print('report: %s' % out_path)
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
