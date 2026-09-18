# -*- coding: utf-8 -*-
"""TIGETのハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形テンプレート）。

  python tools/build_tiget_entries.py tmp/tiget_yt_vt_0918.json --out tmp/built_tiget.json
  python tools/build_tiget_entries.py --selftest

## 売り状態の読み方（2026-09-18 に実ページの文言で確かめた対応表）

| 券種のclass                     | 画面の文言 | OSHINAVI |
|---------------------------------|-----------|----------|
| `is-available`                  | 事前支払い／当日会場払い | 買える |
| `is-available is-fewremaining`  | 〜 残りわずか | 買える |
| `is-unable is-unopened`         | **受付前** | 発売前（startDate==date==販売開始日） |
| `is-unable is-unavailable`      | **売切れ** | `soldout: true`（予定枚数終了） |
| `is-unable is-closed`           | **受付終了** | `soldout`＋`saleEnded`（販売終了） |
| `btn-unable`                    | 一般売切れ | 売切れ扱い |

🚨締切は**決済方法ごとに違う**（カード決済 10/17 23:59／コンビニ決済 10/14 23:59）。
   「最後に買えるのはいつか」なので**いちばん遅い終了日**で締める。

## 載せる条件（新規追加のとき）

- 公演日が今日以降
- **買える枠か受付前の枠が1つ以上ある**（全部が売切れ・受付終了だけのものは新規では載せない）
- 買える枠があるエントリの中の売切れ枠は**印を付けて残す**（feedback_soldout_keep_visible）
"""
import argparse
import datetime
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WD = '月火水木金土日'
# 🚨TIGETのカテゴリ → OSHINAVIのジャンル（**売り場の言う通りに機械で写す**＝人が判断する枠を作らない）
#   2026-09-18＝カテゴリを8つに広げたのに対応表が81/84しか無く、**1,906件が全部 youtuber の下書き**に
#   なっていた（投入前に気づいた）。カテゴリを足す時はここも足す。
CAT_GENRE = {
    '81': 'youtuber',     # YouTuber
    '84': 'vtuber',       # VTuber
    '29': 'idol',         # アイドル
    '45': 'fanevent',     # ショー／ファンイベント
    '46': 'talkshow',     # トークショー／講演会
    '41': 'anime',        # アニメ／ゲーム／声優 … ⚠️OSHINAVI側は anime(アニソン)/seiyuu(声優)/2.5ji に
                          #    分かれていて、TIGETの1カテゴリと1対1にならない。下書きは anime にしてユーザーに聞く
    '79': 'utaite',       # 歌い手  … 🆕OSHINAVIに無いジャンル（振り分け前にタブを作る）
    '80': 'vocaloid',     # ボカロ  … 🆕同じ
}
# 🆕まだ index.html にタブが無いジャンル＝振り分け（ユーザー確認後）の前に作る必要がある
GENRE_NEEDS_TAB = ('utaite', 'vocaloid')
LIVE = ('is-available',)
UNOPENED = 'is-unopened'
SOLDOUT = ('is-unavailable', 'btn-unable')
CLOSED = 'is-closed'


def state_of(cls):
    """券種のclassから売り状態を1語で返す。"""
    c = cls or ''
    if UNOPENED in c:
        return 'unopened'
    if CLOSED in c:
        return 'closed'
    if any(s in c for s in SOLDOUT):
        return 'soldout'
    if 'is-available' in c:
        return 'live'
    return 'unknown'


def md(iso):
    y, m, d = [int(x) for x in iso.split('-')]
    return '%d/%d' % (m, d)


def jp(iso):
    y, m, d = [int(x) for x in iso.split('-')]
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


def last_period(t):
    """券種の受付期間のうち、いちばん遅い終了日時を返す → (開始iso, 開始hm, 終了iso, 終了hm)"""
    ps = [p['parsed'] for p in (t.get('periods') or []) if p.get('parsed')]
    if not ps:
        return None
    return max(ps, key=lambda x: (x[2], x[3]))


