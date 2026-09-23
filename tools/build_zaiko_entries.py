# -*- coding: utf-8 -*-
"""ZAIKOのハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形テンプレート）。

  python tools/build_zaiko_entries.py tmp/zaiko_MMDD.json --out tmp/built_zaiko_MMDD.json
  python tools/build_zaiko_entries.py --selftest

## 売り状態の読み方（ZAIKOはブール値で明示される＝文言を読まなくていい）

| 券種のフラグ | OSHINAVI |
|---|---|
| `is_sold_out` ＋ `is_sale_ended`（**必ずセットで立つ**） | 先着＝`soldout`＋`saleEnded`（**販売終了**）／抽選＝`soldout`＋`presaleEnded`（**先行終了**） |
| 🚨「予定枚数終了」は**出さない** | ZAIKOのデータに「売り切れた」と名乗る根拠が無い（実ページも「抽選申込期間はすでに終了しています」「販売終了日 …」としか書かない） |
| `is_sale_started` が False | 発売前。🚨**開始日時がデータに無い**ので、日付を作らず載せない |
| どれでもない | 買える。締切は `lottery_end_date`（無ければ公演日を置き場＋`saleEndUnknown`） |

🚨**公演がこれからなら売切れ・販売終了でも載せる**（[[feedback_oshinavi_concept]]）。
   ⛔「買える枠が1つも無ければ載せない」は**失効ルール**＝2026-09-21にFANYで85件落とした反省。

## エントリの単位＝1イベント＝1エントリ
ZAIKOは1ページ＝1公演（`/ja/e/<slug>`）。飛び先は券種ごとに分かれないので、
**全券種に同じイベントURLを付ける**（それが実際の申込ページ）。
"""
import argparse
import collections
import datetime
import io
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

WD = '月火水木金土日'

# ZAIKOのジャンル名 → OSHINAVIのジャンル（**売り場の言う通りに機械で写す**
# ＝[[feedback_genre_pia_asis_and_other]]）。
# 🚨🚨2026-09-21＝**実データ461件の語彙55種類を数えてから書いた**（初版は推測で書いて34種類が
#   写せず、425件のうち272件が musicetc に落ちた＝その他は最後の砦なのに過半になった）。
#   ZAIKOの中身はクラブ系が主役（Techno 126・House 95・Trance 40・Electronic 71）。
#   ⚠️`event.genres` は**全件空**で、ジャンルは `performers[].genres` にしか入っていない。
# 🚨表に無いジャンルが来たら **写さずに数えて報告する**（黙って musicetc に倒さない）。
ZAIKO_GENRE = {
    # ── クラブ／DJ（2026-09-21 ユーザー「作って」でジャンルを新設した行き先）──
    'Techno': 'club', 'House': 'club', 'Electronic': 'club', 'Trance': 'club',
    'Psychedelic': 'club', 'Electro': 'club', 'Bass Music': 'club', 'Drum & Bass': 'club',
    'Disco': 'club', 'EDM': 'club', 'Dubstep': 'club', 'Ambient': 'club',
    'Tech House': 'club', 'Dance': 'club', 'HardStyle': 'club', 'Breaks': 'club',
    'Chill out': 'club', 'Dub': 'club', 'Lounge': 'club', 'Allmix': 'club',
    # ── 音楽 ──
    'Hip hop': 'hiphop', 'Trap': 'hiphop', 'Reggae': 'hiphop',
    'Idol': 'idol',
    'Pop': 'jpop', 'R&B': 'jpop', 'Soul': 'jpop', 'Funk': 'jpop',
    'Rock': 'rock', 'Alternative': 'rock', 'Indie': 'rock', 'Punk': 'rock',
    'Metal': 'rock', 'Visual': 'rock',
    'Jazz': 'jazz', 'Classical': 'classic',
    'K-POP': 'kpop', 'Asian': 'yougaku',
    'Anime': 'anime', 'Anime & Manga': 'anime', 'VTuber': 'vtuber',
    'Acoustic': 'musicetc', 'Folk': 'musicetc', 'Crossover': 'musicetc',
    'Instrumental': 'musicetc', 'Noise': 'musicetc', 'Music': 'musicetc',
    'Others': 'musicetc',
    # ── 音楽以外 ──
    'Comedy': 'owarai', 'Wrestling': 'sports', 'Art & Design': 'art',
    # 2026-09-23追加＝夜の収集と番人が「表に無い」と報告した分。
    #   海外の音楽は [[feedback_kaigai_is_area]]＋ぴあの「民族音楽→yougaku」に合わせて yougaku へ。
    'Sports & Fitness': 'sports', 'Body building': 'sports',
    'Esports': 'sports', 'Soccer': 'sports', 'Sumo': 'sports',
    'Goth': 'rock',
    'African': 'yougaku', 'Afrobeats': 'yougaku', 'Latin': 'yougaku',
    'Soca': 'yougaku', 'Oldies': 'yougaku',
    'Owarai': 'owarai', 'Food & Drink': 'gourmet',
    'Culture': 'event', 'Culture & Subculture': 'event',
    # ⛔写さない＝ジャンルではなく「形式」の札。'Live'（78回）は生演奏という意味で、
    #   これを何かのジャンルに倒すと嘘になる。件数は多いが**無視するのが正しい**。
    'Live': None,
    # ⛔🆕2026-09-23＝`Japanese music` も写さない（旧 hougaku は取り消し）。
    #   これは「日本の音楽」という**大分類**で、和楽器(hougaku)の意味ではない
    #   （実例＝SunSet Swish は `Japanese music, Rock` のJ-ROCKバンド／
    #    有弦無限は `Japanese music` ＋出演者 `Metal, Anime`）。
    #   TIGETの31「邦楽」が日本のポップスを指すのと同じ罠（[[feedback_kpop_vs_yougaku]]の隣）。
    #   写さずに落とせば、細分（Rock/Metal/Anime）が付いていればそちらが効き、
    #   何も無ければ musicetc＝その他の砦に落ちる。どちらも嘘にならない。
    'Japanese music': None,
}
GENRE_FALLBACK = 'musicetc'

