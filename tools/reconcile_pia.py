# -*- coding: utf-8 -*-
"""【取りこぼし根絶＋表示保証の常設ゲート】登録済みエントリ ⇄ ぴあの今の実態 を機械照合する。

個別バグ(parse失敗/分類ミス/将来のぴあ仕様変更)を1つずつ潰すのではなく、
「最終データとぴあの“買える枠”を突合」して、どんな原因のドロップでも【出口で】炙り出す。

検出するもの:
  【枠の有無】
  - 🚨MISSING : ぴあに「買える枠(受付中/発売前)」があるのに登録tickets(未来分)に無い締切 = 取りこぼし
  - ⚠️DROP    : 修正版ビルダーでも parse_when が解析できない枠(=新しいぴあ表記。即対応要)
  - 💤STALE   : 登録にあるがぴあ側に対応する買える枠が無い(売切/終了/延長で日付ズレ)
  - ❌FETCH   : ぴあページ取得失敗
  【表示値の一致＝QC(2026-07-24 新設・e+の reconcile_eplus と同等の保証)】
  - ❌QC-TIME  : バッジの「〜M/D HH:MM」「M/D HH:MM発売」が実ページの窓と違う(時刻ズレを含む)
  - ❌QC-PREF  : バッジの県が実ページの県と違う
  - ❌QC-PERF  : バッジの公演日が実ページの公演日と違う
  - ❌QC-CAP   : 締切 > 公演日(公演日で締めるべき)
  - ❌QC-EVDATE: ev.date(千秋楽)が実際の公演より古い＝まだ買えるのにカードが画面から消える
  QCが1件でもあれば **exit 1**（投入/pushをブロックする）。

使い方:
  python tools/reconcile_pia.py --new            # genre:"new" の新着プールだけ(既定の推奨)
  python tools/reconcile_pia.py --ids 1240,1253  # 指定idだけ
  python tools/reconcile_pia.py --all            # links.piaがある全エントリ(重い)
  オプション: --limit N (先頭N件) / --quiet (問題ありだけ表示)

build_pia_entries.py の parse_cards/parse_when/mdbadge を再利用するので、ビルダーを直せば照合も自動で追従する。
朝ルーチン&新着レビュー前&push直前に通すのが運用ルール
(memory: feedback_harvest_status_by_class / feedback_deadline_extended_after_register / feedback_zero_error_pipeline)。
"""
import re, sys, json, time, datetime, importlib.util

# build_pia_entries は import時に sys.stdout をUTF-8でラップする。二重ラップを避けるため
# 自前ではラップせず、bpe を読み込んで stdout 設定を一本化する。
_spec = importlib.util.spec_from_file_location('bpe', __file__.replace('reconcile_pia.py', 'build_pia_entries.py'))
bpe = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(bpe)

TODAY = datetime.date.today().isoformat()
ARGS = sys.argv[1:]
def opt(name, default=None):
    if name in ARGS:
        i = ARGS.index(name)
        return ARGS[i + 1] if i + 1 < len(ARGS) and not ARGS[i + 1].startswith('--') else True
    return default

QUIET = '--quiet' in ARGS

def load_events(path='index.html'):
    h = open(path, encoding='utf-8').read()
    m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S)
    return json.loads(m.group(1))

def pia_urls(ev):
    """このエントリが参照する全ぴあURL(links.pia + 各ticket.url のうち event.do/ticketInformation)。"""
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p and 'pia' in p:
        urls.append(p)
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls:
            urls.append(u)
    return urls