# 🚨🚨2026-09-18 ユーザー決定＝**出す側の申込は載せない**
#   「入れないで　出す側は別　**推しに会いに行きたいがコンセプト**だから」
#   ＝同じフェスのページでも「自分が出店する／自分が参加する／自分が停める」ための申込は対象外。
#   ⚠️「全部載せる」（上のコンセプト）の**内側の線引き**＝推しに会いに行く券かどうかで決める。
#   ✅入れる＝チェキ撮影会（推しに会える）／物販付きチケット／配信視聴券
#   ⛔入れない＝グッズ委託販売のブース・即売会のスペース（出店料）／痛車・コスプレの参加エントリー／
#             駐車場・駐車券だけのページ／チケット先行案内登録（0円の登録）
SELLER_SIDE = re.compile(
    r'委託販売|即売会|出店|ブース(?:出展|申込)?|'          # 自分が売る側
    r'エントリーフォーム|参加エントリ|出場エントリ|'        # 自分が出る側
    r'駐車|'                                              # 停める側
    r'案内登録|先行案内'                                    # 0円の登録だけ
)


def is_seller_side(name):
    """「出す側」の申込ページか（＝推しに会いに行く券ではない）。"""
    return bool(SELLER_SIDE.search(name or ''))


_PAIRS = ('（）', '「」', '『』', '【】', '＜＞', '〔〕', '［］', '〈〉')


def _balanced(s):
    """開きカッコと閉じカッコの数がそろっているか（切り口がカッコの途中でないか）。"""
    return all(s.count(a) == s.count(b) for a, b in _PAIRS)


def ticket_name(raw):
    """券種名を整える。
    🚨TIGETは券種名の欄に「開場16:10/ 開演16:30/終演19:00予定」のような進行案内を書く主催者がいる
       （2026-09-18＝てらコワ6）。バッジに出すと意味が読めないので「チケット」に倒す。"""
    nm = (raw or '').strip()
    # 券種名にくっついた公演日の重複表記を落とす（「優先入場 2026年10月18日(日) 12:00開場」の後半）
    nm = re.sub(r'\s*\d{4}年\d{1,2}月\d{1,2}日.*$', '', nm).strip()
    # 🚨頭の「[9/28・19:00]」のような日付・時刻の札を落とす（2026-09-18＝12215・12897）。
    #    バッジには（9/28公演）が入るので重複だし、check_badges が「略記/半端範囲」として弾く。
    nm = re.sub(r'^[\[［][\d/・:：\s\-—〜~]+[\]］]\s*', '', nm).strip()
    if not nm:
        return 'チケット'
    if re.search(r'開場|開演|終演', nm):
        return 'チケット'
    # 🚨全角「／」と半角カッコは check_badges が「パース化け」として弾く（2026-09-18 id11381）。
    #    TIGETの主催者が書いた本物の券種名なので、記号だけそろえる。
    nm = (nm.replace('／', '・').replace('(', '（').replace(')', '）')
            .replace('[', '［').replace(']', '］'))
    # 🚨カッコの途中で切らない（【対象者様限定】…【特定クラ で不均衡になった＝id11384）。
    #    28字より短くても、元からカッコが閉じていない名前（TIGETの主催者が書きかけた形）があるので
    #    **長さに関係なく**そろうところまで戻す。
    cut = nm[:28]
    while cut and not _balanced(cut):
        cut = cut[:-1]
    # 🚨そろえた結果が空になる＝頭から開きカッコで始まって28字で閉じない名前
    #    （2026-09-18＝「［ナチュスク10周年記念！祝い＆応援して欲しいTシャツ&…」）。
    #    そのまま28字を返すとカッコ不均衡のまま出てしまうので「チケット」に倒す。
    return cut.rstrip('・、 /') if cut else 'チケット'


def sale_start(ev):
    """JSON-LD の offers から販売開始日時を取る。
    🚨全部のofferが同じ日のときだけ使う（食い違ったら発売日を書かない＝推測で日付を作らない）。
      2026-09-18 の実測＝95件中94件が全部同じ・食い違い0件・取れない1件。
    ⚠️offersの価格は手数料込み（券種5,500円→offers5,720円）なので価格での突合はしない。"""
    offs = [o for o in (ev.get('ld_offers') or []) if o.get('valid_from')]
    days = {o['valid_from'] for o in offs}
    if len(days) != 1:
        return None, None
    return offs[0]['valid_from'], offs[0].get('valid_from_time') or ''