# 🚨一覧のカテゴリ → ジャンル（**出演者のジャンルが空のときの受け皿**）。
#   2026-09-21 実測＝461件のうち**269件は performers[].genres が空**（ZAIKOは任意入力らしい）。
#   そのまま musicetc に落とすと「その他」が過半になる（＝[[feedback_genre_pia_asis_and_other]]の
#   「その他は最後の砦」に反する）。カテゴリは**売り場が分類した事実**なので写してよい。
CAT_GENRE = {
    'clubs-nightlife': 'club',
    'performances-shows': 'engeki',
    'festivals-fairs': 'fes',
    'tournaments-competitions': 'sports',
    'concerts-live-music': 'musicetc',   # 音楽だがZAIKOに細分が無い＝ここだけ「その他」
}

PREF47 = ('北海道 青森県 岩手県 宮城県 秋田県 山形県 福島県 茨城県 栃木県 群馬県 埼玉県 千葉県 東京都 '
          '神奈川県 新潟県 富山県 石川県 福井県 山梨県 長野県 岐阜県 静岡県 愛知県 三重県 滋賀県 京都府 '
          '大阪府 兵庫県 奈良県 和歌山県 鳥取県 島根県 岡山県 広島県 山口県 徳島県 香川県 愛媛県 高知県 '
          '福岡県 佐賀県 長崎県 熊本県 大分県 宮崎県 鹿児島県 沖縄県').split()

SELLER_SIDE = re.compile(
    r'委託販売|即売会|出店|ブース(?:出展|申込)?|'
    r'エントリーフォーム|参加エントリ|出場エントリ|'
    r'駐車|案内登録|先行案内'
)

_PAIRS = ('（）', '「」', '『』', '【】', '＜＞', '〔〕', '［］', '〈〉')


def era(y):
    return 'R%d年 ' % (y - 2018) if y > datetime.date.today().year else ''


def md(iso):
    """公演日のバッジ用＝翌年以降は令和略記を付ける（[[feedback_r9_year_notation]]）。"""
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return '%s%d/%d' % (era(y), m, d)


def mdp(iso):
    """締切用＝**年を付けない**。既存21,898枠を数えて確かめた流儀＝
    公演日（カッコの中）にはR9年を付け、締切（カッコの後の〜）には付けない。
    ここを md() にすると「〜R9年 2/1 23:59」になって既存と食い違う（2026-09-21）。"""
    return '%d/%d' % (int(iso[5:7]), int(iso[8:10]))


def jp(iso, extra=''):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    s = '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])
    return (s + ' ' + extra).strip() if extra else s


