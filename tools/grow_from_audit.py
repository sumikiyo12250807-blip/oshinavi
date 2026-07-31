# -*- coding: utf-8 -*-
"""【監査で見つけた取りこぼしでエントリを育てる】pia_missing_audit の本命候補を既存エントリに取り込む。

pia_missing_audit.py が「登録に無いeventCd」を炙り出したあと、それを実際にエントリへ入れる工程。
やり方は tmp/rescue_0730.py と同じ流儀＝**ぴあから作り直して差分を見せ、--apply で置換**。

【何を上書きし、何を守るか】
  上書きする: tickets(ぴあ由来分) / date(千秋楽) / dateLabel / venue / prefecture
    → 千秋楽を動かさないと「まだ買えるのにカードが画面から消える」(id3278 SPECIAL OTHERSで実害)。
      会場や県も1公演のまま残すと嘘になる(「北海道 CASINO DRIVE」のまま8会場ツアーになってしまう)。
  守る: artist / name / links / verified / genre など人が決めた項目
    → 手で直した表記を巻き戻さない。
  守る: **非ぴあ枠(ticket.url が e+/楽天/ローチケ)** は消さずに残す
    → build() はぴあ枠しか作らないので、素直に置換すると他の売り場が消える。

使い方:
  python tools/grow_from_audit.py                      # 全件ドライラン(差分をファイルに出す)
  python tools/grow_from_audit.py --limit 10           # 先頭10組だけ
  python tools/grow_from_audit.py --ids 2202,3278      # 指定エントリだけ
  python tools/grow_from_audit.py --apply              # 適用(バックアップを取る)
  python tools/grow_from_audit.py --selftest
  オプション: --state path / --out path / --rls-from YYYY-MM-DD

適用後は必ず `reconcile_pia.py --ids <触ったid>` と `check_order.js` を通す。
"""
import datetime
import io
import json
import os
import re
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def _load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


ARGS = sys.argv[1:]

# build_pia_entries は import時に sys.stdout をUTF-8で差し替える。差し替え前の実stdoutを
# 押さえておき、進捗はこちらに出す（差し替えられた側が閉じられて I/O error になるのを避ける）。
_REAL_OUT = sys.__stdout__

# 既存のぴあ枠が消える育成は、既定では自動適用しない（誤削除は不可逆）。
ALLOW_DROP = '--allow-drop' in ARGS


def say(msg):
    try:
        _REAL_OUT.write(msg + '\n')
        _REAL_OUT.flush()
    except Exception:
        pass


def pia_urls(ev):
    """このエントリが参照する全ぴあURL（links.pia + 各ticket.url）。
    reconcile_pia.pia_urls と同じ規則。あちらを import すると build_pia_entries が
    二重ロードされて stdout が壊れるので、ここに同じものを持つ。"""
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p and 'pia' in p:
        urls.append(p)
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls:
            urls.append(u)
    return urls


def opt(name, default=None):
    if name in ARGS:
        i = ARGS.index(name)
        if i + 1 < len(ARGS) and not ARGS[i + 1].startswith('--'):
            return ARGS[i + 1]
        return True
    return default


def is_pia_ticket(t):
    """ぴあ由来の枠か（url無し＝links.pia由来、もしくはurlがぴあ）。非ぴあは守る対象。"""
    u = t.get('url') or ''
    return (not u) or ('pia.jp' in u)


def merge_tickets(built_tickets, cur_tickets):
    """ぴあ枠は作り直した方を採用し、非ぴあ枠(e+/楽天/ローチケ)はそのまま残す。"""
    keep = [t for t in cur_tickets if not is_pia_ticket(t)]
    return list(built_tickets) + keep


def perf_key(type_):
    """券種名から「どの公演の枠か」を取り出す。先行の回数(2次→3次)で別枠と誤判定しないため。
    例: '2次受付（岩手・宮城 10/25〜10/27公演）〜7/28 11:00' → '岩手・宮城 10/25〜10/27公演'"""
    m = re.search(r'[（(]([^（）()]*公演[^（）()]*)[）)]', type_ or '')
    if m:
        return m.group(1).strip()
    return (type_ or '').strip()