def build(ev, today):
    if is_seller_side(ev.get('name')):
        return None, '出す側の申込（出店・参加エントリー・駐車・案内登録）'
    cats = ev.get('cats') or []
    genres = [CAT_GENRE[c] for c in cats if c in CAT_GENRE]
    dates = sorted({p['date'] for p in ev['programs'] if p.get('date')})
    future = [d for d in dates if d >= today]
    if not future:
        return None, '公演が終わっている'
    # 🚨主催者が作った試し書き・雛形が混ざる（2026-09-18＝公演名が「当日払い」で増上寺・2030/12/31、
    #    「コリコリ(対バン用)」で大和ハウス プレミストドーム・2032/9/20）。
    #    本物のチケットが2年以上先に売り出されることは無いので、そこで切る（載せると嘘になる）。
    limit = (datetime.date.fromisoformat(today) + datetime.timedelta(days=730)).isoformat()
    if future[0] > limit:
        return None, '公演日が2年より先＝主催者の試し書き・雛形の疑い'

    pref = ev.get('prefecture')
    ss_date, ss_time = sale_start(ev)
    tickets, has_live = [], False
    for p in ev['programs']:
        d = p.get('date')
        if not d or d < today:
            continue
        for t in p['tickets']:
            st = state_of(t.get('class'))
            per = last_period(t)
            nm = ticket_name(t.get('name'))
            # 🚨県が分からないイベントがある（主催者が住所を登録していない＝会場名にも一覧にも
            #    JSON-LDにも県が無い。2026-09-18 に7件）。会場名の市名から県を当てるのは推測なので
            #    **バッジから県を落とす**。カードには📍会場名が出るので場所は読める。
            head = f'{nm}（{pref} {md(d)}公演）' if pref else f'{nm}（{md(d)}公演）'
            if st == 'unopened':
                if not per:
                    continue                      # 受付前で開始日が読めない＝推測で日付を作らない
                tickets.append({'type': f'{head}{md(per[0])} {per[1]}発売'.rstrip(),
                                'date': per[0], 'startDate': per[0], 'url': ev['url']})
                has_live = True
            elif st == 'live':
                if per:
                    tickets.append({'type': f'{head}〜{md(per[2])} {per[3]}'.rstrip(),
                                    'date': per[2], 'url': ev['url']})
                    has_live = True
                elif ss_date:
                    # 🚨「当日支払い」の券種は受付期間の欄がHTMLに出ない＝**締切がどこにも書いていない**。
                    #    公演日を締切に流用するのは嘘（2026-09-09 ラフ×ラフで同じ型の事故）。
                    #    決まり（feedback_sale_end_unknown_display）＝発売日に「〜」を後ろ付けして
                    #    「販売中」で出し、date は画面から消えないための下限＝公演日にする。
                    tickets.append({'type': f'{head}{md(ss_date)} {ss_time}発売〜'.replace('  ', ' ').rstrip(),
                                    'date': d, 'startDate': ss_date,
                                    'saleEndUnknown': True, 'url': ev['url']})
                    has_live = True
            elif st in ('soldout', 'closed'):
                # 🚨受付期間が無い売切れ・受付終了もある（当日会場払いの券種など）。
                #    印は「予定枚数終了」「販売終了」なので締切は要らない＝**公演日を置き場にする**
                #    （バッジに「〜」は付けない＝締切を作らない）。2026-09-18 に4件を落としていた。
                tk = {'type': (f'{head}〜{md(per[2])} {per[3]}'.rstrip() if per else head),
                      'date': (per[2] if per else d), 'url': ev['url'], 'soldout': True,
                      'soldoutSince': today}
                if st == 'closed':
                    tk['saleEnded'] = True
                    tk['saleEndedSince'] = today
                tickets.append(tk)
    if not tickets:
        return None, '枠が読めない'
    # 🚨🚨2026-09-18 ユーザー決定＝**全部載せる**。
    #   「YouTubeのイベントは告知してからすぐ売ってる／告知して探す人が oshinavi.jp から
    #     見つけられればそれが私の目指すところ／特にカウントダウンがメインというわけではなく、
    #     推し活がしやすいを目指してるわけだから、**全部載せてほしい**」
    #   ＝売切れ・販売終了だけのイベントも、**公演がこれからなら**印を付けて載せる
    #   （[[feedback_soldout_keep_visible]]／[[feedback_saleended_vs_soldout]]と同じ扱い）。
    #   ⛔旧＝買える枠が1つも無ければ新規で載せない（10件を落としていた）

    perf = [x for x in (ev.get('performers') or []) if x]
    name = ev.get('name') or ''
    artist = '／'.join(perf[:3]) if perf else name
    if len(future) == 1:
        label = f'{jp(future[0])} {pref or ""}'.strip()
    else:
        label = f'{jp(future[0])}〜{jp(future[-1])} {pref or ""}'.strip()
    e = {
        'artist': artist,
        'name': name,
        'date': future[-1],
        'dateLabel': label,
        'venue': ev.get('venue') or '（会場未定）',
        'prefecture': pref or '',
        'genre': 'new',
        # 🚨カテゴリが対応表に無いまま既定値に落とすと、気づかずに全部同じジャンルになる。
        #    無いカテゴリは musicetc（その他＝最後の砦）に落として、報告で分かるようにする。
        '_genre': genres[0] if genres else 'musicetc',
        '_extraGenres': genres[1:],
        '_srcgenre': 'tiget:' + ','.join(cats),
        'price': None,
        # 🚨YouTuber・VTuberにはAmazonのCDリンクを付けない（feedback_entry_template_standard）
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'tiget': ev['url']},
        'tickets': tickets,
        'verified': True,
        'verifiedAt': today,
    }
    return e, None


