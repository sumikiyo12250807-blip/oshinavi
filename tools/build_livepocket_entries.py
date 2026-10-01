# -*- coding: utf-8 -*-
"""livePocket のハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形テンプレート）。

  python tools/build_livepocket_entries.py tmp/livepocket_MMDD.json --out tmp/built_livepocket_MMDD.json
  python tools/build_livepocket_entries.py --selftest

## 枠の単位＝**受付ごと**（2026-09-28 ユーザー指示「livePocket作って」の依頼どおり）
livePocket の個別ページは「受付（先着販売受付・抽選販売受付 など）」ごとに販売期間を持ち、
その下に券種（会場チケット・撮影会の時間枠・カフェの席 など）が並ぶ。
締切を持つのは受付なので、**1受付＝1枠**。券種の状態は受付の状態を決めるのに使う。

## 売り状態の読み方（2026-09-28 に実ページ108件の文言を数えて決めた）

| 受付の札（head__status） | 券種の札（ticket-card__status） | OSHINAVI |
|---|---|---|
| 販売前 | 販売前 | 発売前＝「M/D HH:MM発売〜締切」・startDate＝発売日・date＝締切（発売日にしない） |
| 販売中 | 販売中／売切間近 が1つでも | 買える＝「〜締切」・date＝締切 |
| 販売中 | 全部が 予定販売数終了 | `soldout`（予定枚数終了） |
| 予定販売枚数終了 | 予定販売数終了 | `soldout`（予定枚数終了） |
| 販売終了 | 受付終了 | `soldout`＋`saleEnded`（販売終了） |
| それ以外の札 | | 🚨推測しない＝枠を作らず「読めない札」として報告 |

🚨締切が書いていない販売中＝TIGETと同じ（2026-09-27 ユーザー決定）＝「〜公演日」の販売中（date＝公演日・startDate なし）。
🚨締切が書いていない販売前＝「M/D HH:MM発売〜公演日」（date＝公演日。発売日にすると翌0時に消える）。
🚨発売前なのに開始日時が読めない＝日付を作らない＝その枠は載せない（報告に出す）。
🚨締切が公演日（会期の最終日）より後なら公演日で締める。配信・視聴・アーカイブは例外。

## 載せないもの
- 出す側の申込（出店・出展・出演エントリー・案内登録）＝[[feedback_oshinavi_concept]]
- 推しに会いに行く枠ではないカテゴリ＝TIGETの CAT_SKIP と同じ線（セミナー・ジム・ヨガ/フィットネス）
- 公演が終わっている／公演日が2年より先（主催者の試し書き）
🚨コラボカフェ・POP UP・グッズ抽選・カードゲームなどは**除外しない**（推し活の範囲・通販も載せる＝9/24決定）。
   判断がつきにくい型は `_review` に理由を書いて報告に出す（人が見る）。
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

# livePocket のカテゴリ（l_cat 大分類 / s_cat 小分類）→ OSHINAVI のジャンル
#   **売り場の分類を機械で写す**（[[feedback_genre_pia_asis_and_other]]）。語彙は 2026-09-28 にヘッダーの
#   カテゴリ一覧（71個）から全部書き出した。表に無いものは数えて報告する（黙って その他 に落とさない）。
CAT_GENRE = {
    ('音楽', '邦楽'): 'jpop',            # 🚨TIGETと同じ＝売り場の「邦楽」は日本のポップス。うちの hougaku（和楽器）ではない
    ('音楽', 'ロック'): 'rock',
    ('音楽', 'ポップス'): 'jpop',
    ('音楽', 'フェス'): 'fes',
    ('音楽', 'hiphop'): 'hiphop',
    ('音楽', 'JAZZ'): 'jazz',
    ('音楽', 'K-POP'): 'kpop',
    ('音楽', 'クラシック'): 'classic',
    ('音楽', 'ヴィジュアル系'): 'rock',  # e+ の visual→rock と同じ
    ('音楽', '音楽その他'): 'musicetc',
    ('音楽', ''): 'musicetc',
    ('演劇・ステージ', '舞台'): 'engeki',
    ('演劇・ステージ', '演劇'): 'engeki',
    ('演劇・ステージ', '落語'): 'owarai',    # ぴあのビルダーと同じ（落語・寄席→owarai）
    ('演劇・ステージ', '伝統芸能'): 'dento',
    ('演劇・ステージ', 'お笑い'): 'owarai',
    ('演劇・ステージ', 'モノマネ'): 'owarai',
    ('演劇・ステージ', 'ダンス'): 'dance',  # 🆕2026-09-30 ユーザー「ダンス作って」（趣味のダンスは event のまま）
    ('演劇・ステージ', '演劇・ステージその他'): 'engeki',
    ('演劇・ステージ', ''): 'engeki',
    ('ファン・アイドル', 'ファンミーティング'): 'fanevent',
    ('ファン・アイドル', '握手会'): 'fanevent',
    ('ファン・アイドル', '展覧会'): 'art',
    ('ファン・アイドル', '撮影会'): 'fanevent',
    ('ファン・アイドル', 'トークショー'): 'talkshow',
    ('ファン・アイドル', 'ライブ'): 'idol',
    ('ファン・アイドル', 'グッズ'): 'fanevent',
    ('ファン・アイドル', 'ファン・アイドルその他'): 'fanevent',
    ('ファン・アイドル', ''): 'fanevent',
    ('アニメ・キャラ', 'コラボカフェ'): 'anime',
    ('アニメ・キャラ', '展覧会'): 'art',
    ('アニメ・キャラ', 'グッズ'): 'anime',
    ('アニメ・キャラ', 'アニメ・キャラその他'): 'anime',
    ('アニメ・キャラ', ''): 'anime',
    ('スポーツ', ''): 'sports',
    ('趣味・カルチャー・レジャー', ''): 'event',
    ('趣味・カルチャー・レジャー', 'ダンス'): 'event',
    ('展覧会・イベント', '物産展'): 'event',
    ('展覧会・イベント', '展覧会'): 'art',
    ('展覧会・イベント', 'お祭り'): 'event',
    ('展覧会・イベント', '花火大会'): 'hanabi',
    ('展覧会・イベント', '街コン'): 'event',
    ('展覧会・イベント', '食フェス'): 'gourmet',
    ('展覧会・イベント', 'アート'): 'art',
    ('展覧会・イベント', '学園祭'): 'gakusai',
    ('展覧会・イベント', 'トークショー'): 'talkshow',
    ('展覧会・イベント', '展覧会・イベントその他'): 'event',
    ('展覧会・イベント', ''): 'event',
}
for _s in ('野球', 'サッカー', 'ラグビー', 'バレーボール', 'プロレス', 'ボクシング', '格闘技', 'eスポーツ',
           'ハンドボール', 'バスケットボール', 'スポーツその他'):
    CAT_GENRE[('スポーツ', _s)] = 'sports'
for _s in ('動物園', '水族館', 'カードゲーム', 'ゲーム', '釣り', '脱出ゲーム', 'ファッション・美容', 'コスプレ',
           '趣味・カルチャー・レジャーその他'):
    CAT_GENRE[('趣味・カルチャー・レジャー', _s)] = 'event'
GENRE_FALLBACK = 'musicetc'

# 🚫推しに会いに行く枠ではないカテゴリ＝TIGETの CAT_SKIP（62〜65 セミナー・71 ジム/トレーニング）と同じ線
CAT_SKIP = {('展覧会・イベント', 'セミナー'): 'セミナー',
            ('趣味・カルチャー・レジャー', 'ジム'): 'ジム',
            ('趣味・カルチャー・レジャー', 'ヨガ・フィットネス'): 'ヨガ・フィットネス'}

# ⚠️載せるが人が見たほうがいい型（判断がつきにくい）＝除外しない。報告に出す
REVIEW_CAT = {('アニメ・キャラ', 'コラボカフェ'): 'コラボカフェ',
              ('アニメ・キャラ', 'グッズ'): 'グッズ', ('ファン・アイドル', 'グッズ'): 'グッズ',
              ('趣味・カルチャー・レジャー', 'カードゲーム'): 'カードゲーム',
              ('展覧会・イベント', '街コン'): '街コン', ('展覧会・イベント', '物産展'): '物産展',
              ('趣味・カルチャー・レジャー', '動物園'): '動物園', ('趣味・カルチャー・レジャー', '水族館'): '水族館',
              ('趣味・カルチャー・レジャー', '釣り'): '釣り'}
REVIEW_NAME = re.compile(r'POP ?UP|ポップアップ|来店予約|抽選販売|通販|見学会|セミナー|講座|アクセサリー|'
                         r'ミニチュア|ガチャ|カフェ|CAFE|Cafe')

# 🚨出す側の申込は載せない（[[feedback_oshinavi_concept]]・2026-09-18 ユーザー決定）。
#   駐車は 2026-09-22 ユーザー決定で「載せる」＝ここには入れない。
#   ⚠️「ブース」単独は入れない（「特殊メイクブース・事前予約チケット」は来場者が申し込む側＝2026-09-28 実例）
SELLER_SIDE = re.compile(
    r'委託販売|即売会|出店|出展|ブース(?:出展|出店|申込)|サークル参加|'
    r'エントリーフォーム|参加エントリ|出場エントリ|出演エントリ|出演者募集|出演申込|'
    r'案内登録|先行案内'
)
# 「配信なし」「配信無し」は配信ではない（会場だけの券）
STREAM = re.compile(r'配信(?!なし|無し)|視聴(?!覚)|アーカイブ')
ONLINE_VENUE = re.compile(r'^\s*(オンライン|配信|Zoom|ツイキャス|YouTube|ONLINE|Online)', re.I)

LIVE_CARD = ('販売中', '売切間近')
SOLD_CARD = ('予定販売数終了', '予定販売枚数終了')
CLOSED_CARD = ('受付終了', '販売終了')


def era(y, today_year):
    return 'R%d年 ' % (y - 2018) if y > today_year else ''


def md(iso, today_year=None):
    """公演日のバッジ用＝翌年以降は令和略記（[[feedback_r9_year_notation]]・ZAIKOビルダーと同じ）。"""
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return '%s%d/%d' % (era(y, today_year or datetime.date.today().year), m, d)


def mdp(iso):
    """発売日・締切用＝年を付けない（既存の流儀＝ZAIKOビルダーの mdp と同じ）。"""
    return '%d/%d' % (int(iso[5:7]), int(iso[8:10]))


def jp(iso):
    y, m, d = int(iso[:4]), int(iso[5:7]), int(iso[8:10])
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


_PAIRS = ('（）', '「」', '『』', '【】', '＜＞', '〔〕', '［］', '〈〉')


def _balanced(s):
    return all(s.count(a) == s.count(b) for a, b in _PAIRS)


def ticket_name(raw, suffix=''):
    """受付名を整える。記号を check_badges が通す形にそろえ、28字で切る（カッコの途中で切らない）。
    🚨足す札（「（配信）」など）は**切った後に**足す（2026-09-28 朝 ZAIKOで、先に足して切り落とされ
       配信の例外が効かず締切が公演日に丸まった穴と同じにしない）。"""
    nm = re.sub(r'\s+', ' ', (raw or '')).strip()
    nm = re.sub(r'\s*\d{4}年\d{1,2}月\d{1,2}日.*$', '', nm).strip()
    # ⚠️半角「/」は変えない（「9/29(火)」の日付が「9・29」に化けた＝2026-09-28 初版）
    nm = (nm.replace('／', '・').replace('(', '（').replace(')', '）')
            .replace('[', '［').replace(']', '］').replace('～', '〜'))
    if not nm or re.fullmatch(r'[・\s]*', nm):
        nm = 'チケット'
    if suffix and suffix.strip('（）') in nm:
        suffix = ''
    cut = nm[:28 - len(suffix)]
    while cut and not _balanced(cut):
        cut = cut[:-1]
    cut = cut.rstrip('・、 ')
    return (cut or 'チケット') + suffix


def slot_state(rec):
    """受付の札と券種の札から、枠の状態を1語で返す（unopened/live/soldout/closed/unknown）。"""
    rs = (rec.get('status') or '').strip()
    cs = [(c.get('status') or '').strip() for c in (rec.get('cards') or [])]
    if rs == '販売前':
        return 'unopened'
    if rs == '販売中':
        if not cs or any(c in LIVE_CARD for c in cs):
            return 'live'
        if all(c == '販売前' for c in cs):
            return 'unopened'
        if all(c in SOLD_CARD for c in cs):
            return 'soldout'
        if all(c in SOLD_CARD + CLOSED_CARD for c in cs):
            return 'closed' if all(c in CLOSED_CARD for c in cs) else 'soldout'
        return 'unknown'
    if rs in ('予定販売枚数終了', '予定販売数終了', '売切'):
        return 'soldout'
    if rs in ('販売終了', '受付終了'):
        return 'closed'
    return 'unknown'


def cats_of(ev):
    """l_cat/s_cat の組を、小分類があるものを先に返す（大分類だけの札は親のリンク）。"""
    cs = [tuple(c) for c in (ev.get('cats') or [])]
    return [c for c in cs if c[1]] + [c for c in cs if not c[1]]


def is_stream_reception(ev, rec):
    """配信の受付か＝受付名か券種名に配信・視聴・アーカイブ、または会場がオンライン（build の（配信）の札と同じ線）。"""
    return bool(STREAM.search(rec.get('title') or '')
                or any(STREAM.search(c.get('name') or '') for c in rec.get('cards') or [])
                or ONLINE_VENUE.search(ev.get('venue') or ''))


def live_stream_reception(ev, today):
    """🆕2026-09-30 買える配信の受付があるか（公演日が過ぎても載せ続ける判定＝ZAIKOのスタリオンと同じ穴）。
    配信の受付で、販売中（買える券種あり）／販売前、締切が今日以降。締切が読めない受付は「買える」と言わない。"""
    for r in ev.get('receptions') or []:
        if slot_state(r) not in ('live', 'unopened') or not is_stream_reception(ev, r):
            continue
        if SELLER_SIDE.search(r.get('title') or ''):
            continue
        en = (r.get('period') or {}).get('end')
        if en and en[0] >= today:
            return True
    return False


# 🆕2026-09-30 配信は見出しに「いつまで見られるか」を書く（ユーザー「配信はいつまで配信かを書かなきゃないよ」）。
#   🚨livePocket のページには**視聴期間の欄が無い**（受付の期間＝売る期限しか無い）。
#   ＝配信の受付の中で、主催者が**受付名・注記・券種名・券種の説明に自分で書いた視聴の終わり**だけを読む
#   （2026-09-30 実測＝取得済み1,184ページの配信の受付で、日付つきで書いてあったのは0件。
#    「配信視聴付（1週間）」のような相対の書き方はあった＝日付を作らないので読まない）。
#   ⛔受付の締切（period.end）を視聴の終わりにしない。
VIEW_UNTIL_RE = re.compile(
    r'(アーカイブ|見逃し|視聴)([^。]{0,24}?)(?:(\d{1,2})/(\d{1,2})|(\d{1,2})月(\d{1,2})日)\s*'
    r'(?:[（(][^）)]{1,3}[）)])?\s*(?:(\d{1,2})[:：](\d{2}))?\s*(?:まで|迄)(?!に|販売|受付|購入|発売|申込)')
NOT_VIEW = re.compile(r'販売|受付|購入|発売|申込')


def view_until_in_text(txt, show_date):
    """文字列に書かれた視聴の終わり（「アーカイブ…10/12 23:59まで」）→ (YYYY-MM-DD, 'H:MM' or '')。無ければ None。
    年は書いていないので公演日の年（公演日より前の月日なら翌年）。"""
    best = None
    for m in VIEW_UNTIL_RE.finditer(re.sub(r'\s+', ' ', txt or '')):
        if NOT_VIEW.search(m.group(2)):
            continue                      # 「視聴チケットの販売は10/5まで」＝売る期限なので読まない
        mo, dd = int(m.group(3) or m.group(5)), int(m.group(4) or m.group(6))
        y = int(show_date[:4])
        try:
            c = datetime.date(y, mo, dd)
            if c.isoformat() < show_date:
                c = datetime.date(y + 1, mo, dd)
        except ValueError:
            continue
        hm = '%d:%s' % (int(m.group(7)), m.group(8)) if m.group(7) else ''
        cand = (c.isoformat(), hm)
        best = max(best, cand) if best else cand
    return best


def stream_until(ev, last):
    """配信の受付に書かれた視聴の終わり（いちばん遅いもの）。取れなければ None。"""
    best = None
    for r in ev.get('receptions') or []:
        if not is_stream_reception(ev, r) or SELLER_SIDE.search(r.get('title') or ''):
            continue
        txts = [r.get('title') or '', r.get('note') or '']
        for c in r.get('cards') or []:
            txts += [c.get('name') or '', c.get('text') or '']
        for t in txts:
            u = view_until_in_text(t if isinstance(t, str) else json.dumps(t, ensure_ascii=False), last)
            if u:
                best = max(best, u) if best else u
    return best


def stream_label(base, last, until):
    """見出しに「（配信は M月D日(曜) HH:MMまで）」を添える。配信の終わりが公演日（最終日）より後の時だけ。"""
    if not until or until[0] <= last:
        return base
    return '%s（配信は%sまで）' % (base, (jp(until[0])[5:] + ' ' + until[1]).strip())


def build(ev, today, unknown=None):
    """1ページ＝1エントリ。載せられないときは (None, 理由)。"""
    unknown = unknown if unknown is not None else collections.Counter()
    name = re.sub(r'\s+', ' ', ev.get('name') or '').strip()
    if not name:
        return None, '公演名が読めない'
    if SELLER_SIDE.search(name):
        return None, '出す側の申込（出店・出展・出演エントリー・案内登録）'
    cats = cats_of(ev)
    for c in cats:
        if c in CAT_SKIP:
            return None, 'カテゴリ「%s」＝推しに会いに行く枠ではない（TIGETのCAT_SKIPと同じ線）' % CAT_SKIP[c]
    dates = sorted(set(ev.get('dates') or []))
    if not dates:
        return None, '開催日が読めない'
    first, last = dates[0], dates[-1]
    # 🚨2026-09-30 配信は公演日（配信開始）が過ぎても視聴券が売られている（ZAIKO 24618 スタリオン＝
    #   9/28 22:00開始・10/5 23:59まで）。ここで捨てると番人も「公演が終わった＝正常」と読んでしまう
    #   （ユーザー「ゲートが間違えてる」）。買える配信の受付があれば捨てず、締切が今日以降の配信の枠だけ出す。
    past = last < today
    if past and not live_stream_reception(ev, today):
        return None, '公演が終わっている'
    if first > (datetime.date.fromisoformat(today) + datetime.timedelta(days=730)).isoformat():
        return None, '公演日が2年より先＝主催者の試し書きの疑い'

    ty = int(today[:4])
    pref = ev.get('prefecture') or ''
    stime = ev.get('start_time') or ''
    slabel = ev.get('start_label') or ('開演時間' if stime else '')
    if len(dates) == 1 or first == last:
        when = '%s %s公演' % (md(first, ty), stime) if stime else '%s公演' % md(first, ty)
        # 見出しが「開演時間」のときだけ「開演」と書く（主催者の自由な見出し＝WUCA 15:00 などは時刻だけ）
        label = jp(first) + ((' %s開演' % stime if slabel == '開演時間' else ' %s' % stime) if stime else '')
    else:
        # 会期が続く型（コラボカフェ・通販・複数日の公演）＝本当の初日〜最終日（[[feedback_show_true_dates_not_sellable_range]]）
        when = '%s〜%s' % (md(first, ty), md(last, ty))
        label = '%s〜%s' % (jp(first), jp(last))
    url = ev['url']

    tickets, skipped_slots, has_live = [], [], False
    # 🆕2026-09-28 夜 独立ゲートが発見＝同じ名前の受付が日付ごとに並ぶ型（ClueMetic Popup＝「先着販売受付」×4）を
    #   同じ札の枠として1つに畳み、受付3つと売切の印が落ちていた。同名の受付が2つ以上ある時は、券種名の頭の日付
    #   （「10/22(木) 14ː00〜」）を受付名に添えて別の枠にする。日付が無ければ「その2」…で分ける。
    #   🆕同じ夜 サイドチェックが追加で発見＝日付の無い型（AETHER CROSS＝VIP/一般/U-25・MERA撮影会＝2部/4部/5部…）
    #   ＝同名の受付どうしで共通の頭を落とした券種名（「VIP」「5部・6部」）を添える。
    title_n = collections.Counter((r.get('title') or '') for r in (ev.get('receptions') or []))
    title_seen = collections.Counter()
    title_tails = collections.defaultdict(set)
    same_cards = collections.defaultdict(list)
    for r in ev.get('receptions') or []:
        same_cards[r.get('title') or ''] += [re.sub(r'\s+', ' ', c.get('name') or '').strip() for c in r.get('cards') or []]

    def card_tail(raw, cards):
        names = [re.sub(r'\s+', ' ', c.get('name') or '').strip() for c in cards]
        pool = [n for n in same_cards[raw] if n]
        pre = ''
        if len(pool) > 1:
            pre = pool[0]
            for n in pool[1:]:
                while pre and not n.startswith(pre):
                    pre = pre[:-1]
        tails = [n[len(pre):].strip() for n in names if n[len(pre):].strip()]
        return '・'.join(dict.fromkeys(tails))
    for rec in ev.get('receptions') or []:
        cards = rec.get('cards') or []
        raw = rec.get('title') or ''
        if title_n[raw] > 1:
            title_seen[raw] += 1
            dm = [re.match(r'\s*(\d{1,2}/\d{1,2})\s*[(（]\s*([月火水木金土日祝・]+)\s*[)）]', c.get('name') or '') for c in cards]
            ds = sorted({'%s（%s）' % (x.group(1), x.group(2)) for x in dm if x})
            tail = ds[0] if len(ds) == 1 else card_tail(raw, cards)
            # 長い（券種がずらっと並ぶ型＝YOKOHAMA SONIC）・空・前と同じ なら「その2」…＝28字で切れて同じ枠に潰れるのを防ぐ
            # 🆕2026-10-01 券種が1枚だけなら 24字まで名前をそのまま使う（ユーザー指摘＝上野deソロソロ lr3mh で
            #   「カメラ撮影可能席(前方１列目)」16字が「その2」になり、どの席が16:15までか分からなかった）
            if not tail or len(tail) > (24 if len(cards) == 1 else 12) or tail in title_tails[raw]:
                tail = 'その%d' % title_seen[raw]
            title_tails[raw].add(tail)
            raw = '%s %s' % (raw, tail)
        if SELLER_SIDE.search(raw) or (cards and all(SELLER_SIDE.search(c.get('name') or '') for c in cards)):
            skipped_slots.append((raw, '出す側の受付'))
            continue
        # 券種に配信があれば（配信）を添える＝締切を公演日で締めない例外に乗せる
        # 🆕2026-09-28 「全部配信」だけだと、会場券＋視聴券の受付や会場「オンライン」の公演で配信と出なかった
        #   （生データ突合で3件＝せんのさん in Zoom・East Mouth Meeting ×2）＝1枚でも配信か、会場がオンラインなら添える
        any_stream = (any(STREAM.search(c.get('name') or '') for c in cards)
                      or bool(ONLINE_VENUE.search(ev.get('venue') or '')))
        nm = ticket_name(raw, '（配信）' if (any_stream and not STREAM.search(raw)) else '')
        is_stream = bool(STREAM.search(nm))
        head = '%s（%s %s）' % (nm, pref, when) if pref else '%s（%s）' % (nm, when)
        per = rec.get('period') or {}
        st, en = per.get('start'), per.get('end')

        def cap(e):
            if e and e[0] > last and not is_stream:
                return (last, '')
            return e
        state = slot_state(rec)
        if state == 'unopened':
            if not st:
                skipped_slots.append((raw, '発売前なのに開始日時が読めない＝日付を作らない'))
                continue
            e2 = cap(en) if en else (last, '')
            tickets.append({'type': ('%s%s %s発売〜%s %s' % (head, mdp(st[0]), st[1], mdp(e2[0]), e2[1]))
                                    .replace('  ', ' ').rstrip(),
                            'date': e2[0], 'startDate': st[0], 'url': url})
            has_live = True
        elif state == 'live':
            if en:
                e2 = cap(en)
                tickets.append({'type': ('%s〜%s %s' % (head, mdp(e2[0]), e2[1])).rstrip(),
                                'date': e2[0], 'url': url})
            else:
                # 🚨締切が書いていない販売中＝TIGETと同じ「〜公演日」の販売中（2026-09-27 ユーザー決定）
                tickets.append({'type': '%s〜%s' % (head, mdp(last)), 'date': last, 'url': url})
            has_live = True
        elif state in ('soldout', 'closed'):
            # 印の枠は締切を作らない＝締切が書いてあればそれを、無ければ公演日を置き場に（TIGETと同じ）
            e2 = cap(en) if en else None
            tk = {'type': ('%s〜%s %s' % (head, mdp(e2[0]), e2[1])).rstrip() if e2 else head,
                  'date': e2[0] if e2 else last, 'url': url, 'soldout': True, 'soldoutSince': today}
            if state == 'closed':
                tk['saleEnded'] = True
                tk['saleEndedSince'] = today
            tickets.append(tk)
        else:
            unknown[(rec.get('status'), tuple(sorted({c.get('status') for c in cards})))] += 1
            skipped_slots.append((raw, '読めない札 受付=%s 券種=%s' % (rec.get('status'),
                                                                   '/'.join(sorted({c.get('status') or '' for c in cards})))))
    if past:
        # 公演日が過ぎた＝締切が今日以降の配信の枠だけ残す（配信でない受付・締切が過ぎた配信は従来どおり出さない）
        tickets = [t for t in tickets if (t.get('date') or '') >= today and STREAM.search(t.get('type') or '')]
    seen, uniq = set(), []
    for t in tickets:
        k = (t.get('type'), t.get('date'), t.get('startDate'), t.get('url'),
             bool(t.get('soldout')), bool(t.get('saleEnded')))
        if k in seen:
            continue
        seen.add(k)
        uniq.append(t)
    if not uniq:
        why = '枠が読めない（受付欄なし）' if not ev.get('receptions') else '載せられる枠が無い'
        if skipped_slots:
            why += '：' + skipped_slots[0][1]
        return None, why

    genres = []
    for c in cats:
        g = CAT_GENRE.get(c)
        if g is None:
            unknown[('カテゴリ',) + c] += 1
            continue
        if g not in genres:
            genres.append(g)
    review = []
    for c in cats:
        if c in REVIEW_CAT and REVIEW_CAT[c] not in review:
            review.append(REVIEW_CAT[c])
    mm = REVIEW_NAME.search(name)
    if mm and mm.group(0) not in review:
        review.append(mm.group(0))
    perf = [p for p in (ev.get('performers') or []) if p]
    e = {
        'artist': '／'.join(perf[:3]) if perf else name,
        'name': name,
        'date': last,
        'dateLabel': stream_label(label, last, stream_until(ev, last)),
        'venue': ev.get('venue') or '（会場未定）',
        'prefecture': pref,
        'genre': 'new',
        '_genre': genres[0] if genres else GENRE_FALLBACK,
        '_extraGenres': genres[1:],
        '_srcgenre': 'livepocket:' + ','.join('/'.join(x for x in c if x) for c in cats),
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'livepocket': url},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
    }
    if review:
        e['_review'] = review
    if skipped_slots:
        e['_skipped_slots'] = skipped_slots
    e['_has_live'] = has_live
    return e, None


def _selftest():
    today = '2026-09-28'

    def rec(status='販売中', title='先着販売受付', order='先着', start=('2026-09-20', '20:00'),
            end=('2026-11-24', '23:59'), cards=None):
        return {'status': status, 'order': order, 'title': title,
                'period': {'start': start, 'end': end, 'text': ''},
                'cards': cards if cards is not None else [{'name': '前売', 'status': status, 'price': 3000}]}

    def ev(recs, **kw):
        d = {'id': 'x', 'url': 'https://livepocket.jp/e/x', 'name': 'テストライブ', 'dates': ['2026-11-25'],
             'start_time': '19:30', 'venue': 'LOFT9 Shibuya', 'prefecture': '東京',
             'performers': ['虹の黄昏', '空気階段'], 'cats': [['展覧会・イベント', ''], ['展覧会・イベント', 'トークショー']],
             'receptions': recs}
        d.update(kw)
        return d
    # ① 販売中＝「〜締切」・date＝締切・startDate なし
    e, _ = build(ev([rec()]), today)
    t = e['tickets'][0]
    assert t['type'] == '先着販売受付（東京 11/25 19:30公演）〜11/24 23:59' and t['date'] == '2026-11-24', t
    assert 'startDate' not in t and e['_genre'] == 'talkshow' and e['artist'] == '虹の黄昏／空気階段', (t, e)
    assert e['links']['livepocket'] == 'https://livepocket.jp/e/x' and e['genre'] == 'new'
    assert e['dateLabel'] == '2026年11月25日(水) 19:30開演', e['dateLabel']
    # ② 販売前＝「発売〜締切」・date＝締切（発売日にしない＝翌0時に消える穴）
    e, _ = build(ev([rec('販売前', start=('2026-09-28', '20:00'), end=('2026-11-25', '0:00'))]), today)
    t = e['tickets'][0]
    assert t['type'] == '先着販売受付（東京 11/25 19:30公演）9/28 20:00発売〜11/25 0:00', t
    assert t['startDate'] == '2026-09-28' and t['date'] == '2026-11-25', t
    # ②-2 販売前で締切なし＝「発売〜公演日」date＝公演日
    e, _ = build(ev([rec('販売前', start=('2026-10-01', '10:00'), end=None)]), today)
    assert e['tickets'][0]['type'].endswith('10/1 10:00発売〜11/25') and e['tickets'][0]['date'] == '2026-11-25', e['tickets']
    # ②-3 販売前で開始が読めない＝載せない（推測しない）
    r, why = build(ev([rec('販売前', start=None)]), today)
    assert r is None and '開始日時が読めない' in why, why
    # ③ 販売中で開始が消えた形（〜締切だけ）も同じ
    e, _ = build(ev([rec(start=None)]), today)
    assert e['tickets'][0]['type'].endswith('〜11/24 23:59'), e['tickets']
    # ③-2 締切が書いていない販売中＝「〜公演日」の販売中（TIGETと同じ決まり）
    e, _ = build(ev([rec(end=None)]), today)
    t = e['tickets'][0]
    assert t['type'] == '先着販売受付（東京 11/25 19:30公演）〜11/25' and t['date'] == '2026-11-25', t
    assert 'saleEndUnknown' not in t and 'startDate' not in t
    # ④ 券種が全部 予定販売数終了＝予定枚数終了（soldout だけ）
    e, _ = build(ev([rec(cards=[{'name': 'A', 'status': '予定販売数終了'}])]), today)
    t = e['tickets'][0]
    assert t['soldout'] and not t.get('saleEnded'), t
    e, _ = build(ev([rec('予定販売枚数終了', cards=[{'name': 'A', 'status': '予定販売数終了'}])]), today)
    assert e['tickets'][0]['soldout'] and not e['tickets'][0].get('saleEnded')
    # ⑤ 販売終了＝soldout＋saleEnded（公演がこれからなら載せる）
    e, _ = build(ev([rec('販売終了', end=('2026-09-20', '23:59'), cards=[{'name': 'A', 'status': '受付終了'}])]), today)
    t = e['tickets'][0]
    assert t['soldout'] and t['saleEnded'] and t['date'] == '2026-09-20', t
    # ⑥ 一部が売切間近・一部が予定販売数終了＝買える
    e, _ = build(ev([rec(cards=[{'name': 'A', 'status': '売切間近'}, {'name': 'B', 'status': '予定販売数終了'}])]), today)
    assert not e['tickets'][0].get('soldout'), e['tickets']
    # ⑦ 読めない札＝枠を作らない（推測しない）
    r, why = build(ev([rec('謎の札', cards=[{'name': 'A', 'status': '謎'}])]), today)
    assert r is None and '読めない札' in why, why
    # ⑧ 締切が公演日より後なら公演日で締める。配信は例外＝（配信）は切った後に足す
    e, _ = build(ev([rec(end=('2026-12-05', '23:59'))]), today)
    assert e['tickets'][0]['date'] == '2026-11-25' and e['tickets'][0]['type'].endswith('〜11/25'), e['tickets']
    long_title = 'とても長い受付の名前がここに入りますよ見逃し付きの特別な版ですよほげほげ'
    e, _ = build(ev([rec(title=long_title, end=('2026-12-05', '23:59'),
                         cards=[{'name': '見逃し配信チケット', 'status': '販売中'}])]), today)
    t = e['tickets'][0]
    assert '（配信）' in t['type'] and t['date'] == '2026-12-05', t
    assert len(t['type'].split('（東京')[0]) <= 28, t['type']
    # ⑨ 出す側は載せない（名前・受付）。特殊メイクブースの予約（来場者側）は巻き添えにしない
    assert build(ev([rec()], name='ハロウィンフェス 出店者募集・出店申込'), today)[0] is None
    assert build(ev([rec()], name='対バン 出演エントリー'), today)[0] is None
    assert build(ev([rec()], name='ZOMBIE FES 2026特殊メイクブース・事前予約チケット'), today)[0] is not None
    e, _ = build(ev([rec(title='出店ブース申込'), rec(title='一般入場')]), today)
    assert [x['type'].split('（')[0] for x in e['tickets']] == ['一般入場'], e['tickets']
    # ⑩ セミナー・ジムは載せない（TIGETと同じ線）
    r, why = build(ev([rec()], cats=[['展覧会・イベント', ''], ['展覧会・イベント', 'セミナー']]), today)
    assert r is None and 'セミナー' in why, why
    # ⑪ コラボカフェは載せる＋_review に印
    e, _ = build(ev([rec()], cats=[['アニメ・キャラ', ''], ['アニメ・キャラ', 'コラボカフェ']]), today)
    assert e and e['_genre'] == 'anime' and 'コラボカフェ' in e['_review'], e
    # ⑫ 会期が続く型＝本当の初日〜最終日、締切の上限は最終日
    e, _ = build(ev([rec(end=('2026-11-20', '23:59'))], dates=['2026-09-27', '2026-11-03']), today)
    assert e['date'] == '2026-11-03' and e['dateLabel'] == '2026年9月27日(日)〜2026年11月3日(火)', e['dateLabel']
    assert e['tickets'][0]['type'] == '先着販売受付（東京 9/27〜11/3）〜11/3' and e['tickets'][0]['date'] == '2026-11-03', e['tickets']
    # ⑬ 公演が終わっている／2年より先／受付欄なし
    assert build(ev([rec()], dates=['2026-09-27']), today)[0] is None
    assert build(ev([rec()], dates=['2029-01-01']), today)[0] is None
    r, why = build(ev([]), today)
    assert r is None and '受付欄なし' in why, why
    # ⑭ 県が無い（「(その他)」）＝バッジから県を落とす
    e, _ = build(ev([rec()], prefecture=None), today)
    assert e['tickets'][0]['type'].startswith('先着販売受付（11/25 19:30公演）'), e['tickets']
    # ⑮ 翌年の公演はR9年（締切側は年なし）
    e, _ = build(ev([rec(end=('2027-01-10', '23:59'))], dates=['2027-01-11']), today)
    assert 'R9年 1/11 19:30公演）〜1/10 23:59' in e['tickets'][0]['type'], e['tickets']
    # ⑯ 券種名の記号＝全角／と半角カッコをそろえる・カッコの途中で切らない
    assert ticket_name('A／B(スタンディング)') == 'A・B（スタンディング）'
    assert _balanced(ticket_name('【対象者様限定】ファンミーティング参加チケット【特定クラスタ様向け】'))
    assert ticket_name('') == 'チケット'
    assert ticket_name('【物販】9/29(火) カフェ') == '【物販】9/29（火） カフェ'        # 半角/の日付を化けさせない
    assert not STREAM.search('会場チケット（配信なし）') and STREAM.search('配信チケット')
    e, _ = build(ev([rec()], start_time='15:00', start_label='WUCA'), today)
    assert e['dateLabel'] == '2026年11月25日(水) 15:00' and '11/25 15:00公演' in e['tickets'][0]['type'], e
    # ⑰ 抽選の受付
    e, _ = build(ev([rec(title='抽選販売受付 大阪', order='抽選')]), today)
    assert e['tickets'][0]['type'].startswith('抽選販売受付 大阪（'), e['tickets']
    # ⑱ 同じ受付名・同じ期間・同じ状態は1つに畳む
    e, _ = build(ev([rec(), rec()]), today)
    assert len(e['tickets']) == 2 and e['tickets'][0]['type'] != e['tickets'][1]['type'], e['tickets']
    # ⑲ 同じ名前・同じ締切の受付が日付ごとに並ぶ型（ClueMetic Popup・9/28夜）＝券種名の頭の日付で分ける・売切の印を落とさない
    e, _ = build(ev([rec(cards=[{'name': '10/22(木) 14ː00～14ː30', 'status': '予定販売数終了'}]),
                     rec(cards=[{'name': '10/23(金)11:00 ～ 11:30', 'status': '販売中'}])],
                    dates=['2026-10-22', '2026-10-25']), today)
    ts = e['tickets']
    assert len(ts) == 2 and '10/22（木）' in ts[0]['type'] and ts[0]['soldout'] and '10/23（金）' in ts[1]['type'] \
        and not ts[1].get('soldout'), ts
    # ⑳ 日付の無い同名受付（VIP/一般・5部6部/4部）＝券種名の違う所を添える
    e, _ = build(ev([rec('販売前', cards=[{'name': 'VIP', 'status': '販売前'}]),
                     rec('販売前', cards=[{'name': '一般', 'status': '販売前'}])]), today)
    assert [t['type'].split('（')[0] for t in e['tickets']] == ['先着販売受付 VIP', '先着販売受付 一般'], e['tickets']
    e, _ = build(ev([rec(cards=[{'name': 'MERA撮影会 吉瀬結(団体) 5部', 'status': '予定販売数終了'},
                                {'name': 'MERA撮影会 吉瀬結(団体) 6部', 'status': '予定販売数終了'}]),
                     rec(cards=[{'name': 'MERA撮影会 吉瀬結(団体) 2部', 'status': '売切間近'}])]), today)
    assert e['tickets'][0]['type'].startswith('先着販売受付 5部・6部') and e['tickets'][0]['soldout'], e['tickets']
    assert e['tickets'][1]['type'].startswith('先着販売受付 2部') and not e['tickets'][1].get('soldout'), e['tickets']
    # ㉑ 🆕2026-09-30 スタリオン型＝公演日（配信開始）は過去・配信の受付の締切は未来 → 捨てない（ZAIKOと同じ穴）
    t30 = '2026-09-30'
    st_rec = rec(title='配信チケット受付', end=('2026-10-05', '23:59'), cards=[{'name': '視聴チケット', 'status': '販売中'}])
    venue_rec = rec(title='会場チケット受付', end=('2026-09-28', '18:00'))
    e, why = build(ev([st_rec, venue_rec], dates=['2026-09-28']), t30)
    assert e, why
    assert [(t['type'], t['date']) for t in e['tickets']] == \
        [('配信チケット受付（東京 9/28 19:30公演）〜10/5 23:59', '2026-10-05')], e['tickets']   # 会場券は落ちる
    assert e['date'] == '2026-09-28' and e['dateLabel'].startswith('2026年9月28日'), e
    # 券種名だけが配信（受付名は普通）の形・販売前の配信も同じ
    e, _ = build(ev([rec(end=('2026-10-05', '23:59'), cards=[{'name': 'アーカイブ視聴', 'status': '販売中'}])],
                    dates=['2026-09-28']), t30)
    assert e and '（配信）' in e['tickets'][0]['type'] and e['tickets'][0]['date'] == '2026-10-05', e
    e, _ = build(ev([rec('販売前', title='見逃し配信', start=('2026-10-01', '10:00'), end=('2026-10-05', '23:59'),
                         cards=[{'name': '視聴', 'status': '販売前'}])], dates=['2026-09-28']), t30)
    assert e and e['tickets'][0]['startDate'] == '2026-10-01' and e['tickets'][0]['date'] == '2026-10-05', e
    # 配信でない受付・売り切れの配信・販売終了の配信・締切が過ぎた配信・締切の無い配信は、従来どおり捨てる
    for r0 in (rec(end=('2026-10-05', '23:59')),
               dict(st_rec, cards=[{'name': '視聴チケット', 'status': '予定販売数終了'}]),
               dict(st_rec, status='販売終了', cards=[{'name': '視聴チケット', 'status': '受付終了'}]),
               dict(st_rec, period={'start': ('2026-09-20', '20:00'), 'end': ('2026-09-29', '23:59'), 'text': ''}),
               dict(st_rec, period={'start': ('2026-09-20', '20:00'), 'end': None, 'text': ''})):
        r, why = build(ev([r0], dates=['2026-09-28']), t30)
        assert r is None and why == '公演が終わっている', (r0, r, why)
    # 過ぎた公演に締切が未来の売切れ会場券が混ざっても出さない
    e, _ = build(ev([st_rec, rec(title='VIP', end=('2026-10-05', '23:59'), cards=[{'name': 'VIP', 'status': '予定販売数終了'}])],
                    dates=['2026-09-28']), t30)
    assert len(e['tickets']) == 1, e['tickets']
    # ㉒ 🆕2026-09-30 配信は見出しに「いつまで見られるか」を書く（配信の受付に主催者が書いた視聴の終わりだけ読む）
    sv = rec(title='配信チケット受付', end=('2026-11-24', '23:59'),
             cards=[{'name': '配信視聴チケット', 'status': '販売中', 'text': 'アーカイブ視聴は12/2(水) 23:59までご覧いただけます。'}])
    e, _ = build(ev([sv]), today)
    assert e['dateLabel'] == '2026年11月25日(水) 19:30開演（配信は12月2日(水) 23:59まで）', e['dateLabel']
    sv2 = dict(sv, note='見逃し配信は12月9日まで')                      # 受付の注記・時刻なし・遅いほう
    assert build(ev([sv2]), today)[0]['dateLabel'] == '2026年11月25日(水) 19:30開演（配信は12月9日(水)まで）'
    # 会場だけの受付には、説明に日付があっても添えない
    e, _ = build(ev([rec(cards=[{'name': '前売', 'status': '販売中', 'text': 'アーカイブ視聴は12/2(水) 23:59まで'}])]), today)
    assert e['dateLabel'] == '2026年11月25日(水) 19:30開演', e['dateLabel']
    # 視聴の終わりが書いていない配信（受付の締切 11/24 や「1週間」から作らない）・売る期限の書き方は添えない
    for c in ({'name': '配信視聴チケット', 'status': '販売中', 'text': '配信視聴付（1週間）'},
              {'name': '配信視聴チケット', 'status': '販売中', 'text': '視聴チケットの販売は12/2まで'},
              {'name': '配信視聴チケット', 'status': '販売中', 'text': 'アーカイブ配信URLは12/2までにお送りします'}):
        e, _ = build(ev([dict(sv, cards=[c])]), today)
        assert '配信は' not in e['dateLabel'], (c, e['dateLabel'])
    # 終わりが公演日より前・同じ日なら添えない／会期の型は最終日より後の時だけ
    e, _ = build(ev([dict(sv, note='アーカイブ 11/25 23:59まで')]), today)
    assert e['dateLabel'] == '2026年11月25日(水) 19:30開演（配信は12月2日(水) 23:59まで）', e['dateLabel']
    e, _ = build(ev([dict(sv, cards=[dict(sv['cards'][0], text='アーカイブ 11/25 23:59まで')])]), today)
    assert '配信は' not in e['dateLabel'], e['dateLabel']
    e, _ = build(ev([sv], dates=['2026-11-20', '2026-11-25']), today)
    assert e['dateLabel'] == '2026年11月20日(金)〜2026年11月25日(水)（配信は12月2日(水) 23:59まで）', e['dateLabel']
    print('selftest OK: slot_state/build/ticket_name/販売前の締切/〜公演日/売切/販売終了/出す側/配信の札/配信の公演後/配信の見出し')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?')
    ap.add_argument('--out', default='tmp/built_livepocket.json')
    ap.add_argument('--today', default=datetime.date.today().isoformat())
    ap.add_argument('--report', default='tmp/build_livepocket_report.txt')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        return 0
    if not a.src:
        ap.error('ハーベスト結果のJSONを渡して（例 tmp/livepocket_0928.json）')
    d = json.load(io.open(a.src, encoding='utf-8'))
    unknown = collections.Counter()
    out, skipped = [], []
    for ev in d['events']:
        e, why = build(ev, a.today, unknown)
        if e:
            out.append(e)
        else:
            skipped.append({'id': ev['id'], 'name': ev.get('name'), 'why': why, 'url': ev['url']})
    live = sum(1 for e in out if e.pop('_has_live', False))
    json.dump({'entries': out, 'skipped': skipped}, io.open(a.out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== build_livepocket (today=%s) %s ===\n' % (a.today, a.src))
    rep.write('組み上がり %d件（うち買える・発売前の枠あり %d件）/ 載せない %d件 / 枠 %d\n'
              % (len(out), live, len(skipped), sum(len(e['tickets']) for e in out)))
    why = collections.Counter(re.sub(r'：.*$', '', s['why']) for s in skipped)
    rep.write('\n--- 載せない理由 ---\n')
    for k, v in why.most_common():
        rep.write('  %d\t%s\n' % (v, k))
    rep.write('\n--- 載せない（全件）---\n')
    for s in skipped:
        rep.write('  %s\t%s\t%s\n' % (s['url'], (s['name'] or '')[:40], s['why']))
    rv = collections.Counter(r for e in out for r in (e.get('_review') or []))
    rep.write('\n--- ⚠️載せるが判断が要りそうな型（_review）---\n')
    for k, v in rv.most_common():
        rep.write('  %d\t%s\n' % (v, k))
    for e in out:
        if e.get('_review'):
            rep.write('  %s\t%s\t%s\n' % (e['links']['livepocket'], '・'.join(e['_review']), e['name'][:40]))
    rep.write('\n--- 枠を作らなかった受付（エントリは載せる）---\n')
    for e in out:
        for raw, w in (e.get('_skipped_slots') or []):
            rep.write('  %s\t%s\t%s\n' % (e['links']['livepocket'], raw[:30], w))
    if unknown:
        rep.write('\n🚨表に無い札・カテゴリ: %s\n' % dict(unknown))
    rep.write('\nジャンル: %s\n' % dict(collections.Counter(e['_genre'] for e in out)))
    rep.close()
    print('build_livepocket: entries=%d live=%d skipped=%d unknown=%d -> %s / %s'
          % (len(out), live, len(skipped), sum(unknown.values()), a.out, a.report))
    return 0


if __name__ == '__main__':
    sys.exit(main())
