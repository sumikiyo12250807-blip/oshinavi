# -*- coding: utf-8 -*-
"""ツアー割れスキャン（恒久ツール・投入前ゲート）。

チケットぴあからの機械収集で、同じツアーが
  「〜（倉敷公演）」「〜（下関公演）」「〜（東京公演）」…
のように **会場ごとに別エントリで投入されてしまう** 事故を投入前に検出する。

実例（2026-07-27 ユーザー発見）:
  ・五十嵐紅|ギターと静寂『クリスマス』（倉敷/下関/千葉/東京公演）の4件
  ・五十嵐紅トリオ|クリスマス 2026（大阪/東京/名古屋/福岡/みなとみらい公演）の5件

OSHINAVIの正ルール: ツアー・複数会場は1エントリにまとめ、各チケット枠に会場別URLを付ける
（正しい例: id1799 五十嵐紅|ギターと静寂『秋』= venue「全国ツアー（…）」+ tickets 3枠に別URL）。

【役割は検出と報告のみ】自動統合・書き込みは絶対にしない（統合/削除はユーザー確認を経る運用）。

使い方:
  python tools/tour_split_scan.py                  # index.html の EVENTS 全件
  python tools/tour_split_scan.py --new            # genre:"new" だけ（投入直後チェック）
  python tools/tour_split_scan.py --json built.json  # build結果JSON配列（投入前チェック・本命）
  python tools/tour_split_scan.py --selftest       # 自己テスト（ファイル/ネット不使用）

終了コード: 「⚠️統合候補」が1組でもあれば 1（投入パイプラインを止めるゲート）。無ければ 0。
"""
import argparse
import io
import json
import re
import sys
import unicodedata
from datetime import date

# Windowsコンソールでも文字化けしないよう標準出力をUTF-8に固定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------------------------
# 正規化
# ---------------------------------------------------------------------------

# 47都道府県（接尾の 都/道/府/県 を落とした形）。「［大阪］」のような裸の地域カッコ用
PREFS = {
    '北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島',
    '茨城', '栃木', '群馬', '埼玉', '千葉', '東京', '神奈川',
    '新潟', '富山', '石川', '福井', '山梨', '長野', '岐阜', '静岡', '愛知',
    '三重', '滋賀', '京都', '大阪', '兵庫', '奈良', '和歌山',
    '鳥取', '島根', '岡山', '広島', '山口',
    '徳島', '香川', '愛媛', '高知',
    '福岡', '佐賀', '長崎', '熊本', '大分', '宮崎', '鹿児島', '沖縄',
}

# NFKC後に残る/現れる開き・閉じカッコ（（）→() ［］→[] はNFKCで半角化される）
_OPEN = '([『「【〈《'
_CLOSE = ')]』」】〉》'
# 末尾の最内カッコ（中にカッコを含まない）＋その後ろに続く閉じカッコ群まで一致
# 『（東京公演）』のような二重カッコは、内側（…）とその後ろの』をまとめて消し、
# 残った開き『は呼び出し側で掃除する
_TRAIL_BRACKET = re.compile(
    r'[' + re.escape(_OPEN) + r']'
    r'([^' + re.escape(_OPEN + _CLOSE) + r']*)'
    r'[' + re.escape(_CLOSE) + r']'
    r'[' + re.escape(_CLOSE) + r'\s]*$'
)


def _is_venue_suffix(content: str) -> bool:
    """カッコの中身が「会場・地域を表す」ものか。

    ・「〜公演」「〜会場」で終わる（内側カッコは剥がして判定。『（東京公演）』対策）
    ・裸の都道府県名（例: 大阪 / 大阪府 / 北海道）
    """
    core = content.strip().strip(_OPEN + _CLOSE).strip()
    if not core:
        return False
    if core.endswith('公演') or core.endswith('会場'):
        return True
    if core == '北海道' or core in PREFS:
        return True
    if len(core) >= 2 and core[-1] in '都道府県' and core[:-1] in PREFS:
        return True
    return False