CITY_SUFFIX = re.compile(r'\s*(?:in|In|IN|＜|<|〜|~|＠|@)\s*[^\s＞>]{1,12}(?:公演)?\s*[＞>]?\s*$')


def tour_key(e):
    """ツアーの束ね先を決める鍵＝（出演者, 会場名を落とした公演名）。
    🚨「『最』ライブツアー2026 in 大阪／in 仙台／in 福岡／in 宮古島」のように、
       TIGETは**会場ごとに別ページ**で売る。決まりは「ツアー・複数会場は1エントリ」
       （feedback_tour_consolidate）なので、ここで束ねて各枠に会場別URLを焼き込む
       （feedback_tour_per_ticket_url）。"""
    base = CITY_SUFFIX.sub('', e['name']).strip()
    if len(base) < 4 or base == e['name']:
        return None
    return (e['artist'], base)


def consolidate(entries):
    """同じツアーの別会場ページを1エントリに畳む。畳まないものはそのまま返す。"""
    groups, order, out = {}, [], []
    for e in entries:
        k = tour_key(e)
        if k is None:
            out.append(e)
            continue
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(e)
    for k in order:
        g = groups[k]
        if len(g) == 1:
            out.append(g[0])
            continue
        g.sort(key=lambda x: x['date'])
        base = dict(g[0])
        base['name'] = k[1]
        venues = []
        prefs = []
        tickets = []
        for e in g:
            if e['venue'] not in venues:
                venues.append(e['venue'])
            if e['prefecture'] and e['prefecture'] not in prefs:
                prefs.append(e['prefecture'])
            tickets += e['tickets']          # 枠には既に会場別のTIGET URLが入っている
        base['venue'] = ('全国ツアー（%s）' % '／'.join(venues)) if len(venues) > 1 else venues[0]
        base['prefecture'] = '・'.join(prefs)
        days = sorted({t['type'] for t in tickets})   # 参考（未使用）
        first, last = g[0]['date'], g[-1]['date']
        base['date'] = last
        base['dateLabel'] = (f'{jp(first)}〜{jp(last)} ' + '・'.join(prefs)).strip()
        base['tickets'] = tickets
        base['_merged_from'] = [e['links']['tiget'] for e in g]
        out.append(base)
    out.sort(key=lambda e: e['date'])
    return out


