# -*- coding: utf-8 -*-
"""統合＝既存エントリに「別ページの公演」の枠を足す。**枠にそのページのURLを焼き込む**。

  python tmp/merge_with_urls_0912.py            … 調べるだけ
  python tmp/merge_with_urls_0912.py --apply

🚨2026-09-10 にここで失敗した＝`refresh_deadlines` にそのまま流したら、
   足した枠が **url を持たないまま** 入り、押すと既存の links.pia（別会場）へ飛ぶ状態になった。
   単独URLのビルドは「links.pia があるから」と ticket.url を付けないので、
   **別エントリへ移す時は移す側でURLを焼き込まないといけない**
   （[[feedback_tour_per_ticket_url]]「エントリを畳む前にurl空の枠へカードリンクを焼き込む」）。

やること:
 ・足す枠には**そのページのURL**を必ず入れる
 ・既存の url 空の枠には**既存の links.pia** を焼き込む（同じ理由で飛び先が壊れるため）
 ・骨格（券種名＋（…公演））が既存にある枠は触らない（締切の更新は refresh の担当）
 ・会場が増えるので dateLabel / venue / prefecture / date を union で作り直す
"""
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
WD = '月火水木金土日'
import datetime as _dt
TODAY = _dt.date.today().isoformat()
PREF47 = set('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 '
             '岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 '
             '福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄'.split())


def pref_of(p):
    """「大阪府」「福岡県」「東京都」→「大阪」「福岡」「東京」。47都道府県でなければ None（「〜」などを県と読まない）。"""
    p = (p or '').strip()
    if p in PREF47:
        return p
    if len(p) > 2 and p[-1] in '都府県' and p[:-1] in PREF47:
        return p[:-1]
    return None


def head(ty):
    m = re.match(r'^(.*?（[^（）]*公演）)', ty or '')
    return m.group(1) if m else (ty or '')


def jp(iso_s):
    import datetime
    y, mo, d = [int(x) for x in iso_s.split('-')]
    return '%d年%d月%d日(%s)' % (y, mo, d, WD[datetime.date(y, mo, d).weekday()])


src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

BUILT = [a for a in sys.argv[1:] if a.endswith('.json')]
built = json.load(io.open(BUILT[0] if BUILT else 'tmp/built_merge_0912.json', encoding='utf-8'))
cands = {c['newid']: c for c in json.load(io.open(BUILT[1] if len(BUILT) > 1 else 'tmp/cand_merge_0912.json', encoding='utf-8'))}