def normalize_name(name: str):
    """エントリ名から末尾の会場カッコを除いた正規化名を返す。

    戻り値: (正規化名, 会場カッコを1つ以上剥がしたか)
    正規化 = NFKC → 末尾会場カッコ除去（多重可）→ 空白除去 → 記号ゆれ吸収 → ASCII小文字化
    """
    s = unicodedata.normalize('NFKC', name or '')
    stripped = False
    while True:
        m = _TRAIL_BRACKET.search(s)
        if not m or not _is_venue_suffix(m.group(1)):
            break
        s = s[:m.start()].rstrip()
        s = s.rstrip(_OPEN)  # 二重カッコの外側開き（『 など）の残骸を掃除
        stripped = True
    s = re.sub(r'\s+', '', s)            # 空白（全角はNFKCで半角化済み）を除去
    s = s.replace('〜', '~')         # 波ダッシュ 〜 → ~（FF5EはNFKCで~になる）
    s = s.replace('・', '').replace('|', '').replace('｜', '')
    return s.lower(), stripped


# ---------------------------------------------------------------------------
# 判定
# ---------------------------------------------------------------------------

def _ticket_dates(e):
    """tickets[].date（販売終了日）のソート済みタプル。"""
    return tuple(sorted(t.get('date') or '' for t in e.get('tickets') or []))


def _show_dates_within(entries, days=90):
    """全エントリの公演日(date)が days 日以内に収まるか。欠損があれば False。"""
    ds = []
    for e in entries:
        try:
            ds.append(date.fromisoformat(e.get('date') or ''))
        except ValueError:
            return False
    return (max(ds) - min(ds)).days <= days


def classify_group(entries):
    """組を '候補'（⚠️統合候補）か '参考' に分類する。

    誤検知よけの追加条件（どちらかを満たせば候補）:
      A) 全エントリの tickets[].date（販売終了日）の組が全て同じ
      B) 全エントリの _piaSub が同じ（空でない）かつ 公演日が90日以内
    """
    tsets = {_ticket_dates(e) for e in entries}
    if len(tsets) == 1 and any(tsets):   # 全員同じ販売終了日構成（空同士は除く）
        return '候補'
    subs = {e.get('_piaSub') for e in entries}
    if len(subs) == 1 and next(iter(subs)) and _show_dates_within(entries):
        return '候補'
    return '参考'


def scan(events):
    """エントリ列からツアー割れ疑いの組を洗う。

    戻り値: (候補の組リスト, 参考の組リスト)。各組は (正規化名, [エントリ,...])。
    グループ化は正規化名の一致。ただし「会場カッコを剥がした子が1件も居ない組」は
    単なる同名重複（それは dup_scan.py の守備範囲）なので対象外。
    """
    groups = {}
    for e in events:
        key, stripped = normalize_name(e.get('name') or '')
        if not key:
            continue
        groups.setdefault(key, []).append((e, stripped))

    cands, refs = [], []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        if not any(stripped for _, stripped in members):
            continue  # 会場カッコ由来でない同名＝ツアー割れではない
        entries = [e for e, _ in members]
        (cands if classify_group(entries) == '候補' else refs).append((key, entries))
    cands.sort(key=lambda x: x[0])
    refs.sort(key=lambda x: x[0])
    return cands, refs


# ---------------------------------------------------------------------------
# 入出力
# ---------------------------------------------------------------------------

def load_events_from_index(path):
    """index.html から EVENTS 配列を取り出す（既存ツールと同方式・読むだけ／書き込み禁止）。"""
    # CRLF保護のため newline='' 必須（過去にnewline指定漏れで他ツールが壊れた事故あり）
    with open(path, encoding='utf-8', newline='') as f:
        src = f.read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    if not m:
        raise RuntimeError(f'{path}: const EVENTS が見つからないわ')
    return json.loads(m.group(2))