def perf_dt_of(t, base_date):
    """券種の `override_datetime_period`（「11月09日 (月) 19:00 – 終了時間未定」）から
    **その券種の公演日と開演時刻**を読む。年は入っていないので base_date（イベントの公演日）の年を使い、
    月日が base より前なら翌年と見る（年末年始のまたぎ）。取れなければ (None, None)。
    🚨これを読まないと、1ページに複数公演あるページで全部イベントの初日になる（2026-09-21）。"""
    s = t.get('perf_dt') or ''
    m = re.search(r'(\d{1,2})月(\d{1,2})日[^\d]*(?:(\d{1,2}):(\d{2}))?', s)
    if not m:
        return None, None
    y = int(base_date[:4])
    mo, dy = int(m.group(1)), int(m.group(2))
    if (mo, dy) < (int(base_date[5:7]), int(base_date[8:10])):
        y += 1
    try:
        d = datetime.date(y, mo, dy).isoformat()
    except ValueError:
        return None, None
    hm = '%d:%s' % (int(m.group(3)), m.group(4)) if m.group(3) else None
    return d, hm


def pref_of(det, listrow):
    """県。①会場の location「東京都, 日本」 ②一覧の pref ③住所 の順。無ければ空。"""
    for src in ((det or {}).get('venue_location'), (listrow or {}).get('pref'),
                (det or {}).get('venue_address')):
        for n in PREF47:
            if n in (src or ''):
                return n if n == '北海道' else n[:-1]
    return ''


def _balanced(s):
    return all(s.count(a) == s.count(b) for a, b in _PAIRS)


def ticket_name(raw, is_lottery, is_stream):
    """券種名を整える。空なら「チケット」。抽選・配信は分かるように添える。"""
    nm = re.sub(r'\s+', ' ', (raw or '')).strip()
    nm = re.sub(r'^[●○◆■▲☆★]+', '', nm).strip()
    nm = re.sub(r'\s*\d{4}年\d{1,2}月\d{1,2}日.*$', '', nm).strip()
    if not nm:
        nm = '抽選チケット' if is_lottery else 'チケット'
    nm = (nm.replace('／', '・').replace('(', '（').replace(')', '）')
            .replace('[', '［').replace(']', '］'))
    if is_stream and '配信' not in nm:
        nm = nm + '（配信）'
    cut = nm[:28]
    while cut and not _balanced(cut):
        cut = cut[:-1]
    return cut.rstrip('・、 /') if cut else 'チケット'


def artist_of(det, listrow):
    """出演者の先頭3組。取れなければイベント名。"""
    names = [(p.get('name') or '').strip() for p in ((det or {}).get('performers') or [])]
    names = [n for n in names if n and not re.fullmatch(r'ほか|他|など|MC|ゲスト', n)]
    if names:
        return '／'.join(names[:3])
    return ((det or {}).get('name') or (listrow or {}).get('title') or 'ZAIKO').strip()


def genres_of(det, unknown, cat=None):
    """ジャンルを写す。**出演者のジャンル → イベントのジャンル** の順。未知は数えて報告。
    🚨🆕2026-09-23に順番を入れ替えた。それまではイベント側が先だったが、
       イベント側は1件も読めていなかった（ハーベスタが dict を list として回していた）ので
       実質「出演者だけ」で動いていた。ハーベスタを直した今、イベント側を先にすると
       **出演者に付いた強い札（VTuberなど）がイベント側の広い札に負ける**
       （実例＝20938 藍海のん＝出演者 VTuber／イベント Alternative,Pop,Rock）。
       具体的な出演者側を先に読み、イベント側は足りない分を補う形にする。"""
    got = []
    for p in ((det or {}).get('performers') or []):
        for g in (p.get('genres') or []):
            if g in ZAIKO_GENRE:
                if ZAIKO_GENRE[g]:
                    got.append(ZAIKO_GENRE[g])
            elif g:
                unknown[g] += 1
    for g in ((det or {}).get('genres') or []):
        if g in ZAIKO_GENRE:
            if ZAIKO_GENRE[g]:
                got.append(ZAIKO_GENRE[g])
        elif g:
            unknown[g] += 1
    if not got and cat in CAT_GENRE:
        got.append(CAT_GENRE[cat])       # 出演者のジャンルが空＝一覧のカテゴリで補う
    return list(dict.fromkeys(got))