def pia_buyable(urls):
    """ぴあURL群から買える枠を機械抽出 → [dict(iso,sd,suf,title,state,prefs,perfdate,perf_end)]。
    解析不能はdropsに。"""
    buyable, drops, errs = [], [], []
    seen = set()
    for u in urls:
        try:
            h = bpe.fetch(u)
        except Exception as ex:
            errs.append((u, str(ex)[:60])); continue
        # eventCd無効化/差し替え=「ご確認ください」エラーページ。0カードと区別して大声で出す
        # (2026-06-30 風輪のurlが朝有効→無効化。静かに0枠になり取りこぼす穴を塞ぐ)。
        if bpe.is_error_page(h):
            errs.append((u, '無効URL(ご確認ください)=eventCd削除/差替')); continue
        # 券種がw.pia.jp直販ページで出るイベントは t.pia.jp に券種カードが無い。0枠と読むと
        # 販売中を「ぴあ0枠」＝削除候補にしてしまう(2026-07-15 nobinobi 2026)。照合不能として出す。
        if bpe.wpia_only(h):
            errs.append((u, '🚨w.pia.jp直販形式=券種カード無し・機械照合不可(削除NG・目視必須)')); continue
        for r in bpe.parse_cards(h):
            if r['state'] not in ('受付中', '発売前'):
                continue
            suf, iso, sd = bpe.parse_when(r['state'], r['when'])
            # 🚨飛び先の売り場コードまで見て同一性を判定する。ツアーのまとめページは公演日を
            # 出さないカードがあり、締切と券種名だけで畳むと別会場の枠が消える
            # （2026-08-18 杉山清貴の福岡プレリザーブを「一致」と報告して見逃した）。
            key = (iso, r['title'], r['perfdate'], bpe.slot_code(r.get('url')))
            if key in seen:
                continue
            seen.add(key)
            if not iso:
                drops.append((r['state'], r['when'], r['title'][:40]))
            else:
                buyable.append({
                    'iso': iso, 'sd': sd, 'suf': suf, 'title': r['title'][:40], 'state': r['state'],
                    'prefs': r['prefs'], 'perfdate': r['perfdate'],
                    'perf_end': r.get('perf_end') or r['perfdate'],
                })
        time.sleep(0.25)
    return buyable, drops, errs


# 「ぴあ0枠」と出た時だけ間を空けて単独リトライする回数と待ち秒（--retries / --retry-wait）。
def _num(name, default):
    v = opt(name)
    if v in (None, True):
        return default
    return type(default)(v)

RETRIES = _num('--retries', 2)
RETRY_WAIT = _num('--retry-wait', 6.0)

# 登録の未来枠も0の子（＝削除候補）まで0枠リトライするか。
# --ids は削除判断の精密照合で使う経路なので既定でON（削除は不可逆＝安全側に倒す）。
# --new/--all は件数が多く全部リトライすると走査が実用外になるので、登録枠がある子だけ。
RETRY_EMPTY_REG = bool(opt('--ids')) or '--retry-empty' in ARGS


def fetch_buyable(urls, expect):
    """→ (buyable, drops, errs, tries)。**0枠と出た時だけ単独リトライ**する。

    【なぜ必要か】2026-07-28、49件を一括再照合したら「ぴあ買える0枠」の偽陽性が3件出た
    （climbgrow 3321／立川立飛 3324／キリン駐車券 3349）。実ページには全部枠があり、
    単独で回し直したら3件とも✅一致。しかも ❌FETCH は0件だったので
    [[reference_pia_rate_limit_429]] の「429が出ていないSTALEは本物」も成り立たなかった。
    ＝ぴあは連続アクセス時、例外も429も返さずに券種カードの無いページを返すことがある。
    放置すると翌朝「買える枠0＝死枠」として**生きている枠を削除候補に出す**。

    リトライは「ぴあ0枠×エラー無し」の時だけ＝全体を遅くせず危ない側だけ確かめる。
    登録枠も0の子（削除候補）は RETRY_EMPTY_REG が真の時だけ（--ids 経路＝既定ON）。
    ここを飛ばすと、一過性の空ページを「全枠死亡」と読んで**生きた枠ごと削除**しかねない。"""
    buyable, drops, errs = pia_buyable(urls)
    tries = 0
    while (not buyable) and (expect or RETRY_EMPTY_REG) and not errs and tries < RETRIES:
        tries += 1
        time.sleep(RETRY_WAIT * tries)      # 間隔を広げながら（1回目6秒→2回目12秒）
        buyable, drops, errs = pia_buyable(urls)
    return buyable, drops, errs, tries


# ============================================================================
# QC＝「バッジに出ている値が、ぴあの実ページの現在窓と一致する」ことの機械保証。
#
# 従来の reconcile は「締切"日付"の集合」しか突合しておらず、次が全部素通りだった:
#   ・締切の時刻ズレ（〜8/6 18:00 が 〜8/6 23:59 でもPASS）
#   ・発売時刻ズレ（8/8 10:00発売 が 12:00発売 でもPASS）
#   ・県違い／公演日違い（バッジの「（岩手 10/30公演）」が実ページと別）
#   ・締切 > 公演日 のcap逆転
#   ・ev.date(千秋楽)が実公演より古く、まだ買えるのにカードが画面から消える(2026-07-24 BOOP!型)
# e+側 reconcile_eplus.py と同じ「真値と比較」方式。比較は日付/機械生成文字列の == だけなので
# 端末の文字化けに一切依存しない（[[feedback_no_mojibake_japanese_read]]）。
# ============================================================================