def print_group(key, entries):
    print(f'■ {key}（{len(entries)}件）')
    for e in entries:
        pia = (e.get('links') or {}).get('pia') or '-'
        print(f'   id={e.get("id")} {e.get("name")}')
        print(f'      公演日={e.get("date")} / {e.get("prefecture")} / {e.get("venue")}')
        print(f'      pia: {pia}')
    print()


def report(cands, refs, total, label):
    print(f'対象 {total} 件（{label}）\n')
    if cands:
        print('=== ⚠️統合候補（ツアー割れの疑い・1エントリに統合を検討） ===')
        for key, entries in cands:
            print_group(key, entries)
    if refs:
        print('=== 参考（名前は一致するが販売日/ジャンル/時期が揃わない組） ===')
        for key, entries in refs:
            print_group(key, entries)
    print(f'⚠️統合候補 {len(cands)}組 ／ 参考 {len(refs)}組')
    if cands:
        print('※ 統合・削除は自動でしない。ユーザー確認のうえ id1799 形式（venue=全国ツアー、各枠に会場別URL）へ。')
    return 1 if cands else 0


# ---------------------------------------------------------------------------
# 自己テスト（実ファイル・ネットワーク不使用）
# ---------------------------------------------------------------------------

def _mk(id_, name, show_date, ticket_dates, pia_sub='音楽/クラシック', pref='東京都'):
    return {
        'id': id_, 'name': name, 'artist': name, 'date': show_date,
        'prefecture': pref, 'venue': f'{pref}のどこかのホール', 'genre': 'new',
        '_piaSub': pia_sub,
        'links': {'pia': f'https://t.pia.jp/pia/event/event.do?eventCd=99{id_}'},
        'tickets': [{'type': '一般発売', 'date': d,
                     'url': f'https://t.pia.jp/pia/event/event.do?eventCd=99{id_}'} for d in ticket_dates],
    }