def build_one(listrow, det, today, unknown):
    """1イベント＝1エントリ。載せられないときは (None, 理由)。"""
    name = re.sub(r'\s+', ' ', (det or {}).get('name') or listrow.get('title') or '').strip()
    if SELLER_SIDE.search(name):
        return None, '出す側の申込（出店・参加エントリー・駐車・案内登録）'
    # 🚨2026-09-24 一覧の日付（tags の countdown）は**公演日とは限らない**＝AKB48劇場・雨模様のソラリスなどで
    #   締切側の日付が入っていた（2027/1 の公演が「9/24公演」で登録され、翌朝の削除に乗るところだった）。
    #   個別ページの display_date_period.start（画面の「開演」）を優先し、無い時だけ一覧の日付を使う。
    dp = ((det or {}).get('display_date_period') or {}).get('start') or {}
    d = dp.get('date_string') or listrow.get('date')
    if not d:
        return None, '公演日が取れない'
    if d < today:
        return None, '公演が終わっている'
    limit = (datetime.date.fromisoformat(today) + datetime.timedelta(days=730)).isoformat()
    if d > limit:
        return None, '公演日が2年より先＝試し書きの疑い'
    if not det:
        return None, '個別ページが読めなかった（券種が分からない）'

    pref = pref_of(det, listrow)
    # 🚨**「00:00」は開演時刻ではない**＝ZAIKO側が時刻を入れていないだけ。
    #   バッジに「10/14 00:00公演」と出すと**書いていない時刻を書く**ことになる
    #   （2026-09-21 エージェントの指摘＝24件がこの形だった）。
    stime = (dp.get('time_string') if dp.get('date_string') else '') or listrow.get('time') or ''
    if stime in ('00:00', '0:00'):
        stime = ''
    venue = re.sub(r'\s+', ' ', (det.get('venue_name') or listrow.get('venue') or '')).strip()
    url = listrow['url']
    when = '%s %s公演' % (md(d), stime) if stime else '%s公演' % md(d)

    tickets, has_live = [], False
    tks = det.get('tickets') or []
    names = [ticket_name(t.get('name'), t.get('is_lottery'), t.get('is_stream')) for t in tks]
    for i, t in enumerate(tks):
        if SELLER_SIDE.search(t.get('name') or ''):
            continue
        # 🚨券種ごとに公演日時が書いてあるなら**その枠はその日の公演**として出す
        #   （1ページに複数公演・複数会場を詰めるページがある）
        t_d, t_hm = perf_dt_of(t, d)
        if t_d:
            when_t = '%s %s公演' % (md(t_d), t_hm) if t_hm and t_hm not in ('0:00',) else '%s公演' % md(t_d)
        else:
            when_t, t_d = when, d
        nm = names[i]
        if names.count(nm) > 1:
            # 🚨同じ券種名が並ぶと**画面で見分けられない**（ZAIKOは券種名が空の枠が
            #   1,066/1,267枠＝ほとんど「チケット」に倒れる）。
            #   値段が違うなら**値段を添える**＝ページに書いてある本物の情報で見分ける
            #   （TIGET・FANYのビルダーと同じ流儀）。値段まで同じなら番号で分ける。
            prices = [(x.get('price') or '').strip() for x in tks]
            same = {prices[j] for j, n2 in enumerate(names) if n2 == nm}
            if len(same) > 1 and prices[i]:
                nm = '%s %s' % (nm, prices[i])
            else:
                nm = '%s（%d）' % (nm, names[:i].count(nm) + 1)
        head = '%s（%s %s）' % (nm, pref, when_t) if pref else '%s（%s）' % (nm, when_t)
        ed, edt = t.get('end_date'), t.get('end_time')
        if t.get('is_sold_out') or t.get('is_sale_ended'):
            tk = {'type': ('%s〜%s %s' % (head, mdp(ed), edt or '')).rstrip() if ed else head,
                  'date': ed or t_d, 'url': url, 'soldout': True, 'soldoutSince': today}
            # 🚨🚨ZAIKOは **is_sold_out と is_sale_ended を必ずセットで立てる**（実測＝片方だけは0枠）。
            #   ＝フラグからは「売り切れた」のか「期間が終わっただけ」なのか**区別できない**。
            #   実ページの文字を見たら（div-official /ja/item/381246）、
            #     抽選の枠＝「**抽選申込期間はすでに終了しています**」
            #     先着の枠＝「販売終了日 …」
            #   ＝**売り切れとは書いていない**。なのに「予定枚数終了」と出すのは嘘になる
            #   （[[feedback_no_fake_info]]／[[feedback_saleended_vs_soldout]]）。
            #   ✅**抽選の枠＝先行終了（presaleEnded）／先着の枠＝販売終了（saleEnded）**にする。
            #   「予定枚数終了」はZAIKOでは**出さない**（売り切れを名乗る根拠がデータに無い）。
            if t.get('is_lottery'):
                tk['presaleEnded'] = True
            else:
                tk['saleEnded'] = True
                tk['saleEndedSince'] = today
            tickets.append(tk)
        elif t.get('is_lottery') and ed and ed < today:
            # 🚨2026-09-22 抽選の申込が終わったあと、当選者の支払い期間（on_sale_until）の間は
            #   ZAIKOが is_sold_out も is_sale_ended も立てない（天川はの・おかしばのしゃべり場で実測）。
            #   申込はもうできない＝買える枠ではない。印が無いと締切が過去の枠だけ残って
            #   「カードは出るのに買える枠0」になる（check_zero_badge で発覚）。上と同じく先行終了にする。
            tickets.append({'type': ('%s〜%s %s' % (head, mdp(ed), edt or '')).rstrip(),
                            'date': ed, 'url': url, 'soldout': True, 'soldoutSince': today,
                            'presaleEnded': True})
        elif not t.get('is_sale_started'):
            # 🚨2026-09-21に直した＝**発売開始日時はデータにある**（先着は on_sale_from、
            #   抽選は lottery_start_date）。初版は lottery_end_date だけ見ていて、
            #   受付前153枠を「日付が無い」と判断して落としていた。
            #   開始日が**今日以降のときだけ**載せる（過去の開始日は別の理由でまだ始まっていない形＝
            #   推測で日付を作らないので触らない）。
            sd, sdt = t.get('start_date'), t.get('start_time')
            if not sd or sd < today:
                continue
            tickets.append({'type': ('%s%s %s発売' % (head, md(sd), sdt or '')).rstrip(),
                            'date': sd, 'startDate': sd, 'url': url})
            has_live = True
        else:
            if ed:
                end, endt = ed, edt
                # 締切が公演日より後なら公演日で締める（配信・視聴は例外）
                if end > t_d and not re.search(r'配信|視聴|アーカイブ', nm):
                    end, endt = t_d, ''
                tickets.append({'type': ('%s〜%s %s' % (head, mdp(end), endt or '')).rstrip(),
                                'date': end, 'url': url})
            else:
                # 締切がどこにも書かれていない＝締切を作らず公演日を置き場にする
                tickets.append({'type': '%s販売中' % head, 'date': t_d,
                                'saleEndUnknown': True, 'url': url})
            has_live = True

    if not tickets:
        return None, '載せられる枠が無い'

    seen, uniq = set(), []
    for t in tickets:
        k = (t.get('type'), t.get('date'), t.get('url'), bool(t.get('soldout')),
             bool(t.get('saleEnded')), bool(t.get('saleEndUnknown')))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(t)

    gs = genres_of(det, unknown, listrow.get('cat')) or [GENRE_FALLBACK]
    return {
        'id': None,
        'artist': artist_of(det, listrow),
        'name': name,
        'date': d,
        'dateLabel': jp(d, ('%s開演' % stime) if stime else ''),
        'venue': venue,
        'prefecture': pref,
        'genre': 'new',
        '_genre': gs[0],
        '_extraGenres': gs[1:],
        '_srcgenre': 'zaiko:%s' % ','.join((det.get('genres') or []) or ['?']),
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'zaiko': url},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
        '_has_live': has_live,
    }, None


