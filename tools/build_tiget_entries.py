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
# 🆕2026-09-18 ユーザー「うん　毎日確認お願いします」＝**TIGETの葉カテゴリを全部取り込む**。
#   ジャンルは**売り場のカテゴリを機械で写す**（[[feedback_genre_pia_asis_and_other]]）＝
#   人が1件ずつ見る枠を作らない。TIGETに無い区別（声優／2.5次元など）は下の注を見る。
CAT_GENRE = {
    # ── 音楽 ──
    '29': 'idol',         # アイドル
    '30': 'jazz',         # ジャズ／フュージョン
    '31': 'jpop',         # 邦楽ポップ／ロック  🚨TIGETの「邦楽」は日本のポップス＝うちの hougaku(和楽器) ではない
    '32': 'hiphop',       # 邦楽ヒップホップ／レゲエ
    '33': 'jpop',         # 邦楽ソウル／R&B
    '34': 'enka',         # 邦楽演歌／民謡
    '35': 'musicetc',     # 邦楽その他
    '36': 'yougaku',      # 洋楽ポップ／ロック
    '37': 'hiphop',       # 洋楽ヒップホップ／レゲエ
    '38': 'yougaku',      # 洋楽ソウル／R&B
    '39': 'yougaku',      # 洋楽その他
    '40': 'classic',      # アカペラ／合唱
    '41': 'anime',        # アニメ／ゲーム／声優 … ⚠️2.5次元は82に別であるので混ざらない。
                          #    声優個人のイベントだけ seiyuu にするのは**名前の裏取りが要る**＝機械では anime
    '42': 'fes',          # フェスティバル(音楽)
    '43': 'musicetc',     # 音楽その他
    '78': 'kpop',         # K-POP
    '79': 'utaite',       # 歌い手
    '80': 'vocaloid',     # ボカロ
    '81': 'youtuber',     # YouTuber
    '84': 'vtuber',       # VTuber
    # ── イベント ──
    '44': 'event',        # 脱出／謎解き
    '45': 'fanevent',     # ショー／ファンイベント
    '46': 'talkshow',     # トークショー／講演会
    '47': 'gourmet',      # グルメ／ディナーショー … うちは gourmet と dinnershow に分かれるが
                          #    TIGETは1つ。広いほう(gourmet)に寄せる
    '48': 'kids',         # ファミリー／子ども向け
    '49': 'anime',        # アニメ／ゲーム
    '50': 'event',        # ファッション／ビューティー
    '51': 'art',          # 展示会／博覧会
    '52': 'event',        # イベントその他
    '82': '2.5ji',        # 2.5次元
    # ── お笑い／演劇／ダンス ──
    '53': 'owarai',       # お笑い／寄席
    '54': 'engeki',       # 演劇
    '55': 'engeki',       # ダンス／パフォーマンス … うちに踊りのタブが無い
    '56': 'engeki',       # バレエ … 同じ
    '57': 'engeki',       # 朗読／リーディング
    '58': 'musical',      # ミュージカル／ショー
    '59': 'fes',          # フェスティバル(演劇)
    '60': 'magic',        # マジック／手品
    '61': 'engeki',       # 演劇その他
    # ── クラシック ──
    '66': 'classic', '67': 'classic', '68': 'classic', '69': 'classic', '70': 'classic',
    # ── スポーツ・映画・アート・その他 ──
    '72': 'sports', '73': 'sports', '74': 'sports',
    '75': 'movie',        # 映画
    '76': 'art',          # アート・ミュージアム
    '77': 'event',        # その他
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


def prog_time(p):
    """公演の塊の見出しから開場時刻を取る（「2026年09月27日(日) 11:30開場」→ 11:30）。"""
    m = re.search(r'(\d{1,2}):(\d{2})', p.get('datetime_text') or '')
    return '%d:%s' % (int(m.group(1)), m.group(2)) if m else None


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
#             チケット先行案内登録（0円の登録）
#   🆕🚨2026-09-22 ユーザー決定「載せる」＝**駐車券だけ・グッズ引換券だけのページは載せる**。
#      推しの現場へ行くのに要るものだから「出す側」ではない（[[feedback_oshinavi_concept]]）。
#      ＝ここから「駐車」を外した。9/18の除外リストは失効。
SELLER_SIDE = re.compile(
    r'委託販売|即売会|出店|ブース(?:出展|申込)?|'          # 自分が売る側
    r'エントリーフォーム|参加エントリ|出場エントリ|'        # 自分が出る側
    r'案内登録|先行案内'                                    # 0円の登録だけ
)


# 🆕2026-09-24 ユーザー決定「チェキ通販は外して」＝グッズ・チェキの**通信販売だけ**のページは載せない
#   （id22620「Bunny La Crew オンラインチェキ通販」。開催日の欄は販売締切を入れてあるだけ）。
#   ⚠️駐車券・グッズ引換券（現場で使う）と配信視聴券は載せる＝ここには入れない。
NOT_EVENT = re.compile(r'通販|通信販売')


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
    if NOT_EVENT.search(ev.get('name') or ''):
        return None, '通信販売だけのページ（会いに行く現場が無い）'
    # 🚨主催者の雛形が730日の線をすり抜ける（2026-09-18＝id13228 公演名「予約」・
    #    公演2027-11-18 なのに**発売日が2025-11-18**＝1年10か月前）。
    #    ありふれた1語の公演名で、発売日が1年以上前のものは雛形として弾く。
    ss = sale_start(ev)[0]
    if (ev.get('name') or '').strip() in ('予約', 'チケット', 'テスト', '当日払い', '前売') and ss:
        if ss < (datetime.date.fromisoformat(today) - datetime.timedelta(days=365)).isoformat():
            return None, '公演名が1語＋発売日が1年より前＝主催者の雛形の疑い'
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
    # 🚨🚨同じ日に公演が2つ以上あるエントリは、バッジに**開場時刻**を入れる。
    #    入れないと「昼の部」「夜の部」や時間帯予約が同じ文字になり、後ろの重複つぶしで
    #    **本物の別枠が消える**（2026-09-18＝198エントリ・113枠が潰れていた。
    #    id510796 ひでじビールは11:00〜17:00の30分刻み17枠が1枠になっていた）。
    #    決まり＝[[feedback_same_day_show_time_badge]]（同会場同日の時間違いは公演時間を入れる）。
    percount = {}
    for p in ev['programs']:
        if p.get('date'):
            percount[p['date']] = percount.get(p['date'], 0) + 1
    tickets, has_live = [], False
    for p in ev['programs']:
        d = p.get('date')
        if not d or d < today:
            continue
        ptime = prog_time(p) if percount.get(d, 0) > 1 else None
        # 🚨同じ公演の中で券種名がぶつかると、**画面に同じバッジが並んで区別がつかない**
        #    （2026-09-18＝98エントリでこれが起きた。「チケット（岐阜 3/7公演）〜3/7 14:00」が3つ）。
        #    真因は2つ＝①TIGETの主催者が別の券種に同じ名前を付けている
        #              ②こちらの ticket_name() が「開場/開演」入りの名前を全部「チケット」に倒す
        #    ぶつかって**値段が違うなら値段を添えて見分ける**（値段はページに書いてある本物の情報）。
        #    値段まで同じなら本当の重複なので、後ろでまとめて1つに畳む。
        names = [ticket_name(t.get('name')) for t in p['tickets']]
        prices = [t.get('price') for t in p['tickets']]
        multi = {n for n in names if names.count(n) > 1}
        for i, t in enumerate(p['tickets']):
            st = state_of(t.get('class'))
            per = last_period(t)
            # 🚨出す側は**券種名にも**当てる（2026-09-18＝id12480「出店ブース」・
            #    id12821「yen販売のみの出店者」・id13146「ステージ装飾協賛のみ」が残っていた）。
            #    ⚠️「取り置き」「チェキ撮影」は推しに会う側なので巻き添えにしない。
            if is_seller_side(t.get('name')) and not re.search(r'取り置き|取置|チェキ', t.get('name') or ''):
                continue
            nm = names[i]
            if nm in multi and prices[i] is not None:
                same = {prices[j] for j, n in enumerate(names) if n == nm}
                if len(same) > 1:
                    nm = '%s %s円' % (nm, format(prices[i], ','))
            # 🚨県が分からないイベントがある（主催者が住所を登録していない＝会場名にも一覧にも
            #    JSON-LDにも県が無い。2026-09-18 に7件）。会場名の市名から県を当てるのは推測なので
            #    **バッジから県を落とす**。カードには📍会場名が出るので場所は読める。
            when = f'{md(d)} {ptime}公演' if ptime else f'{md(d)}公演'
            head = f'{nm}（{pref} {when}）' if pref else f'{nm}（{when}）'
            # 🆕2026-09-24 券種の下の注記（受付：… 〜／受付終了日時：…）＝受付期間の欄が無い券種の発売と締切
            sa, ea = t.get('start_at'), t.get('end_at')
            if ea and ea[0] > d and not re.search(r'配信|視聴|アーカイブ', nm):
                ea = (d, '')                       # 締切が公演日より後なら公演日で締める
            if st == 'unopened':
                if per:
                    # 🚨2026-09-24 発売前でも締切（受付期間の終わり）を持つ＝date=発売日だと発売日の翌0時に消える
                    #   （FANYで24枠が消えたのと同じ型）。
                    end, endt = per[2], per[3]
                    if end > d and not re.search(r'配信|視聴|アーカイブ', nm):
                        end, endt = d, ''
                    tickets.append({'type': f'{head}{md(per[0])} {per[1]}発売〜{md(end)} {endt}'.replace('  ', ' ').rstrip(),
                                    'date': end, 'startDate': per[0], 'url': ev['url']})
                    has_live = True
                elif sa and sa[0] >= today:
                    tk = {'type': f'{head}{md(sa[0])} {sa[1]}発売'.rstrip(), 'date': sa[0],
                          'startDate': sa[0], 'url': ev['url']}
                    if ea and ea[0] >= sa[0]:
                        tk['type'] = f'{head}{md(sa[0])} {sa[1]}発売〜{md(ea[0])} {ea[1]}'.replace('  ', ' ').rstrip()
                        tk['date'] = ea[0]
                    tickets.append(tk)
                    has_live = True
                elif ss_date and ss_date >= today:
                    # 🚨受付前で受付期間の欄が無い時は JSON-LD の validFrom が発売日。
                    #    ただし**今日以降のときだけ**使う（2026-09-18＝「当日券」の validFrom は
                    #    そのイベントが売り出された日で**過去**＝流用すると過ぎた日を発売日にしてしまう）。
                    #    これで63イベントの発売前が拾えるようになった。
                    tickets.append({'type': f'{head}{md(ss_date)} {ss_time}発売'.replace('  ', ' ').rstrip(),
                                    'date': ss_date, 'startDate': ss_date, 'url': ev['url']})
                    has_live = True
                # validFrom が過去・取れない＝推測で日付を作らないので載せない
            elif st == 'live':
                if per:
                    # 🚨締切が公演日より後なら公演日で締める（[[feedback_sale_end_cap_show_date]]）。
                    #    ⚠️配信・視聴チケットは公演の後も買えるので例外（巻き添えで嘘にしない）。
                    end, endt = per[2], per[3]
                    if end > d and not re.search(r'配信|視聴|アーカイブ', nm):
                        end, endt = d, ''
                    tickets.append({'type': f'{head}〜{md(end)} {endt}'.rstrip(),
                                    'date': end, 'url': ev['url']})
                    has_live = True
                elif ea:
                    # 🆕2026-09-24 「当日支払い」でも注記に受付終了日時があれば、それが締切
                    s0 = sa or ((ss_date, ss_time) if ss_date else None)
                    tk = {'type': f'{head}〜{md(ea[0])} {ea[1]}'.rstrip(), 'date': ea[0], 'url': ev['url']}
                    if s0 and s0[0] >= today:
                        tk['startDate'] = s0[0]
                        tk['type'] = f'{head}{md(s0[0])} {s0[1]}発売〜{md(ea[0])} {ea[1]}'.replace('  ', ' ').rstrip()
                    tickets.append(tk)
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
    # 🚨まったく同じ枠（券種名・締切・飛び先・印がぜんぶ同じ）は1つに畳む。
    #    画面では見分けられないので、並べても利用者の役に立たない。
    #    ⚠️飛び先が違うなら畳まない（[[feedback_dedup_badges_keeps_urls]]）＝キーにurlを入れている。
    seen, uniq = set(), []
    for t in tickets:
        k = (t.get('type'), t.get('date'), t.get('startDate'), t.get('url'),
             bool(t.get('soldout')), bool(t.get('saleEnded')), bool(t.get('saleEndUnknown')))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(t)
    tickets = uniq

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


# 🚨ツアーの尻尾＝会場を表す札だけを剥がす。
#   2026-09-18＝`〜vol.1〜`『〈14時の部〉』`~live.12~` まで剥がして**別商品・別公演を畳んでいた**
#   （id12767 能楽いろは＝〈通し券〉5,500円と〈14時の部〉3,000円が1エントリに／id11869・12758・12427・12312）。
#   ⛔剥がさない＝vol. / の部 / DAY / live. / 通し / 先行 / 回 / 夜 / 昼 …（別の商品・別の公演）
CITY_SUFFIX = re.compile(r'\s*(?:in|In|IN|＠|@)\s*[^\s＞>〈〉]{1,12}(?:公演)?\s*$')
NOT_A_PLACE = re.compile(r'vol|Vol|VOL|ｖｏｌ|の部|DAY|Day|day|live|LIVE|通し|先行|[0-9]+回|昼|夜|部$')


def tour_key(e):
    """ツアーの束ね先を決める鍵＝（出演者, 会場名を落とした公演名）。
    🚨「『最』ライブツアー2026 in 大阪／in 仙台／in 福岡／in 宮古島」のように、
       TIGETは**会場ごとに別ページ**で売る。決まりは「ツアー・複数会場は1エントリ」
       （feedback_tour_consolidate）なので、ここで束ねて各枠に会場別URLを焼き込む
       （feedback_tour_per_ticket_url）。"""
    m = CITY_SUFFIX.search(e['name'])
    if not m or NOT_A_PLACE.search(m.group(0)):
        return None
    base = CITY_SUFFIX.sub('', e['name']).strip()
    if len(base) < 4:
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
    # 🆕2026-09-24 当日支払いでも注記に「受付終了日時」があれば締切にする（締切不明にしない）
    ev3b = json.loads(json.dumps(ev))
    ev3b['programs'][0]['tickets'] = [{'name': '自由席', 'class': 'is-available', 'periods': [],
                                       'end_at': ['2026-10-17', '23:59']}]
    t3b = build(ev3b, '2026-09-18')[0]['tickets'][0]
    assert t3b['type'] == '自由席（大阪 10/18公演）〜10/17 23:59' and t3b['date'] == '2026-10-17', t3b
    assert 'saleEndUnknown' not in t3b, t3b
    # 🆕発売前（受付期間あり）は発売〜締切で持つ＝発売日の翌0時に消えない
    ev3c = json.loads(json.dumps(ev))
    ev3c['programs'][0]['tickets'] = [{'name': '一般', 'class': 'is-unable is-unopened',
                                       'periods': [{'parsed': ['2026-09-25', '19:15', '2026-10-17', '23:59']}]}]
    t3c = build(ev3c, '2026-09-18')[0]['tickets'][0]
    assert t3c['type'] == '一般（大阪 10/18公演）9/25 19:15発売〜10/17 23:59', t3c
    assert t3c['startDate'] == '2026-09-25' and t3c['date'] == '2026-10-17', t3c
    # 🆕受付前で受付期間の欄が無くても、注記「受付：… 〜」があれば発売日（validFrom より優先）
    ev3d = json.loads(json.dumps(ev))
    ev3d['programs'][0]['tickets'] = [{'name': '一般予約', 'class': 'is-unable is-unopened', 'periods': [],
                                       'start_at': ['2026-10-03', '10:00']}]
    t3d = build(ev3d, '2026-09-18')[0]['tickets'][0]
    assert t3d['type'] == '一般予約（大阪 10/18公演）10/3 10:00発売' and t3d['startDate'] == '2026-10-03', t3d
    # 🚨受付前で受付期間の欄が無い＝validFrom が今日以降なら発売日として使う／過去なら載せない
    evU = json.loads(json.dumps(ev))
    evU['programs'][0]['tickets'] = [{'name': '一般チケット', 'class': 'is-unable is-unopened',
                                      'price': 2500, 'periods': []}]
    evU['ld_offers'] = [{'valid_from': '2026-09-27', 'valid_from_time': '20:00'}]
    eU, _ = build(evU, '2026-09-18')
    assert eU['tickets'][0]['type'] == '一般チケット（大阪 10/18公演）9/27 20:00発売', eU['tickets'][0]
    assert eU['tickets'][0]['startDate'] == '2026-09-27'
    evU2 = json.loads(json.dumps(evU))
    evU2['ld_offers'] = [{'valid_from': '2026-07-16', 'valid_from_time': '19:00'}]   # 過去＝使わない
    assert build(evU2, '2026-09-18')[0] is None, '過ぎた日を発売日にしてしまう'
    # 🚨同じ日に公演が2つ以上＝バッジに開場時刻を入れる（昼夜・時間帯予約を潰さない）
    evT = json.loads(json.dumps(ev))
    evT['programs'] = [
        {'date': '2026-10-18', 'datetime_text': '2026年10月18日(日)　11:00開場',
         'tickets': [{'name': 'BBQ予約', 'class': 'is-available', 'price': 4000,
                      'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-17', '23:59']}]}]},
        {'date': '2026-10-18', 'datetime_text': '2026年10月18日(日)　11:30開場',
         'tickets': [{'name': 'BBQ予約', 'class': 'is-available', 'price': 4000,
                      'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-17', '23:59']}]}]},
    ]
    eT, _ = build(evT, '2026-09-18')
    tyT = sorted(t['type'] for t in eT['tickets'])
    assert tyT == ['BBQ予約（大阪 10/18 11:00公演）〜10/17 23:59',
                   'BBQ予約（大阪 10/18 11:30公演）〜10/17 23:59'], tyT
    # 🚨締切が公演日より後なら公演日で締める（配信は例外）
    evC = json.loads(json.dumps(ev))
    evC['programs'][0]['tickets'] = [
        {'name': '一般', 'class': 'is-available', 'price': 3000,
         'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-25', '21:00']}]},
        {'name': '【配信】視聴チケット', 'class': 'is-available', 'price': 2000,
         'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-25', '21:00']}]}]
    eC, _ = build(evC, '2026-09-18')
    got = {t['type']: t['date'] for t in eC['tickets']}
    assert got.get('一般（大阪 10/18公演）〜10/18') == '2026-10-18', got
    assert got.get('【配信】視聴チケット（大阪 10/18公演）〜10/25 21:00') == '2026-10-25', got
    # 🚨出す側は券種名にも当てる（取り置き・チェキは巻き添えにしない）
    evS = json.loads(json.dumps(ev))
    evS['programs'][0]['tickets'] = [
        {'name': '出店ブース', 'class': 'is-available', 'price': 3000,
         'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-17', '23:59']}]},
        {'name': '自由席（TIGET予約 or 出演者から取り置き）', 'class': 'is-available', 'price': 2500,
         'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-17', '23:59']}]}]
    eS, _ = build(evS, '2026-09-18')
    assert len(eS['tickets']) == 1 and '自由席' in eS['tickets'][0]['type'], [t['type'] for t in eS['tickets']]
    # 🚨ツアー畳み＝会場の札だけ剥がす（vol./の部/通し券は別商品なので畳まない）
    def mk2(nm):
        return {'artist': 'A', 'name': nm, 'venue': 'v', 'prefecture': '東京', 'date': '2026-10-01',
                'dateLabel': '', 'links': {'tiget': 'u'}, 'tickets': []}
    assert tour_key(mk2('能楽いろは〈通し券〉')) is None
    assert tour_key(mk2('定期公演 vol.87')) is None
    assert tour_key(mk2('Aライブ in 大阪')) == ('A', 'Aライブ')
    # 🚨同じ公演で券種名がぶつかる＝値段が違えば値段で見分ける／値段も同じなら1つに畳む
    ev8 = json.loads(json.dumps(ev))
    ev8['programs'][0]['tickets'] = [
        {'name': '開場17:00 開演17:30', 'class': 'is-available', 'price': 3000,
         'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-17', '23:59']}]},
        {'name': '開場18:00 開演18:30', 'class': 'is-available', 'price': 4000,
         'periods': [{'parsed': ['2026-09-01', '10:00', '2026-10-17', '23:59']}]},
    ]
    e8, _ = build(ev8, '2026-09-18')
    ty8 = sorted(t['type'] for t in e8['tickets'])
    assert ty8 == ['チケット 3,000円（大阪 10/18公演）〜10/17 23:59',
                   'チケット 4,000円（大阪 10/18公演）〜10/17 23:59'], ty8
    ev9 = json.loads(json.dumps(ev8))
    ev9['programs'][0]['tickets'][1]['price'] = 3000        # 値段も同じ＝本当の重複
    e9, _ = build(ev9, '2026-09-18')
    assert len(e9['tickets']) == 1, [t['type'] for t in e9['tickets']]
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
               'もののけフェス2026【チケット先行案内登録】'):
        assert is_seller_side(nm), nm
    # 推しに会いに行く券＝載せる（巻き添えで消さない）
    # 🆕2026-09-22 ユーザー決定＝駐車券だけ・グッズ引換券だけのページも載せる
    for nm in ('ブイ×カケ フェス 事前予約駐車場', 'ホークスCS 駐車場予約券', 'hololive グッズ引換券',
               '【特別企画】 花村きり チェキ撮影会', 'ブイ×カケ フェス ゲストレイヤーチェキ撮影会',
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