added = burned = 0
touched = []
for b in built:
    e = by.get(cands[b['id']].get('target', b['id']))
    if not e:
        continue
    srcurl = cands[b['id']]['urls'][0]
    myurl = (e.get('links') or {}).get('pia') or ''

    # ① 既存の url 空の枠に、既存の links.pia を焼き込む（会場が増える前に）
    for t in e.get('tickets') or []:
        if not t.get('url') and myurl:
            t['url'] = myurl
            burned += 1

    # ② 既存に無い骨格の枠だけ足す。**そのページのURLを焼き込む**
    have = {head(t.get('type')) for t in (e.get('tickets') or [])}
    news = []
    for bt in b.get('tickets') or []:
        if head(bt.get('type')) in have:
            continue
        t = dict(bt)
        t['url'] = bt.get('url') or srcurl
        news.append(t)
    if not news:
        continue
    e.setdefault('tickets', []).extend(news)
    added += len(news)

    # ③ 🚨会場（venue）は**作り直さない**。
    #    ここで union すると、駐車場チケットのように「公演会場ではないページ」の会場名を
    #    ツアーの会場一覧に混ぜてしまう（2026-09-10 id4998 にし阿波の花火で発生）。
    #    直すのは「嘘になるところ」だけ＝**千秋楽(date) と 県 と dateLabel の日付**。
    #    date を伸ばさないと、足した先の公演が来る前にカードが画面から消える
    #    （[[feedback_longrun_event]]＝date は千秋楽）。
    # 🚨9/12 修正＝47都道府県の名前だけを県として認める（「（〜 10/11公演）」の「〜」を県と読んでいた＝id554）
    # 🚨土台は既存の県＝古い形の券種名（「一般発売（〜10/10 23:59）」）は県を持たないので、
    #   券種名だけから集め直すと既存の会場の県が消える（id554 の愛知が落ちて京都だけになった）
    prefs = [p for p in (pref_of(x) for x in re.split(r'[・/／]', e.get('prefecture') or '')) if p]
    for t in e.get('tickets') or []:
        bm = re.search(r'（([^（）]*?)\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}', t.get('type') or '')
        if not bm:
            continue
        for p in re.split(r'[・/／]', bm.group(1)):
            p = pref_of(p)
            if p and p not in prefs:
                prefs.append(p)
    # 🚨初日は**今の dateLabel に書いてある初日**から取る。
    #   e['date'] は千秋楽なので、それを初日として使うと会期が縮んで嘘になる
    #   （[[feedback_show_true_dates_not_sellable_range]]）。
    #   🚨千秋楽も同じ＝**今の dateLabel に書いてある最後の日**を下回らせない。
    #     既存の date が初日で止まっているエントリがある（id942 キーウ＝date が10/31なのに
    #     ラベルは〜12/25）ので、max を date だけで取ると会期が縮んで嘘になる。
    #     🚨ラベルの後ろ側は「〜12月25日」と**年を書かない**ことがある（id942 キーウ）。
    #       年なしは直前に出た年を引き継ぐ。年だけ見る正規表現だと丸ごと読み落とす。
    ds, _y = [], None
    for a, b2, c in re.findall(r'(?:(\d{4})年)?\s*(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or ''):
        if a:
            _y = int(a)
        if _y:
            ds.append('%04d-%02d-%02d' % (_y, int(b2), int(c)))
    # 🚨9/12 ユーザー決定＝もう終わった公演の日は会期に入れない → 今日より前の日は会期の頭に使わない
    # 🚨日付の欄は「最初〜最後」しか持たないので、頭が過去日だと間の「これからの公演」を見落として会期を縮める
    #   （これからの公演は入れる決まり）→ 登録している全部の枠の「（… M/D公演）」の公演日も材料に入れる
    def show_dates(ty):
        m2 = re.search(r'（([^（）]*)公演）', ty or '')
        out, y = [], 2026
        if not m2:
            return out
        for r9, mo, dd in re.findall(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', m2.group(1)):
            if r9:
                y = 2027
            out.append('%04d-%02d-%02d' % (y, int(mo), int(dd)))
        return out
    tix_d = [x for t in (e.get('tickets') or []) for x in show_dates(t.get('type'))]
    alld = [x for x in (ds + tix_d + [e.get('date'), b.get('date')]) if x]
    fut = [x for x in alld if x >= TODAY]
    d0 = min(fut) if fut else min(alld)
    d1 = max(alld)
    if prefs:
        # 〜4県は列挙・5県以上は「全国」（build_pia_entries.PREF_ENUM_MAX と同じ規則）
        e['prefecture'] = '・'.join(prefs) if len(prefs) <= 4 else '全国'
    e['date'] = d1
    e['dateLabel'] = ('%s〜%s %s' % (jp(d0), jp(d1), e.get('prefecture') or '')).strip() if d0 != d1 \
        else ('%s %s' % (jp(d1), e.get('prefecture') or '')).strip()
    touched.append((e['id'], e.get('name', '')[:34], len(news), e['dateLabel'][:52]))

print('足した枠 %d / 既存のurl空に焼き込んだ %d / 触ったエントリ %d件'
      % (added, burned, len(touched)))
for i, n, k, v in touched:
    print('  id=%-5s %-34s ＋%d枠  %s' % (i, n, k, v))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
io.open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('書き込み完了')