def badge_split(ty):
    """type「券種（県 M/D公演）SUF」→ (pref_str, md_str, suf)。形が違えば(None,None,None)。
    ※SUFは build_pia_entries.parse_when が返す機械生成文字列（「〜8/9 23:59」「8/8 10:00発売」）。
      ここを丸ごと比較すれば締切日・締切時刻・発売日・発売時刻が一度に照合できる。"""
    m = re.search(r'（([^（）]*?)\s+([^（）]*?)公演）', ty or '')
    if not m:
        return (None, None, None)
    return m.group(1).strip(), m.group(2).strip(), ty[m.end():].strip()


# バッジの公演日部分。会場名などのプレフィックス（「シアタークリエ 8/8〜8/30」）は手修正で
# 意図的に足されるので許し、末尾の日付だけを比較する。略記(「9/5-13」)はここでマッチせずFAILになる
# ＝[[feedback_badge_date_full_form]]（完全M/D形）の違反として正しく検出される。
_MD_TAIL = re.compile(r'(?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R\d+年\s*)?\d{1,2}/\d{1,2})?$')


def qc_entry(ev, cards, reg, stat=None):
    """→ [(code, detail)]。codeは TIME/PREF/PERF/CAP/EVDATE(=FAIL) と BADGE(=情報)。

    stat(dict) を渡すと checked/skip/badge を数える。**照合できなかった枠を黙って飛ばすと
    「FAIL 0＝全部正しい」と読めてしまう**ので、カバレッジを必ず表に出すため。"""
    out = []
    matched_ends = []
    def bump(k):
        if stat is not None:
            stat[k] = stat.get(k, 0) + 1
    for t in reg:
        if 'eplus.jp' in (t.get('url') or ''):
            bump('eplus'); continue       # e+枠は reconcile_eplus.py の担当
        # 締切日+発売日が完全一致する枠が「ぴあ側にも登録側にも1つだけ」の時に限って照合する。
        # 同キーが複数ある（同じ締切で複数公演＝昼夜/連日）ときはどの枠がどのカードか確定できず、
        # 総当たりすると別公演のカードと突き合わせて公演日違いを誤報する
        # （2026-07-24 浜崎あゆみ石川＝10/17と10/18の2公演が同じ〜8/9締切で、ぴあ側に生きた
        #   カードが10/18の1枚しか無く、10/17枠がそれとマッチして「公演日違い」に見えた）。
        key = (t.get('date'), t.get('startDate') or None)
        cand = [c for c in cards if (c['iso'], c['sd'] or None) == key]
        same = [x for x in reg if (x.get('date'), x.get('startDate') or None) == key]
        if len(cand) != 1 or len(same) != 1:
            # 締切だけでは対が決まらない（連日/昼夜で同じ締切）。バッジの公演日で絞る。
            # 絞って1枚に定まればそれが対＝ここを飛ばすと同一ツアーの枠が丸ごと未照合になる
            # （2026-07-24 実測で新着50件の75枠中20枠が未照合だった）。
            _, md0, _ = badge_split(t.get('type'))
            mm0 = _MD_TAIL.search(md0 or '')
            md0 = mm0.group(0) if mm0 else None
            cand = [c for c in cand
                    if md0 and c['perfdate']
                    and bpe.mdbadge(c['perfdate'], c['perf_end'] or c['perfdate']) == md0]
            if len(cand) != 1:
                bump('skip'); continue    # 0件は既存のSTALEで報告済み
        c = cand[0]
        if c['perf_end']:
            matched_ends.append(c['perf_end'])
        pf, md, suf = badge_split(t.get('type'))
        if suf is None:
            # 統合バッジ等の手作りtypeはこの形でないことがある。FAILにはせず情報として出す。
            out.append(('BADGE', f"型が「券種（県 M/D公演）…」でない: {(t.get('type') or '')[:40]}"))
            bump('badge'); continue
        bump('checked')
        if suf != (c['suf'] or ''):
            out.append(('TIME', f"表示「{suf}」≠ ぴあ実窓「{c['suf']}」| {(t.get('type') or '')[:30]}"))
        # 県は「ぴあの県がバッジに載っているか」で見る。複数会場を1枠にまとめたバッジは
        # ぴあ1カードより多くの県を名乗るのが正しい（載せ落としだけが事故）。
        badge_pfs = set(x for x in re.split(r'[・/／]', pf or '') if x)
        if c['prefs'] and not set(c['prefs']) <= badge_pfs:
            out.append(('PREF', f"県「{pf}」にぴあの「{'・'.join(c['prefs'])}」が入っていない"
                                f"| {(t.get('type') or '')[:30]}"))
        if c['perfdate']:
            exp_md = bpe.mdbadge(c['perfdate'], c['perf_end'] or c['perfdate'])
            mm = _MD_TAIL.search(md or '')
            if (mm.group(0) if mm else None) != exp_md:
                out.append(('PERF', f"公演日「{md}」≠ ぴあ「{exp_md}」| {(t.get('type') or '')[:30]}"))
        pe = c['perf_end'] or c['perfdate']
        if pe and t.get('date') and t['date'] > pe:
            out.append(('CAP', f"締切{t['date']} > 公演日{pe}（公演日で締めるべき）| {(t.get('type') or '')[:30]}"))
    # (EVDATE) ev.date が実際の千秋楽より古いと、まだ買えるのにカードが画面から消える。
    # 判定は「このエントリが実際に売っている枠(=登録ticketと対応が取れたカード)」の公演日だけで行う。
    # cards全体で見ると、bundleページが他会場の公演も返すため1会場エントリが誤検知する
    # （2026-07-24 仮面ライダースーパーライブ宮崎公演＝bundleに全国公演が載っていた）。
    if matched_ends and (ev.get('date') or '') < max(matched_ends):
        out.append(('EVDATE', f"ev.date={ev.get('date')} が実公演の千秋楽{max(matched_ends)}より古い＝画面から消える"))
    return out