def build_all(path, out_path, today):
    d = json.load(io.open(path, encoding='utf-8'))
    det = d.get('details') or {}
    unknown = collections.Counter()
    built, why = [], collections.Counter()
    for r in d.get('list') or []:
        e, reason = build_one(r, det.get(r['url']), today, unknown)
        if e:
            built.append(e)
        else:
            why[reason] += 1
    live = sum(1 for e in built if e.pop('_has_live', False))
    with io.open(out_path, 'w', encoding='utf-8') as f:
        json.dump(built, f, ensure_ascii=False, indent=1)
    print('組めた %d件（うち買える枠あり %d件）/ 一覧 %d件 → %s'
          % (len(built), live, len(d.get('list') or []), out_path))
    print('枠 %d枠' % sum(len(e['tickets']) for e in built))
    for k, n in why.most_common():
        print('  載せなかった: %-44s %d件' % (k, n))
    if unknown:
        print('🚨表に無いジャンル（写せなかった）: %s' % dict(unknown))
    print('  ジャンル: %s' % dict(collections.Counter(e['_genre'] for e in built)))
    return 0


def _selftest():
    today = '2026-09-21'
    unk = collections.Counter()
    lr = {'url': 'https://akb48.zaiko.io/ja/e/2026-1001', 'title': '10月1日公演',
          'date': '2026-10-01', 'time': '19:00', 'venue': 'AKB48劇場', 'pref': '東京都',
          'cat': 'concerts-live-music'}

    def mk(tickets, **kw):
        d = {'name': '10月1日公演', 'venue_name': 'AKB48劇場',
             'venue_location': '東京都, 日本', 'venue_address': '東京都千代田区',
             'genres': ['Idol'], 'performers': [{'name': '岩立沙穂', 'genres': ['Idol']},
                                                {'name': '柏木由紀', 'genres': ['Idol']}],
             'tickets': tickets}
        d.update(kw)
        return d

    def tk(**kw):
        t = {'name': '一般', 'price': '¥4,300', 'is_lottery': False, 'is_sale_started': True,
             'is_sale_ended': False, 'is_sold_out': False, 'is_stream': False,
             'start_date': '2026-08-01', 'start_time': '10:00',
             'end_date': '2026-09-30', 'end_time': '23:59', 'perf_dt': ''}
        t.update(kw)
        return t

    # ① 買える枠＝締切つき。県・公演時刻・出演者・ジャンルが入る
    e, _ = build_one(lr, mk([tk()]), today, unk)
    assert e['tickets'][0]['type'] == '一般（東京 10/1 19:00公演）〜9/30 23:59', e['tickets'][0]
    assert e['artist'] == '岩立沙穂／柏木由紀' and e['prefecture'] == '東京'
    assert e['_genre'] == 'idol' and e['links']['zaiko'] == lr['url']
    assert e['dateLabel'] == '2026年10月1日(木) 19:00開演', e['dateLabel']

    # ①-2 🚨一覧の日付より個別ページの開演（display_date_period）を優先（2026-09-24 AKB48劇場で一覧が3日前を出した）
    lr2 = dict(lr, date='2026-09-27', time='16:00')
    dp = {'start': {'date_string': '2026-09-30', 'time_string': '18:30'}}
    e1b, _ = build_one(lr2, mk([tk()], display_date_period=dp), today, unk)
    assert e1b['date'] == '2026-09-30' and e1b['dateLabel'] == '2026年9月30日(水) 18:30開演', e1b['dateLabel']
    assert '9/30 18:30公演' in e1b['tickets'][0]['type'], e1b['tickets'][0]
    e1c, _ = build_one(lr2, mk([tk()]), today, unk)          # 個別に無ければ一覧のまま
    assert e1c['date'] == '2026-09-27', e1c['date']

    # ② 🚨ZAIKOは売切と終了をセットで立てる＝**「予定枚数終了」を名乗らない**。
    #    先着の枠が終わった＝**販売終了**（実ページも「販売終了日 …」と書く）
    e2, why2 = build_one(lr, mk([tk(is_sold_out=True, is_sale_ended=True)]), today, unk)
    assert e2 is not None, (e2, why2)
    assert e2['tickets'][0]['soldout'] and e2['tickets'][0]['saleEnded'], e2['tickets'][0]
    assert 'presaleEnded' not in e2['tickets'][0], e2['tickets'][0]

    # ③ 抽選の枠が終わった＝**先行終了**（実ページ「抽選申込期間はすでに終了しています」）
    e3, _ = build_one(lr, mk([tk(is_sold_out=True, is_sale_ended=True, is_lottery=True)]),
                      today, unk)
    assert e3['tickets'][0]['soldout'] and e3['tickets'][0]['presaleEnded'], e3['tickets'][0]
    assert 'saleEnded' not in e3['tickets'][0], e3['tickets'][0]

    # ③-2 🚨抽選の申込が終わって当選者の支払い期間の間は、フラグが立たない（2026-09-22 実測）
    #     ＝申込締切が過去の抽選枠は先行終了にする。締切が先なら今までどおり買える枠
    e3b, _ = build_one(lr, mk([tk(is_lottery=True, is_sale_started=True, end_date='2026-09-05')]),
                       today, unk)
    assert e3b['tickets'][0].get('presaleEnded') and e3b['tickets'][0].get('soldout'), e3b['tickets'][0]
    e3d, _ = build_one(lr, mk([tk(is_lottery=True, is_sale_started=True)]), today, unk)
    assert not e3d['tickets'][0].get('soldout'), e3d['tickets'][0]

    # ③-3 🚨「00:00」は開演時刻ではない（ZAIKOが入れていないだけ）＝バッジに書かない
    e3c, _ = build_one(dict(lr, time='00:00'), mk([tk()]), today, unk)
    assert '00:00公演' not in e3c['tickets'][0]['type'], e3c['tickets'][0]
    assert e3c['tickets'][0]['type'].startswith('一般（東京 10/1公演）'), e3c['tickets'][0]
    assert '開演' not in e3c['dateLabel'], e3c['dateLabel']

    # ④ 締切が公演日より後なら公演日で締める。配信は例外
    e4, _ = build_one(lr, mk([tk(end_date='2026-10-05')]), today, unk)
    assert e4['tickets'][0]['date'] == '2026-10-01', e4['tickets'][0]
    e4b, _ = build_one(lr, mk([tk(is_stream=True, end_date='2026-10-05')]), today, unk)
    assert e4b['tickets'][0]['date'] == '2026-10-05', e4b['tickets'][0]
    assert '配信' in e4b['tickets'][0]['type'], e4b['tickets'][0]

    # ⑤ 締切がどこにも無い＝締切を作らず「販売中」＋saleEndUnknown（公演日を置き場に）
    e5, _ = build_one(lr, mk([tk(end_date=None, end_time=None)]), today, unk)
    assert e5['tickets'][0]['saleEndUnknown'] and e5['tickets'][0]['date'] == '2026-10-01'
    assert e5['tickets'][0]['type'].endswith('販売中'), e5['tickets'][0]

    # ⑥ 受付前＝**開始日（on_sale_from / lottery_start_date）があるなら「M/D HH:MM発売」で載せる**
    e6, _ = build_one(lr, mk([tk(is_sale_started=False,
                                start_date='2026-09-25', start_time='20:00')]), today, unk)
    assert e6['tickets'][0]['type'] == '一般（東京 10/1 19:00公演）9/25 20:00発売', e6['tickets'][0]
    assert e6['tickets'][0]['startDate'] == '2026-09-25', e6['tickets'][0]
    # 開始日が無い／過去なら載せない（推測で日付を作らない）
    e6b, why6b = build_one(lr, mk([tk(is_sale_started=False, start_date=None)]), today, unk)
    assert e6b is None, (e6b, why6b)
    e6c, _ = build_one(lr, mk([tk(is_sale_started=False, start_date='2026-09-01')]), today, unk)
    assert e6c is None, e6c

    # ⑦ 公演が終わっている／個別が読めない／出す側
    assert build_one(dict(lr, date='2026-09-20'), mk([tk()]), today, unk)[0] is None
    assert build_one(lr, None, today, unk)[0] is None
    assert build_one(dict(lr, title='出店ブース申込'),
                     mk([tk()], name='出店ブース申込'), today, unk)[0] is None

    # ⑧ 券種名が空＝「チケット」／抽選なら「抽選チケット」／同名は番号で分ける
    e8, _ = build_one(lr, mk([tk(name=''), tk(name='', is_lottery=True)]), today, unk)
    kinds = [t['type'].split('（')[0] for t in e8['tickets']]
    assert kinds == ['チケット', '抽選チケット'], kinds

    # ⑧-3 🚨駐車券は**券種名（ref_name）で外す**（front_textしか見ないと素通りする）
    e8d, _ = build_one(lr, mk([tk(), tk(name='両会場駐車券', price='¥4,000')]), today, unk)
    assert len(e8d['tickets']) == 1, [t['type'] for t in e8d['tickets']]
    assert '駐車' not in e8d['tickets'][0]['type'], e8d['tickets'][0]

    # ⑧-4 🚨券種ごとに公演日時が書いてあるなら**その日の公演として出す**
    #     （1ページに複数公演・複数会場を詰めるページ＝ダウ9000は4公演／
    #      新しい学校のリーダーズは5会場。読まないと全部イベント初日になり嘘になる）
    e8e, _ = build_one(lr, mk([
        tk(name='【一般先着】10/15(木)13時開演', perf_dt='10月15日 (木) 13:00 – 終了時間未定',
           end_date='2026-10-15', end_time='23:59'),
        tk(name='【一般先着】10/16(金)13時開演', perf_dt='10月16日 (金) 13:00 – 終了時間未定',
           end_date='2026-10-16', end_time='23:59')]), today, unk)
    got8e = [t['type'] for t in e8e['tickets']]
    assert '（東京 10/15 13:00公演）' in got8e[0], got8e
    assert '（東京 10/16 13:00公演）' in got8e[1], got8e
    # 上書きが無いときはイベントの公演日を使う（従来どおり）
    e8f, _ = build_one(lr, mk([tk()]), today, unk)
    assert '（東京 10/1 19:00公演）' in e8f['tickets'][0]['type'], e8f['tickets'][0]

    # ⑨ 表に無いジャンルは写さずに数える
    unk2 = collections.Counter()
    e9, _ = build_one(lr, mk([tk()], genres=['Kabuki'], performers=[]), today, unk2)
    assert unk2['Kabuki'] == 1 and e9['_genre'] == GENRE_FALLBACK, (unk2, e9['_genre'])

    # ⑧-2 券種名が空で値段が違うなら**値段を添えて見分ける**（番号だけにしない）
    e8b, _ = build_one(lr, mk([tk(name='', price='¥4,300'), tk(name='', price='¥6,000')]),
                       today, unk)
    heads8 = [t['type'].split('（東京')[0] for t in e8b['tickets']]
    assert heads8 == ['チケット ¥4,300', 'チケット ¥6,000'], heads8
    # 値段まで同じなら番号で分ける
    e8c, _ = build_one(lr, mk([tk(name='', price='¥4,300'), tk(name='', price='¥4,300')]),
                       today, unk)
    heads8c = [t['type'].split('（東京')[0] for t in e8c['tickets']]
    assert heads8c == ['チケット（1）', 'チケット（2）'], heads8c

    # ⑨-2 出演者のジャンルが空＝一覧のカテゴリで補う（clubs-nightlife → club）
    unk3 = collections.Counter()
    e9b, _ = build_one(dict(lr, cat='clubs-nightlife'),
                       mk([tk()], genres=[], performers=[{'name': 'DJ テスト', 'genres': []}]),
                       today, unk3)
    assert e9b['_genre'] == 'club', e9b['_genre']
    assert not unk3, unk3

    # ⑨-3 🆕2026-09-23＝イベント側のジャンルが効く（ハーベスタが dict を読めるようになった分）。
    #      出演者が空でも「売り場が Idol と言っている」なら idol。その他に落とさない。
    unk4 = collections.Counter()
    e9c, _ = build_one(dict(lr, cat='concerts-live-music'),
                       mk([tk()], genres=['Idol'], performers=[]), today, unk4)
    assert e9c['_genre'] == 'idol', e9c['_genre']
    # ⑨-4 出演者の札のほうが具体的なときは出演者が勝つ（VTuber がイベント側の Rock に負けない）
    e9d, _ = build_one(lr, mk([tk()], genres=['Alternative', 'Pop', 'Rock'],
                              performers=[{'name': '藍海テスト', 'genres': ['VTuber', 'Rock']}]),
                       today, unk4)
    assert e9d['_genre'] == 'vtuber', e9d['_genre']
    # ⑨-5 `Japanese music` は大分類なので写さない（和楽器の意味ではない）。
    #      細分があればそちらが効き、無ければ その他 に落ちる。
    e9e, _ = build_one(lr, mk([tk()], genres=['Japanese music', 'Rock'], performers=[]), today, unk4)
    assert e9e['_genre'] == 'rock', e9e['_genre']
    e9f, _ = build_one(dict(lr, cat='concerts-live-music'),
                       mk([tk()], genres=['Japanese music'], performers=[]), today, unk4)
    assert e9f['_genre'] == GENRE_FALLBACK, e9f['_genre']
    assert not unk4, unk4
    # 大会・競技はスポーツへ／演劇・ショーは演劇へ
    for _cat, _want in (('tournaments-competitions', 'sports'),
                        ('performances-shows', 'engeki'),
                        ('festivals-fairs', 'fes')):
        _e, _ = build_one(dict(lr, cat=_cat), mk([tk()], genres=[], performers=[]),
                          today, collections.Counter())
        assert _e['_genre'] == _want, (_cat, _e['_genre'])

    # ⑩ 2027公演はR9年表記
    e10, _ = build_one(dict(lr, date='2027-02-11'),
                       mk([tk(end_date='2027-02-01')]), today, unk)
    assert 'R9年 2/11 19:00公演' in e10['tickets'][0]['type'], e10['tickets'][0]
    # 🚨締切側には年を付けない（既存の流儀）
    assert e10['tickets'][0]['type'].endswith('〜2/1 23:59'), e10['tickets'][0]

    print('selftest OK')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?')
    ap.add_argument('--out', default=None)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.src:
        ap.error('ハーベスト結果のJSONを渡して（例 tmp/zaiko_0921d.json）')
    today = datetime.date.today().isoformat()
    return build_all(a.src, a.out or a.src.replace('.json', '_built.json'), today)


if __name__ == '__main__':
    sys.exit(main())