def lost_pia_slots(built_tickets, cur_tickets):
    """今ある「ぴあ由来の枠」のうち、作り直しに同じ公演の枠が無いもの＝消える枠。
    売切/終了なら消えて正しいが、ぴあの一過性の空ページだと生きた枠を消してしまう
    ([[reference_pia_rate_limit_429]]と同型)。だから必ず人の目に出す。"""
    newk = {perf_key(t.get('type')) for t in built_tickets}
    return [t for t in cur_tickets if is_pia_ticket(t) and perf_key(t.get('type')) not in newk]


def pick_date(built_date, cur_date, kept_tickets):
    """千秋楽は「作り直した千秋楽」と「今の千秋楽」の遅い方。
    非ぴあ枠だけが持つ後半公演を、ぴあ由来の千秋楽で短くしてしまわないため。"""
    cands = [d for d in [built_date, cur_date] if d]
    return max(cands) if cands else cur_date


def norm_pia(u):
    m = re.search(r'eventBundleCd=(\w+)', u or '')
    if m:
        return 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + m.group(1)
    m = re.search(r'eventCd=(\w+)', u or '')
    if m:
        return 'https://t.pia.jp/pia/event/event.do?eventCd=' + m.group(1)
    return None


def targets_from_state(state, evs, rls_from, today, pma):
    """監査の状態ファイル → {id: {'artist','new_urls','entry'}}。
    アーティスト名で一致するエントリが1件のときだけ自動対象にする（複数はどれを育てるか機械では決められない）。"""
    by_artist = {}
    for ev in evs:
        by_artist.setdefault((ev.get('artist') or '').strip(), []).append(ev)

    out, ambiguous, orphan = {}, [], []
    for kw, v in (state.get('results') or {}).items():
        ms = [m for m in v['missing'] if m['own_name'] and pma.in_scope(m, rls_from, today)]
        if not ms:
            continue
        evl = by_artist.get(kw) or []
        if len(evl) == 0:
            orphan.append((kw, len(ms)))
            continue
        if len(evl) > 1:
            ambiguous.append((kw, len(ms), [e.get('id') for e in evl]))
            continue
        ev = evl[0]
        urls = [norm_pia(m['url']) for m in ms]
        out[ev['id']] = {'artist': kw, 'new_urls': [u for u in urls if u], 'entry': ev}
    return out, ambiguous, orphan