def selftest():
    """QCが「壊れたデータで確かにFAILを出す」ことを毎回確かめる（陽性テスト）。
    誤検知ゼロ(=全部PASS)だけ見ていると、実は何も検査していなくても気づけない。"""
    card = {'iso': '2026-08-09', 'sd': None, 'suf': '〜8/9 23:59', 'title': 'x', 'state': '受付中',
            'prefs': ['岩手'], 'perfdate': '2026-10-30', 'perf_end': '2026-10-30'}
    ev = {'id': 0, 'date': '2026-10-30'}
    ok = {'type': '一般発売（岩手 10/30公演）〜8/9 23:59', 'date': '2026-08-09'}
    assert qc_entry(ev, [card], [ok]) == [], qc_entry(ev, [card], [ok])
    def codes(t, e=ev, c=card):
        return [x[0] for x in qc_entry(e, [c], [t])]
    # ① 締切の時刻ズレ（日付は合っているので旧reconcileは素通りしていた本命）
    assert codes({**ok, 'type': '一般発売（岩手 10/30公演）〜8/9 18:00'}) == ['TIME']
    # ② 締切日そのもののズレ（suf比較で一緒に捕まる）
    assert codes({**ok, 'type': '一般発売（岩手 10/30公演）〜8/10 23:59'}) == ['TIME']
    # ③ 県違い
    assert codes({**ok, 'type': '一般発売（宮城 10/30公演）〜8/9 23:59'}) == ['PREF']
    # ④ 公演日違い
    assert codes({**ok, 'type': '一般発売（岩手 10/31公演）〜8/9 23:59'}) == ['PERF']
    # ⑤ 発売前の発売時刻ズレ
    pre = {'iso': '2026-08-08', 'sd': '2026-08-08', 'suf': '8/8 10:00発売', 'title': 'x', 'state': '発売前',
           'prefs': ['岩手'], 'perfdate': '2026-10-30', 'perf_end': '2026-10-30'}
    t_pre = {'type': '一般発売（岩手 10/30公演）8/8 12:00発売', 'date': '2026-08-08', 'startDate': '2026-08-08'}
    assert [x[0] for x in qc_entry(ev, [pre], [t_pre])] == ['TIME']
    # ⑥ cap逆転（締切 > 公演日）
    cap_c = {**card, 'iso': '2026-11-30', 'suf': '〜11/30 23:59'}
    cap_t = {'type': '一般発売（岩手 10/30公演）〜11/30 23:59', 'date': '2026-11-30'}
    assert [x[0] for x in qc_entry(ev, [cap_c], [cap_t])] == ['CAP']
    # ⑦ ev.dateが実公演より古い＝まだ買えるのにカードが画面から消える(BOOP!型)
    assert [x[0] for x in qc_entry({'id': 0, 'date': '2026-07-22'}, [card], [ok])] == ['EVDATE']
    # ⑧ 手修正で足した会場名プレフィックスは許す（「シアタークリエ 8/8〜8/30」）
    assert codes({**ok, 'type': '一般発売（岩手 メニコン 10/30公演）〜8/9 23:59'}) == []
    # ⑨ 略記の公演日は完全M/D形でないのでFAIL（[[feedback_badge_date_full_form]]）
    rng = {**card, 'perf_end': '2026-11-13'}
    assert [x[0] for x in qc_entry({'id': 0, 'date': '2026-11-13'}, [rng],
                                   [{**ok, 'type': '一般発売（岩手 10/30-13公演）〜8/9 23:59'}])] == ['PERF']
    # ⑩ 複数会場を1枠にまとめたバッジが、ぴあ1カードより多くの県を名乗るのは正しい
    assert codes({**ok, 'type': '一般発売（岩手・宮城 10/30公演）〜8/9 23:59'}) == []
    # ⑪ EVDATEは「登録枠と対応が取れたカード」だけで判定する（bundleの他会場公演で誤爆しない）
    other = {**card, 'iso': '2026-12-01', 'suf': '〜12/1 23:59',
             'perfdate': '2026-12-20', 'perf_end': '2026-12-20'}
    assert qc_entry(ev, [card, other], [ok]) == [], qc_entry(ev, [card, other], [ok])
    # ⑫ 同じ締切の登録枠が複数（連日公演）でも、公演日で対が1枚に定まるなら照合する。
    card31 = {**card, 'perfdate': '2026-10-31', 'perf_end': '2026-10-31'}
    two = [ok, {**ok, 'type': '一般発売（岩手 10/31公演）〜8/9 23:59'}]
    st = {}
    assert qc_entry({'id': 0, 'date': '2026-10-31'}, [card, card31], two, st) == []
    assert st.get('checked') == 2 and not st.get('skip'), st
    # ⑬ 公演日で絞っても対が決まらない時だけ未照合(skip)にする。別公演のカードと突き合わせて
    #    「公演日違い」を誤報しない（浜崎あゆみ石川＝10/17枠に対しぴあは10/18の1枚しか無い）。
    st2 = {}
    assert qc_entry(ev, [card], two, st2) == [], qc_entry(ev, [card], two)
    assert st2.get('checked') == 1 and st2.get('skip') == 1, st2
    # ⑬ e+枠は対象外（reconcile_eplusの担当）／ペアリング不能な枠は飛ばす
    assert qc_entry(ev, [card], [{**ok, 'type': 'ちがう', 'url': 'https://eplus.jp/sf/detail/1-P0'}]) == []
    assert qc_entry(ev, [card], [{**ok, 'date': '2026-09-09'}]) == []
    print('selftest OK: QC(TIME/PREF/PERF/CAP/EVDATE)は壊れたデータで確かにFAILを出す')
    selftest_retry()