def selftest():
    ok = True

    def check(label, cond):
        nonlocal ok
        print(('  ○ ' if cond else '  × ') + label)
        ok = ok and cond

    # ケース1: 実例その1を模す。会場カッコ4件・販売終了日が全て同じ → 統合候補
    ev1 = [
        _mk(1, '五十嵐紅|ギターと静寂『クリスマス』（倉敷公演）', '2026-12-20', ['2026-12-19']),
        _mk(2, '五十嵐紅|ギターと静寂『クリスマス』（下関公演）', '2026-12-21', ['2026-12-19']),
        _mk(3, '五十嵐紅|ギターと静寂『クリスマス』（千葉公演）', '2026-12-23', ['2026-12-19']),
        _mk(4, '五十嵐紅|ギターと静寂『クリスマス』（東京公演）', '2026-12-24', ['2026-12-19']),
    ]
    c, r = scan(ev1)
    check('ケース1: ギターと静寂『クリスマス』4会場（同一販売終了日）→ 候補1組',
          len(c) == 1 and len(c[0][1]) == 4 and not r)

    # ケース2: 実例その2を模す。販売終了日はバラバラだが _piaSub 同一＋公演日90日以内 → 統合候補
    ev2 = [
        _mk(11, '五十嵐紅トリオ|クリスマス 2026（大阪公演）', '2026-12-05', ['2026-12-04']),
        _mk(12, '五十嵐紅トリオ|クリスマス 2026（東京公演）', '2026-12-10', ['2026-12-09']),
        _mk(13, '五十嵐紅トリオ|クリスマス 2026（名古屋公演）', '2026-12-12', ['2026-12-11']),
        _mk(14, '五十嵐紅トリオ|クリスマス 2026（福岡公演）', '2026-12-15', ['2026-12-14']),
        _mk(15, '五十嵐紅トリオ|クリスマス 2026（みなとみらい公演）', '2026-12-20', ['2026-12-19']),
    ]
    c, r = scan(ev2)
    check('ケース2: トリオ|クリスマス 2026 5会場（_piaSub同一・90日以内）→ 候補1組',
          len(c) == 1 and len(c[0][1]) == 5 and not r)

    # ケース3: 同アーティストでも別公演（『秋』と『バロック』）→ 検出しない
    ev3 = [
        _mk(21, '五十嵐紅|ギターと静寂『秋』', '2026-11-09', ['2026-11-08']),
        _mk(22, '五十嵐紅|ギターと静寂 特別公演『バロック』', '2026-11-05', ['2026-11-04']),
    ]
    c, r = scan(ev3)
    check('ケース3: 『秋』と『バロック』は別公演 → 0組', not c and not r)

    # ケース4: 名前は一致するが追加条件を満たさない（販売日バラバラ・_piaSub違い・公演日も遠い）→ 参考どまり
    ev4 = [
        _mk(31, '歌姫リサイタル（東京公演）', '2026-09-01', ['2026-08-31'], pia_sub='音楽/J-POP・ROCK'),
        _mk(32, '歌姫リサイタル（大阪公演）', '2027-03-01', ['2027-02-28'], pia_sub='音楽/演歌・邦楽'),
    ]
    c, r = scan(ev4)
    check('ケース4: 条件を満たさない同名組 → 候補0・参考1組', not c and len(r) == 1)

    # ケース5: 会場カッコでない末尾カッコ（（仮）/（完全版））は剥がさない → 検出しない
    ev5 = [
        _mk(41, '真夏のフェス（仮）', '2026-08-01', ['2026-07-31']),
        _mk(42, '真夏のフェス（完全版）', '2026-08-02', ['2026-07-31']),
    ]
    c, r = scan(ev5)
    check('ケース5: （仮）と（完全版）は会場カッコでない → 0組', not c and not r)

    # ケース6: 裸の県名カッコ ［大阪］＋二重カッコ『（東京公演）』も剥がせる → 統合候補
    ev6 = [
        _mk(51, '冬の音楽祭［大阪］', '2026-12-01', ['2026-11-30']),
        _mk(52, '冬の音楽祭『（東京公演）』', '2026-12-03', ['2026-11-30']),
    ]
    c, r = scan(ev6)
    check('ケース6: ［大阪］と『（東京公演）』→ 候補1組', len(c) == 1 and len(c[0][1]) == 2 and not r)

    # ケース7: 会場カッコの無い完全同名（表記違い重複はdup_scanの守備範囲）→ 本ツールでは0組
    ev7 = [
        _mk(61, '同名コンサート', '2026-10-01', ['2026-09-30']),
        _mk(62, '同名コンサート', '2026-10-01', ['2026-09-30']),
    ]
    c, r = scan(ev7)
    check('ケース7: 会場カッコ無しの同名重複は対象外 → 0組', not c and not r)

    print()
    print('selftest: ' + ('全ケース合格よ' if ok else '失敗があるわ'))
    return 0 if ok else 1


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='ツアー割れ（会場別エントリ分裂）スキャン。検出と報告のみ')
    ap.add_argument('--file', default='index.html', help='既定の読み込み元（読むだけ・書き込みしない）')
    ap.add_argument('--new', action='store_true', help='genre:"new" のエントリだけを対象にする')
    ap.add_argument('--json', dest='json_path', help='build結果のJSON配列を対象にする（投入前チェック用）')
    ap.add_argument('--selftest', action='store_true', help='自己テスト（ファイル/ネット不使用）')
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if args.json_path:
        with open(args.json_path, encoding='utf-8', newline='') as f:
            events = json.load(f)
        label = args.json_path
    else:
        events = load_events_from_index(args.file)
        label = args.file

    if args.new:
        events = [e for e in events if e.get('genre') == 'new']
        label += ' / genre:new のみ'

    cands, refs = scan(events)
    return report(cands, refs, len(events), label)


if __name__ == '__main__':
    sys.exit(main())