def _selftest():
    assert state_of('is-available') == 'live'
    assert state_of('is-available is-fewremaining') == 'live'
    assert state_of('is-unable is-unopened') == 'unopened'
    assert state_of('is-unable is-unavailable') == 'soldout'
    assert state_of('btn-unable') == 'soldout'
    assert state_of('is-unable is-closed') == 'closed'
    assert md('2026-10-18') == '10/18'
    assert jp('2026-10-18') == '2026年10月18日(日)'
    t = {'periods': [{'parsed': ['2026-09-13', '21:00', '2026-10-14', '23:59']},
                     {'parsed': ['2026-09-13', '21:00', '2026-10-17', '23:59']}]}
    assert last_period(t)[2] == '2026-10-17', last_period(t)
    ev = {'url': 'u', 'name': 'テスト', 'venue': 'ホール', 'prefecture': '大阪', 'cats': ['81'],
          'performers': ['もん'],
          'programs': [{'date': '2026-10-18', 'tickets': [
              {'name': '一般 2026年10月18日(日)　12:00開場', 'class': 'is-available',
               'periods': [{'parsed': ['2026-09-13', '21:00', '2026-10-17', '23:59']}]},
              {'name': 'VIP', 'class': 'is-unable is-closed',
               'periods': [{'parsed': ['2026-08-01', '10:00', '2026-09-01', '23:59']}]}]}]}
    ev['ld_offers'] = [{'price': 3720, 'valid_from': '2026-08-20', 'valid_from_time': '11:40'}]
    e, why = build(ev, '2026-09-18')
    assert e and e['_genre'] == 'youtuber', (e, why)
    assert e['tickets'][0]['type'] == '一般（大阪 10/18公演）〜10/17 23:59', e['tickets'][0]
    assert e['tickets'][1].get('saleEnded') is True
    assert e['links']['tiget'] == 'u' and 'amazon' not in e['links']
    # 🚨2026-09-18 ユーザー決定＝全部載せる。全部が受付終了でも**公演がこれからなら載せる**
    ev2 = json.loads(json.dumps(ev))
    ev2['programs'][0]['tickets'][0]['class'] = 'is-unable is-closed'
    e2, why2 = build(ev2, '2026-09-18')
    assert e2 and all(t.get('soldout') for t in e2['tickets']), (e2, why2)
    assert all(t.get('saleEnded') for t in e2['tickets']), e2['tickets']
    # 公演が終わっているものは載せない（ここは変えない）
    assert build(ev2, '2026-10-19')[0] is None
    # 受付期間が無い売切れも載せる＝公演日を置き場にして「〜」は付けない
    ev5 = json.loads(json.dumps(ev))
    ev5['programs'][0]['tickets'] = [{'name': '当日会場払い', 'class': 'is-unable is-unavailable', 'periods': []}]
    e5, _ = build(ev5, '2026-09-18')
    assert e5['tickets'][0]['type'] == '当日会場払い（大阪 10/18公演）', e5['tickets'][0]
    assert e5['tickets'][0]['date'] == '2026-10-18' and e5['tickets'][0]['soldout'] is True
    # 受付期間が無い（当日支払い）＝発売日に〜を後ろ付けして販売中・締切は作らない
    ev3 = json.loads(json.dumps(ev))
    ev3['programs'][0]['tickets'] = [{'name': '自由席', 'class': 'is-available', 'periods': []}]
    e3, _ = build(ev3, '2026-09-18')
    t3 = e3['tickets'][0]
    assert t3['type'] == '自由席（大阪 10/18公演）8/20 11:40発売〜', t3['type']
    assert t3['saleEndUnknown'] is True and t3['date'] == '2026-10-18' and t3['startDate'] == '2026-08-20', t3
    # 公演日が2年より先＝主催者の試し書き・雛形の疑い
    ev6 = json.loads(json.dumps(ev))
    ev6['programs'][0]['date'] = '2030-12-31'
    assert build(ev6, '2026-09-18')[0] is None, '2年より先を載せてしまう'
    ev7 = json.loads(json.dumps(ev))
    ev7['programs'][0]['date'] = '2028-09-01'          # 2年以内はふつうに載せる
    assert build(ev7, '2026-09-18')[0] is not None
    # offersのvalidFromが食い違うときは発売日を書かない＝その枠は載せない
    ev4 = json.loads(json.dumps(ev3))
    ev4['ld_offers'] = [{'valid_from': '2026-08-20'}, {'valid_from': '2026-09-01'}]
    assert build(ev4, '2026-09-18')[0] is None
    assert ticket_name('開場16:10/ 開演16:30/終演19:00予定（途中休憩あり）') == 'チケット'
    assert ticket_name('優先入場 2026年10月18日(日)　12:00開場') == '優先入場'
    assert ticket_name('') == 'チケット'
    # 出す側＝載せない
    for nm in ('☆VTuber様限定！ご本人様のグッズ委託販売&配布ブース',
               '第3回 ブイ×カケフェス VTuberグッズ即売会',
               '第三回 ブイ×カケ フェス Vtuberコスプレ&撮影参加エントリーフォーム',
               '痛車(四輪)エントリーフォーム＠第三回ブイ×カケフェス',
               'ブイ×カケ フェス 事前予約駐車場',
               'もののけフェス2026【チケット先行案内登録】'):
        assert is_seller_side(nm), nm
    # 推しに会いに行く券＝載せる（巻き添えで消さない）
    for nm in ('【特別企画】 花村きり チェキ撮影会', 'ブイ×カケ フェス ゲストレイヤーチェキ撮影会',
               '「最」ライブツアー2026 in 大阪', 'グッズ付きチケットのライブ',
               '【配信】おうちで見るワンマン', 'Torimochi virtual live vol.028 DAY-1'):
        assert not is_seller_side(nm), nm
    assert ticket_name('A／後方チケット(スタンディング)') == 'A・後方チケット（スタンディング）'
    assert ticket_name('[9/28・19:00] 入場整理券') == '入場整理券', ticket_name('[9/28・19:00] 入場整理券')
    assert ticket_name('［ナチュスク10周年記念！祝い＆応援して欲しいTシャツ&グッズ付きチケット］') == 'チケット'
    long = ticket_name('【対象者様限定】ファンミーティング参加チケット【特定クラスタ様向け】')
    assert _balanced(long) and long == '【対象者様限定】ファンミーティング参加チケット', long
    # ツアーを畳む
    def mk(nm, ven, pref, d, url):
        return {'artist': 'もん／立花萌香', 'name': nm, 'venue': ven, 'prefecture': pref,
                'date': d, 'dateLabel': '', 'links': {'tiget': url},
                'tickets': [{'type': f'一般（{pref} x公演）', 'date': d, 'url': url}]}
    g = consolidate([mk('「最」ライブツアー2026 in 大阪', 'J.Bridge', '大阪', '2026-10-18', 'u1'),
                     mk('「最」ライブツアー2026 in 仙台', 'ripple', '宮城', '2026-11-29', 'u2')])
    assert len(g) == 1 and g[0]['name'] == '「最」ライブツアー2026', g
    assert g[0]['venue'] == '全国ツアー（J.Bridge／ripple）' and g[0]['prefecture'] == '大阪・宮城'
    assert g[0]['date'] == '2026-11-29' and len(g[0]['tickets']) == 2
    assert {t['url'] for t in g[0]['tickets']} == {'u1', 'u2'}   # 枠ごとに会場別URL
    # 名前が同じでも会場の札が無いものは畳まない
    assert len(consolidate([mk('てらコワ6', 'a', '東京', '2026-11-21', 'u1'),
                            mk('別イベント', 'b', '東京', '2026-11-22', 'u2')])) == 2
    print('selftest OK: state_of/md/jp/last_period/sale_start/build/ticket_name/consolidate')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_tiget.json')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    a = ap.parse_args()
    d = json.load(open(a.src, encoding='utf-8'))
    out, skipped = [], []
    for ev in d['events']:
        e, why = build(ev, a.today)
        if e:
            out.append(e)
        else:
            skipped.append({'id': ev['id'], 'name': ev.get('name'), 'why': why, 'url': ev['url']})
    raw_n = len(out)
    out = consolidate(out)
    json.dump({'entries': out, 'skipped': skipped},
              io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'=== 組み上がり {len(out)}件（ツアーを畳む前 {raw_n}件）/ 載せない {len(skipped)}件 → {a.out} ===')
    why = {}
    for s in skipped:
        why[s['why']] = why.get(s['why'], 0) + 1
    for k, v in sorted(why.items(), key=lambda x: -x[1]):
        print(f'  {k}: {v}件')


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