def selftest_retry():
    """0枠リトライが「発動すべき時だけ発動し、2回目で枠を回収できる」ことを確かめる。
    （2026-07-28のSTALE偽陽性3件＝一括0枠→単独で一致、の再発防止）"""
    global pia_buyable, RETRY_WAIT, RETRY_EMPTY_REG
    real, real_wait, real_empty = pia_buyable, RETRY_WAIT, RETRY_EMPTY_REG
    RETRY_WAIT = 0.0                                   # テストは待たない
    RETRY_EMPTY_REG = False
    card = [{'iso': '2026-08-09', 'sd': None, 'suf': '〜8/9 23:59', 'title': 'x', 'state': '受付中',
             'prefs': ['岩手'], 'perfdate': '2026-10-30', 'perf_end': '2026-10-30'}]
    try:
        calls = {'n': 0}
        def flaky(urls):                               # 1回目だけ0枠を返す（ぴあの一過性の空ページ）
            calls['n'] += 1
            return (([], [], []) if calls['n'] == 1 else (card, [], []))
        pia_buyable = flaky
        b, _, _, tries = fetch_buyable(['u'], expect=1)
        assert b == card and tries == 1, (b, tries)    # ① 2回目で回収できる

        calls['n'] = 0
        pia_buyable = lambda urls: ([], [], [])
        b, _, _, tries = fetch_buyable(['u'], expect=1)
        assert b == [] and tries == RETRIES, tries     # ② 本物の0枠は上限まで試して0のまま

        pia_buyable = lambda urls: (card, [], [])
        _, _, _, tries = fetch_buyable(['u'], expect=1)
        assert tries == 0, tries                       # ③ 枠が取れた時は無駄打ちしない

        pia_buyable = lambda urls: ([], [], [])
        _, _, _, tries = fetch_buyable(['u'], expect=0)
        assert tries == 0, tries                       # ④ 登録枠0＋大量走査(--new/--all)では省略

        # ⑤ 削除候補(登録枠0)でも --ids 経路なら必ずリトライする＝生きた枠を消さないための本命
        RETRY_EMPTY_REG = True
        calls['n'] = 0
        pia_buyable = flaky
        b, _, _, tries = fetch_buyable(['u'], expect=0)
        assert b == card and tries == 1, (b, tries)
        RETRY_EMPTY_REG = False

        pia_buyable = lambda urls: ([], [], [('u', 'w.pia.jp直販')])
        _, _, _, tries = fetch_buyable(['u'], expect=1)
        assert tries == 0, tries                       # ⑥ FETCH/直販エラーは別の話＝リトライしない
    finally:
        pia_buyable, RETRY_WAIT, RETRY_EMPTY_REG = real, real_wait, real_empty
    print('selftest OK: 0枠リトライは「登録枠あり×エラー無し×0枠」の時だけ発動し2回目で回収する')