def main():
    if '--selftest' in ARGS:
        return selftest()

    pma = _load('pma', 'pia_missing_audit.py')
    bpe = _load('bpe', 'build_pia_entries.py')

    today = datetime.date.today().isoformat()
    rf = opt('--rls-from')
    # 🚨 `--rls-from all` ＝発売日で絞らない（2026-07-31追加）。
    # 既定の「発売日が指定日以降」は**カウントダウン価値のある新規発掘**の考え方で、
    # **既に受付中の枠を丸ごと落とす**（in_scope は発売日が空だと必ず False）。
    # 育成は「登録済みエントリに同じツアーの買える枠が抜けている」のを埋める作業なので、
    # 受付中も入れないと取りこぼしが残る（布袋寅泰3533＝先行抽選が受付中の10枠が落ちていた）。
    # [[feedback_capture_all_not_select]] 発売前も受付中も網羅する。
    rls_from = None if (isinstance(rf, str) and rf.lower() in ('all', 'none')) \
        else (rf if isinstance(rf, str) else '2026-08-01')
    state_path = opt('--state') or os.path.join(ROOT, 'tmp', 'pia_missing_audit_state.json')
    out_path = opt('--out') or os.path.join(ROOT, 'tmp', 'grow_from_audit.txt')
    apply_ = '--apply' in ARGS

    idx = os.path.join(ROOT, 'index.html')
    h = open(idx, encoding='utf-8').read()
    m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
    EVENTS = json.loads(m.group(2))
    byid = {e['id']: e for e in EVENTS}

    state = json.load(open(state_path, encoding='utf-8'))
    tg, ambiguous, orphan = targets_from_state(state, EVENTS, rls_from, today, pma)

    only = opt('--ids')
    if isinstance(only, str):
        want = {int(x) for x in only.split(',') if x.strip()}
        tg = {k: v for k, v in tg.items() if k in want}
    ids = sorted(tg)
    lim = opt('--limit')
    if isinstance(lim, str):
        ids = ids[:int(lim)]

    log = ['取りこぼし取り込み（育成）  rls-from=%s  today=%s' % (rls_from, today), '']
    log.append('対象エントリ: %d 件' % len(ids))
    if ambiguous:
        log.append('')
        log.append('⚠️同名エントリが複数あるので自動対象外（どれを育てるか人が決める）: %d 組' % len(ambiguous))
        for kw, n, iid in ambiguous:
            log.append('   %s  未登録%d件  id=%s' % (kw, n, ','.join(str(x) for x in iid)))
    if orphan:
        log.append('')
        log.append('⚠️artist名に一致するエントリが無い（表記ゆれ）: %d 組' % len(orphan))
        for kw, n in orphan:
            log.append('   %s  未登録%d件' % (kw, n))
    log.append('')

    built_ok, skipped, warn = {}, [], []
    for i in ids:
        t = tg[i]
        ev = byid[i]
        cur = ev.get('tickets') or []
        urls = pia_urls(ev) + [u for u in t['new_urls'] if u not in pia_urls(ev)]
        log.append('=' * 72)
        log.append('id=%d  %s   ぴあURL %d本（既存%d + 新規%d）'
                   % (i, t['artist'], len(urls), len(pia_urls(ev)), len(t['new_urls'])))
        try:
            ne = bpe.build({'newid': i, 'artist': ev.get('artist', ''), 'urls': urls})
        except Exception as ex:
            log.append('  🚨 build 例外＝置換しない: %s %s' % (type(ex).__name__, str(ex)[:160]))
            skipped.append((i, 'build例外'))
            continue
        if ne is None:
            log.append('  🚨 買える枠ゼロで返ってきた＝置換しない（要目視）')
            skipped.append((i, '0枠'))
            continue

        kept = [x for x in cur if not is_pia_ticket(x)]
        newt = merge_tickets(ne['tickets'], cur)
        nd = pick_date(ne.get('date'), ev.get('date'), kept)
        log.append('  枠 %d → %d（うち非ぴあ据置 %d）' % (len(cur), len(newt), len(kept)))
        log.append('  千秋楽 %s → %s' % (ev.get('date'), nd))
        log.append('  会場 %s' % (ev.get('venue') or ''))
        log.append('    →  %s' % (ne.get('venue') or ''))
        log.append('  県   %s → %s' % (ev.get('prefecture'), ne.get('prefecture')))
        log.append('  日付表記 %s' % (ev.get('dateLabel') or ''))
        log.append('    →     %s' % (ne.get('dateLabel') or ''))
        log.append('  --- 今の枠 ---')
        for x in cur:
            log.append('    %s | date=%s start=%s%s'
                       % (x.get('type'), x.get('date'), x.get('startDate'),
                          '  [非ぴあ:据置]' if not is_pia_ticket(x) else ''))
        log.append('  --- 作り直した枠 ---')
        for x in ne['tickets']:
            log.append('    %s | date=%s start=%s' % (x.get('type'), x.get('date'), x.get('startDate')))
        if nd != ne.get('date'):
            warn.append((i, '千秋楽は非ぴあ枠のため今の値を維持'))

        lost = lost_pia_slots(ne['tickets'], cur)
        if lost:
            log.append('  🚨 消えるぴあ枠 %d件（売切/終了なら正しいが、ぴあの一過性の空ページの可能性もある）' % len(lost))
            for x in lost:
                log.append('      × %s | date=%s' % (x.get('type'), x.get('date')))
            if not ALLOW_DROP:
                log.append('  → 枠が消えるので自動適用しない（見てから --allow-drop で適用）')
                skipped.append((i, '消える枠あり(要目視)'))
                log.append('')
                continue

        built_ok[i] = {'tickets': newt, 'date': nd, 'dateLabel': ne.get('dateLabel'),
                       'venue': ne.get('venue'), 'prefecture': ne.get('prefecture')}
        log.append('')

    log.append('=' * 72)
    log.append('作り直せた: %d 件 / 見送り: %d 件' % (len(built_ok), len(skipped)))
    for i, why in skipped:
        log.append('   見送り id=%d  %s' % (i, why))
    for i, why in warn:
        log.append('   注意 id=%d  %s' % (i, why))

    if apply_ and built_ok:
        for i, v in built_ok.items():
            e = byid[i]
            e['tickets'] = v['tickets']
            e['date'] = v['date']
            if v['dateLabel']:
                e['dateLabel'] = v['dateLabel']
            if v['venue']:
                e['venue'] = v['venue']
            if v['prefecture']:
                e['prefecture'] = v['prefecture']
            e['verifiedAt'] = datetime.date.today().isoformat()
        stamp = datetime.date.today().strftime('%m%d')
        bak = os.path.join(ROOT, 'index.html.bak_%s_grow_audit' % stamp)
        open(bak, 'w', encoding='utf-8').write(h)
        new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
        open(idx, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
        raw = open(idx, 'rb').read()
        stray = raw.count(b'\n') - raw.count(b'\r\n')
        log.append('=== %d件 適用 (backup: %s) ===' % (len(built_ok), os.path.basename(bak)))
        log.append('孤立LF(CRLFでないLF) = %d  ※0でないと sort_guard が誤ブロックする' % stray)
        say('applied=%d  stray_lf=%d' % (len(built_ok), stray))
    else:
        log.append('=== 表示のみ。適用するなら --apply ===')

    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(log) + '\n')
    say('wrote %s  targets=%d built=%d skipped=%d ambiguous=%d orphan=%d'
        % (out_path, len(ids), len(built_ok), len(skipped), len(ambiguous), len(orphan)))
    return 0