def main():
    if '--selftest' in ARGS:
        selftest(); return 0
    evs = load_events()
    if opt('--ids'):
        ids = set(int(x) for x in str(opt('--ids')).split(','))
        targets = [e for e in evs if e.get('id') in ids]
    elif '--new' in ARGS:
        targets = [e for e in evs if e.get('genre') == 'new']
    elif '--all' in ARGS:
        targets = [e for e in evs if pia_urls(e)]
    else:
        print('対象を指定して: --new / --ids a,b / --all'); return 2
    lim = opt('--limit')
    if lim:
        targets = targets[:int(lim)]

    print(f'=== reconcile_pia (today={TODAY}) 対象{len(targets)}件 ===\n')
    n_missing = n_drop = n_stale = n_err = n_ok = 0
    n_retried = n_rescued = 0     # 0枠リトライの発動回数／それで生き返った件数
    qc_fail = []          # (id, code, detail)
    stat = {}             # 照合カバレッジ（checked/skip/badge/eplus）
    for ev in targets:
        urls = pia_urls(ev)
        if not urls:
            continue
        # 登録tickets(未来締切のみ=今載ってるはずの枠)
        reg_all = [t for t in ev.get('tickets', []) if (t.get('date') or '') >= TODAY]
        # ぴあ以外の売り場を ticket.url で明示した枠(JFA公式直販/e+/ローチケ等)は、このゲートの
        # 守備範囲外。ぴあに無くて当たり前なので STALE/枠数不一致の判定から外す。
        # ただし黙って落とすと「照合したつもり」になるので件数は必ず表に出す
        # （2026-07-28 id3349 キリンチャレンジカップ＝試合本体がJFA直販・駐車券だけぴあ）。
        reg = [t for t in reg_all
               if not (t.get('url') or '') or 'pia.jp' in (t.get('url') or '')]
        n_other = len(reg_all) - len(reg)
        stat['other'] = stat.get('other', 0) + n_other
        # ぴあ側の実態を取得。0枠と出たら単独リトライ（偽陽性で生きた枠を殺さないため）。
        buyable, drops, errs, tries = fetch_buyable(urls, len(reg))
        if tries:
            n_retried += 1
            if buyable:
                n_rescued += 1
                print(f'    🔁RETRY id={ev["id"]} 一括では0枠→単独{tries}回目で{len(buyable)}枠を回収'
                      f'（0枠は偽陽性だった）')
            else:
                print(f'    🔁RETRY id={ev["id"]} 単独{tries}回試しても0枠（本物の可能性・要確認）')
        reg_dates = set(t.get('date') for t in reg)
        pia_dates = set(b['iso'] for b in buyable)
        missing = [b for b in buyable if b['iso'] not in reg_dates]   # ぴあにあるが登録に無い締切
        stale = [t for t in reg if t.get('date') not in pia_dates]    # 登録にあるがぴあに無い
        qc = qc_entry(ev, buyable, reg, stat) if buyable else []
        qc_bad = [q for q in qc if q[0] != 'BADGE']
        # STALE と 枠数不一致 も必ず表に出す（2026-06-26 839南佳孝/1313w.o.d.が「一致」表示で
        # 隠れてた反省。STALEは自動削除でなくWebFetch要確認のサイン）
        problem = bool(missing or drops or errs or stale or qc or len(reg) != len(buyable))
        if problem:
            tag = '❌' if qc_bad else ('🚨' if missing else ('💤' if stale else ('⚠️' if drops else '❌')))
            print(f'{tag} id={ev["id"]} {ev.get("artist","")[:30]} | 登録{len(reg)}枠 / ぴあ買える{len(buyable)}枠'
                  + (f' ／ ぴあ外{n_other}枠は対象外' if n_other else ''))
            for b in missing:
                print(f'    🚨MISSING ぴあに [{b["state"]}] {b["suf"]} ({b["iso"]}) があるが登録に無い | {b["title"]}')
                n_missing += 1
            for st, w, title in drops:
                print(f'    ⚠️DROP 解析不能 [{st}] when={w!r} | {title}'); n_drop += 1
            for u, e in errs:
                print(f'    ❌FETCH {e} | {u}'); n_err += 1
            for code, detail in qc:
                mark = 'QC-' + code
                print(f'    {"❌" if code != "BADGE" else "・"}{mark} {detail}')
                if code != 'BADGE':
                    qc_fail.append((ev['id'], code, detail))
            if stale and not QUIET:
                for t in stale:
                    print(f'    💤STALE 登録「{(t.get("type") or "")[:40]}」({t.get("date")}) がぴあの買える枠に無い'); n_stale += 1
        else:
            n_ok += 1
            if not QUIET:
                print(f'✅ id={ev["id"]} {ev.get("artist","")[:24]} | 登録{len(reg)}=ぴあ{len(buyable)} 一致'
                      + (f' ／ ぴあ外{n_other}枠は対象外' if n_other else ''))
    print(f'\n=== 集計: OK {n_ok} / 🚨MISSING {n_missing} / ⚠️DROP {n_drop} / 💤STALE {n_stale} / '
          f'❌FETCH {n_err} / ❌QC {len(qc_fail)} ===')
    # カバレッジ＝「QC 0」が“全部見て問題なし”なのか“そもそも見ていない”のかを必ず区別する。
    ck, sk, bd, ep = stat.get('checked', 0), stat.get('skip', 0), stat.get('badge', 0), stat.get('eplus', 0)
    tot = ck + sk + bd + ep
    print(f'=== QC照合カバレッジ: 照合できた枠 {ck}/{tot}' +
          (f' / 未照合 skip{sk}(同締切の枠が複数で対を確定できない)' if sk else '') +
          (f' badge{bd}(型が「券種（県 M/D公演）…」でない手作りバッジ)' if bd else '') +
          (f' e+{ep}(reconcile_eplusの担当)' if ep else '') + ' ===')
    if n_retried:
        print(f'=== 🔁0枠リトライ: 発動{n_retried}件 / うち{n_rescued}件は枠が復活（一括時の0枠は偽陽性）'
              f' / 残り{n_retried - n_rescued}件は単独でも0枠 ===')
    oth = stat.get('other', 0)
    if oth:
        print(f'=== ぴあ外の売り場を明示した枠 {oth}件は対象外（このゲートでは見ていない＝別途要確認） ===')
    if sk or bd:
        print('   ※未照合の枠は「正しい」と確認できていない枠。QC 0＝全部正しい、ではない。')
    if n_missing or n_drop:
        print('→ 🚨/⚠️ は取りこぼし。該当エントリをぴあ機械パースで枠追加して修正すること。')
    if qc_fail:
        cnt = {}
        for _, code, _ in qc_fail:
            cnt[code] = cnt.get(code, 0) + 1
        print('→ ❌QC＝バッジの表示が実ページと違う（' + ' / '.join(f'{k}{v}' for k, v in sorted(cnt.items())) + '）。')
        print('   投入/pushはブロック。該当を直してから再実行すること。')
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main() or 0)