def selftest():
    # is_pia_ticket: url無しはぴあ由来(links.pia経由)、pia.jpはぴあ、それ以外は守る
    assert is_pia_ticket({'type': 'a', 'date': 'd'}) is True
    assert is_pia_ticket({'url': 'https://t.pia.jp/pia/event/event.do?eventCd=1'}) is True
    assert is_pia_ticket({'url': 'https://eplus.jp/sf/detail/xxx'}) is False
    assert is_pia_ticket({'url': 'https://click.linksynergy.com/deeplink?...rakuten'}) is False

    # merge_tickets: 非ぴあ枠が消えない（これが消えると他の売り場が死ぬ）
    cur = [
        {'type': 'ぴあ一般', 'date': '2026-08-01'},
        {'type': 'e+先着', 'date': '2026-08-05', 'url': 'https://eplus.jp/sf/detail/x'},
    ]
    built = [{'type': 'ぴあ一般(新)', 'date': '2026-08-01'}, {'type': 'ぴあ追加', 'date': '2026-09-01'}]
    got = merge_tickets(built, cur)
    assert len(got) == 3, got
    assert got[-1]['type'] == 'e+先着', got
    assert not any(x['type'] == 'ぴあ一般' for x in got), got   # 古いぴあ枠は作り直しで消える

    # perf_key: 先行の回数違いを同じ公演として扱う（2次→3次で「消えた」と誤判定しない）
    assert perf_key('2次受付（岩手・宮城 10/25〜10/27公演）〜7/28 11:00') == '岩手・宮城 10/25〜10/27公演'
    assert perf_key('3次受付（岩手・宮城 10/25〜10/27公演）〜8/12 11:00') == '岩手・宮城 10/25〜10/27公演'
    assert perf_key('一般発売（北海道 9/28公演）〜9/27 23:59') == '北海道 9/28公演'
    assert perf_key('プリセール') == 'プリセール'

    # lost_pia_slots: 先行の回数違いは消えた扱いにせず、本当に無い公演だけ出す
    cur2 = [
        {'type': '2次受付（岩手・宮城 10/25〜10/27公演）〜7/28 11:00', 'date': '2026-07-28'},
        {'type': '一般発売（北海道 9/28公演）〜9/27 23:59', 'date': '2026-09-27'},
        {'type': 'e+先着（東京 12/1公演）', 'date': '2026-11-30', 'url': 'https://eplus.jp/sf/detail/x'},
    ]
    built2 = [
        {'type': '3次受付（岩手・宮城 10/25〜10/27公演）〜8/12 11:00', 'date': '2026-08-12'},
        {'type': '一般発売（千葉 11/8公演）9/4 10:00発売', 'date': '2026-09-04'},
    ]
    lost = lost_pia_slots(built2, cur2)
    assert len(lost) == 1, lost
    assert '北海道 9/28' in lost[0]['type'], lost      # 本物の消失だけ
    assert all('eplus' not in (x.get('url') or '') for x in lost)  # 非ぴあは対象外

    # pick_date: 遅い方を採る（非ぴあ枠だけが持つ後半公演を切らない）
    assert pick_date('2026-12-20', '2026-11-07', []) == '2026-12-20'
    assert pick_date('2026-11-07', '2026-12-20', []) == '2026-12-20'
    assert pick_date(None, '2026-11-07', []) == '2026-11-07'

    # norm_pia: 監査が返す ticket.pia.jp 形式を t.pia.jp 形式へ寄せる
    assert norm_pia('https://ticket.pia.jp/pia/event.do?eventCd=2628913') == \
        'https://t.pia.jp/pia/event/event.do?eventCd=2628913'
    assert norm_pia('https://ticket.pia.jp/pia/event.do?eventBundleCd=b2669204') == \
        'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669204'
    assert norm_pia('https://eplus.jp/x') is None

    # targets_from_state: 同名エントリが複数なら自動対象にしない
    class P:
        @staticmethod
        def in_scope(m, f, t):
            return True
    evs = [
        {'id': 1, 'artist': 'AA', 'links': {'pia': 'p?eventCd=1'}, 'tickets': []},
        {'id': 2, 'artist': 'BB', 'links': {'pia': 'p?eventCd=2'}, 'tickets': []},
        {'id': 3, 'artist': 'BB', 'links': {'pia': 'p?eventCd=3'}, 'tickets': []},
    ]
    st = {'results': {
        'AA': {'missing': [{'own_name': True, 'url': 'x?eventCd=111', 'rlsdate': '2026/08/05'}]},
        'BB': {'missing': [{'own_name': True, 'url': 'x?eventCd=222', 'rlsdate': '2026/08/05'}]},
        'CC': {'missing': [{'own_name': True, 'url': 'x?eventCd=333', 'rlsdate': '2026/08/05'}]},
        'DD': {'missing': [{'own_name': False, 'url': 'x?eventCd=444', 'rlsdate': '2026/08/05'}]},
    }}
    tgt, amb, orp = targets_from_state(st, evs, '2026-08-01', '2026-07-30', P)
    assert list(tgt) == [1], tgt                      # AAだけ自動対象
    assert amb and amb[0][0] == 'BB', amb             # BBは2エントリで曖昧
    assert orp and orp[0][0] == 'CC', orp             # CCは一致エントリ無し
    assert 'DD' not in [a[0] for a in amb] and 4 not in tgt   # 別名義は拾わない
    print('selftest OK (is_pia_ticket/merge_tickets/pick_date/norm_pia/targets_from_state)')


if __name__ == '__main__':
    sys.exit(main() or 0)
