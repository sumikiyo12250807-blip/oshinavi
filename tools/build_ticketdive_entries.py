# -*- coding: utf-8 -*-
"""TicketDive のハーベスト結果から OSHINAVI のエントリを組む（TIGET 版と同じ T-SQUARE形・1公演1カード）。

  python tools/build_ticketdive_entries.py tmp/ticketdive_MMDD.json --out tmp/built_ticketdive_MMDD.json
  python tools/build_ticketdive_entries.py --selftest

## 枠（tickets）の作り方＝**受付（ticketInfoList）× 公演（stage）ごとに1枠**
- type＝「受付名（県 M/D公演）M/D HH:MM発売」（発売前）／「受付名（県 M/D公演）〜M/D HH:MM」（受付中・売り切れ）
  2027年の公演日は「（県 R9年 1/5公演）」（ぴあと同じ＝R9年は公演の日付にだけ付ける）。
- date＝締切（endApply・JST）／startDate＝発売日（発売前だけ）／url＝公演ページ。
- 🚨発売前も締切を持つ（date＝発売日だと発売日の翌0時に消える＝9/24 FANY・TIGET・ZAIKO と同じ穴）。
- 締切が公演日より後なら公演日で締める（配信・視聴・アーカイブの受付は例外）。
- 同じ日に公演が2つ以上＝バッジに**開演**時刻（stages[].startStage）を入れる（昼夜を潰さない）。
- 受付が画面に出る前（ticketInfoList[].release が未来）の受付は載せない＝まだ公開されていない情報。
- 締切が過ぎた受付は載せない。

## 売り状態（ticketTypes[].remainingRate / status）
| 状態 | 判定 | OSHINAVI |
|---|---|---|
| 発売前 | いま < startApply | startDate 付き |
| 売り切れ | その公演の券種が**全部** remainingRate==0 | soldout:true（予定枚数終了） |
| 受付中 | startApply ≦ いま、残り>0 の券種があり、status が closed でない | 受付中 |
| 分からない | 受付期間の内なのに残り>0 で status が closed・残りが読めない 等 | **載せない**（発売中にしない）・報告 |

## 県（TicketDive には県の項目が無い）
推測しない。決められる順＝①会場の住所（stages[].venue.address）②会場名に県名（「(大阪府)」など）
③公演ページの紹介文で**会場名か「会場」「住所」「〒」と同じ行**に書かれた住所の県名（1つに決まる時だけ）
④調べて確かめた会場の表（VENUE_PREF・住所の出所をコメントに残す）。
決まらなければ県は空（バッジから県を落とす）＝報告に数を出す。
`--index-venue` を付けた時だけ、index.html で他の売り場（ぴあ・e+ 等の県欄）が**同じ会場名**に付けた県（1つに揃っている時だけ）も使う。
`--place-table` を付けた時だけ、TIGET でユーザーが決めた地名→県の表（tiget_harvest.pref_from_place）も使う（既定は使わない）。

## ジャンル（TicketDive にはカテゴリが無い）
**売り場の文字（公演名・紹介文）に出ている語だけ**で GENRE_LABEL の札を当てる。当たらなければ `_genre` 空＋`_review`（人が振り分ける）。
"""
import argparse
import datetime
import importlib.util
import io
import json
import os
import re
import sys
import unicodedata

_KEEP = []
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    # 🚨読み込む道具は中で sys.stdout を差し替える＝前後のラッパーを握っておく（gate_tiget_slots と同じ手）
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


BT = _load('build_tiget_entries')     # ticket_name / is_seller_side / STREAM_RE / jp / md（同じ物差し）
TH = _load('tiget_harvest')           # PREF47 / pref_from_place（--place-table の時だけ）
TD = _load('ticketdive_harvest')      # to_jst
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JST = datetime.timezone(datetime.timedelta(hours=9))

# 調べて確かめた会場の表（会場の公式サイトの住所で確かめたものだけ足す。出所をコメントに残す）
VENUE_PREF = {
}

# ジャンル＝売り場の文字に出ている語 → GENRE_LABEL の札（先に当たったものが主）
GENRE_WORDS = (
    ('idol', r'アイドル|特典会|チェキ会|チェキ撮影|生誕祭|定期公演'),
    ('owarai', r'漫才|お笑い|コント|芸人'),
    ('engeki', r'朗読劇|舞台|演劇|劇団|公演台本'),
)
# ⚠️「定期公演」「生誕祭」は劇団・芸人でも使う＝アイドルの札は「アイドル|特典会|チェキ」が1つも無く
#    お笑い・演劇の語がある時は付けない（下の genre_of で見る）


def full_pref(text):
    """文字の中の都道府県名（「東京都」「大阪府」「北海道」「〜県」）を集合で返す（短い形は見ない＝誤爆防止）。"""
    t = text or ''
    out = []
    for p in TH.PREF47:
        if p in t:
            out.append(p if p == '北海道' else p[:-1])
    # 「京都府」は「東京都」にも「京都」が含まれる形では出ない（「京都府」だけ見る）ので PREF47 のままでよい
    return set(out)


# --index-venue の時だけ埋まる：index.html で**他の売り場（ぴあ・e+ 等）が同じ会場名に付けた県**（全部が同じ県の時だけ）
INDEX_VENUE = {}


def vkey(s):
    return re.sub(r'[\s　・･\-—–_/／()（）\[\]【】「」『』"\'’]', '', unicodedata.normalize('NFKC', s or '')).lower()


def load_index_venues(path='index.html'):
    """index.html の EVENTS から 会場名 → 県 の表を作る。条件＝会場名が5字以上・県が1つだけ（「東京・大阪」は使わない）・
    同じ会場名に2つ以上の県が付いていたら使わない・TicketDive 由来のカードは数えない（自分の推測を自分で使わない）。"""
    h = io.open(path, encoding='utf-8', newline='').read()
    ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
    seen = {}
    for e in ev:
        if 'ticketdive' in (e.get('links') or {}):
            continue
        p = (e.get('prefecture') or '').strip()
        k = vkey(e.get('venue'))
        if not p or len(k) < 5 or not re.fullmatch(r'[一-龥]{2,3}', p) or p not in TH.BARE_PREF:
            continue
        seen.setdefault(k, set()).add(p)
    INDEX_VENUE.clear()
    INDEX_VENUE.update({k: list(v)[0] for k, v in seen.items() if len(v) == 1})
    return len(INDEX_VENUE)


def pref_of_stage(stage, detail, place_table=False):
    """1つの公演の県と、決めた出所を返す → (県 or '', 出所)。"""
    ad = full_pref(stage.get('address'))
    if len(ad) == 1:
        return ad.pop(), 'address'
    vn = stage.get('venue') or ''
    vp = full_pref(vn)
    if len(vp) == 1:
        return vp.pop(), 'venue_name'
    # 紹介文：会場名の入った行・「会場/住所/〒/場所」の行の県名（1つに決まる時だけ）
    lines = []
    key = re.sub(r'\s+', '', vn)
    for ln in (detail or '').splitlines():
        l2 = re.sub(r'\s+', '', ln)
        if (key and len(key) >= 3 and key in l2) or re.search(r'会場|住所|〒|場所|所在地', ln):
            lines.append(ln)
    dp = set()
    for ln in lines:
        # 住所の形（県名のすぐ後ろに市区町村）のものだけ
        for m in re.finditer(r'(東京都|北海道|大阪府|京都府|[一-龥]{2,3}県)\s*[一-龥ぁ-んァ-ヶ]{1,6}[市区町村郡]', ln):
            p = m.group(1)
            if p in TH.PREF47:
                dp.add(p if p == '北海道' else p[:-1])
    if len(dp) == 1:
        return dp.pop(), 'detail_address'
    for k, v in VENUE_PREF.items():
        if k in vn:
            return v, 'venue_table'
    p = INDEX_VENUE.get(vkey(vn))
    if p:
        return p, 'index_venue'
    if place_table and not re.search(r'配信|オンライン', vn):
        p = TH.pref_from_place(vn)
        if p:
            return p, 'place_table'
    return '', 'unknown'


def genre_of(name, detail):
    txt = (name or '') + '\n' + (detail or '')
    hits = []
    for g, rx in GENRE_WORDS:
        m = re.search(rx, txt)
        if m:
            hits.append((g, m.group(0)))
    # 公演名に「フェス」＝fes（[[feedback_fes_definition]] 2026-10-13 すちこ決定）・公演名に「ミュージカル」＝musical
    for g, rx in (('fes', r'フェス'), ('musical', r'ミュージカル')):
        m = re.search(rx, name or '')
        if m and g not in [h[0] for h in hits]:
            hits.append((g, m.group(0)))
    gs = [g for g, _ in hits]
    if 'idol' in gs and not re.search(r'アイドル|特典会|チェキ', txt) and ({'owarai', 'engeki'} & set(gs)):
        hits = [h for h in hits if h[0] != 'idol']
    return [g for g, _ in hits], [w for _, w in hits]


def jst_dt(iso):
    """UTC の ISO → JST の datetime（読めなければ None）。"""
    if not iso:
        return None
    try:
        return datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(JST)
    except Exception:
        return None


def ymd(d):
    return d.strftime('%Y-%m-%d')


def hm(d):
    return '%d:%02d' % (d.hour, d.minute)


def mdr(iso):
    """'2027-01-05' → 'R9年 1/5'（2027年は R9年 を前に付ける）／2026年は '1/5'。"""
    y = int(iso[:4])
    s = BT.md(iso)
    return ('R%d年 %s' % (y - 2018, s)) if y >= 2027 else s


def ev_detail(ev):
    """紹介文の代わり＝ハーベストが残した住所の行と札の語（紹介文そのものは写さない）。古い形（detail）も読む。"""
    if ev.get("detail"):
        return ev["detail"]
    return '\n'.join(ev.get('detail_lines') or []) + '\n' + ' '.join(ev.get('detail_words') or [])


def build(ev, today, now=None, place_table=False):
    """1公演 → (エントリ, None) か (None, 理由)。now は JST の datetime（既定＝いま）。"""
    now = now or datetime.datetime.now(JST)
    name = ev.get('name') or ''
    if ev.get('status') and ev.get('status') != 'release':
        return None, '公開されていない（status=%s）' % ev.get('status')
    if BT.is_seller_side(name):
        return None, '出す側の申込（出店・参加エントリー・案内登録）'
    stages = []
    for s in ev.get('stages') or []:
        st = jst_dt(s.get('start')) or jst_dt(s.get('open'))
        if not st:
            continue
        pref, how = pref_of_stage(s, ev_detail(ev), place_table)
        stages.append(dict(s, _dt=st, _date=ymd(st), _pref=pref, _prefFrom=how))
    if not stages:
        return None, '公演日が読めない'
    future = sorted({s['_date'] for s in stages if s['_date'] >= today})
    if not future:
        return None, '公演が終わっている'
    limit = (datetime.date.fromisoformat(today) + datetime.timedelta(days=730)).isoformat()
    if future[0] > limit:
        return None, '公演日が2年より先＝主催者の試し書き・雛形の疑い'
    perday = {}
    for s in stages:
        perday[s['_date']] = perday.get(s['_date'], 0) + 1

    tickets, unknown, hidden, expired = [], [], 0, 0
    for info in ev.get('infos') or []:
        rel = jst_dt(info.get('release'))
        if rel and rel > now:
            hidden += 1
            continue
        raw = info.get('name') or ''
        if BT.is_seller_side(raw):
            continue
        nm = BT.ticket_name(raw)
        sa, ea = jst_dt(info.get('startApply')), jst_dt(info.get('endApply'))
        types = [t for t in info.get('types') or []
                 if not (BT.is_seller_side(t.get('name')) and not re.search(r'取り置き|取置|チェキ', t.get('name') or ''))]
        if not types:
            continue
        any_sid = any(t.get('stageIds') for t in types)
        for s in stages:
            d = s['_date']
            stream = bool(re.search(BT.STREAM_RE, raw))
            if d < today and not stream:
                continue
            ts = [t for t in types if (s.get('id') in (t.get('stageIds') or []))] if any_sid else types
            if not ts:
                continue
            # 締切（JST）。公演日より後なら公演日で締める（配信は例外）
            if ea:
                end_d, end_t = ymd(ea), hm(ea)
                if end_d > d and not stream:
                    end_d, end_t = d, ''
            else:
                end_d, end_t = d, ''          # 締切が無い＝「〜公演日」（TIGET の当日支払いと同じ決まり）
            if end_d < today:
                expired += 1
                continue
            when = (f'{BT.md(d)} {hm(s["_dt"])}公演' if perday.get(d, 0) > 1 else f'{BT.md(d)}公演')
            if d >= '2027-01-01':
                when = 'R%d年 %s' % (int(d[:4]) - 2018, when)
            head = f'{nm}（{s["_pref"]} {when}）' if s['_pref'] else f'{nm}（{when}）'
            end_s = f'{BT.md(end_d)} {end_t}'.rstrip()
            rates = [t.get('remainingRate') for t in ts]
            stats = {t.get('status') for t in ts} | {info.get('status')}
            if sa and now < sa:
                tickets.append({'type': f'{head}{BT.md(ymd(sa))} {hm(sa)}発売',
                                'date': end_d, 'startDate': ymd(sa), 'url': ev['page']})
            elif rates and all(r == 0 for r in rates):
                tickets.append({'type': f'{head}〜{end_s}', 'date': end_d, 'url': ev['page'],
                                'soldout': True, 'soldoutSince': today})
            elif any(isinstance(r, (int, float)) and r > 0 and t.get('status') != 'closed' for r, t in zip(rates, ts)) \
                    and info.get('status') != 'closed':
                tickets.append({'type': f'{head}〜{end_s}', 'date': end_d, 'url': ev['page']})
            else:
                unknown.append('%s（%s）status=%s 残り=%s' % (raw[:20], d, sorted(x for x in stats if x), rates))
    seen, uniq = set(), []
    for t in tickets:
        k = (t['type'], t['date'], t.get('startDate'), bool(t.get('soldout')))
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    tickets = uniq
    if not tickets:
        why = '載せる枠が無い（締切が過ぎた %d・未公開 %d・状態が分からない %d）' % (expired, hidden, len(unknown))
        return None, why
    fut_st = [s for s in stages if s['_date'] >= today]
    prefs = []
    for s in fut_st:
        if s['_pref'] and s['_pref'] not in prefs:
            prefs.append(s['_pref'])
    venues = []
    for s in fut_st:
        if s.get('venue') and s['venue'] not in venues:
            venues.append(s['venue'])
    arts = []
    for s in stages:
        for a in s.get('artists') or []:
            n = (a.get('name') or '').strip()
            if n and n not in arts:
                arts.append(n)
    pref = '・'.join(prefs)
    label = (f'{BT.jp(future[0])} {pref}' if len(future) == 1
             else f'{BT.jp(future[0])}〜{BT.jp(future[-1])} {pref}').strip()
    gs, words = genre_of(name, ev_detail(ev))
    e = {
        'artist': '／'.join(arts) if arts else name,
        'name': name,
        'date': future[-1],
        'dateLabel': label,
        'venue': '／'.join(venues) or '（会場未定）',
        'prefecture': pref,
        'genre': 'new',
        '_genre': gs[0] if gs else '',
        '_extraGenres': gs[1:],
        '_srcgenre': 'ticketdive:' + ','.join(words),
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'ticketdive': ev['page']},
        'tickets': tickets,
        'verified': True,
        'verifiedAt': today,
    }
    rv = []
    if not gs:
        rv.append('ジャンル：売り場にカテゴリが無く、公演名・紹介文に札を決める語が無い')
    if any(not s['_pref'] for s in fut_st):
        rv.append('県：住所・会場名・紹介文の住所から決まらない（推測しない）')
    if rv:
        e['_review'] = ' / '.join(rv)
    e['_prefFrom'] = sorted({s['_prefFrom'] for s in fut_st})
    if unknown:
        e['_unknownState'] = unknown
    return e, None


def _selftest():
    now = datetime.datetime(2026, 11, 12, 9, 0, tzinfo=JST)
    today = '2026-11-12'
    base = {'url': 'x', 'page': 'https://ticketdive.com/event/x', 'name': 'テスト定期公演 vol.1', 'status': 'release',
            'detail': '【会場】下北沢SHELTER\n住所：東京都世田谷区北沢2-6-10\n問い合わせ：',
            'stages': [{'id': 'S1', 'start': '2026-12-03T10:00:00.000Z', 'open': '2026-12-03T09:30:00.000Z',
                        'venue': '下北沢SHELTER', 'address': '', 'artists': [{'id': 'A', 'name': 'あいどる'}]}],
            'infos': [{'id': 'I1', 'name': '一般販売', 'release': '2026-11-01T00:00:00.000Z',
                       'startApply': '2026-11-10T11:00:00.000Z', 'endApply': '2026-12-02T14:59:59.999Z',
                       'status': 'applied', 'types': [
                           {'name': 'A', 'price': 3000, 'stageIds': ['S1'], 'remainingRate': 1, 'status': 'applied'},
                           {'name': 'B', 'price': 4000, 'stageIds': ['S1'], 'remainingRate': 0, 'status': 'closed'}]}]}
    e, why = build(json.loads(json.dumps(base)), today, now)
    assert e, why
    assert e['tickets'] == [{'type': '一般販売（東京 12/3公演）〜12/2 23:59', 'date': '2026-12-02',
                             'url': 'https://ticketdive.com/event/x'}], e['tickets']
    assert e['prefecture'] == '東京' and e['_prefFrom'] == ['detail_address'] and e['_genre'] == 'idol', e
    assert e['date'] == '2026-12-03' and e['dateLabel'] == '2026年12月3日(木) 東京' and e['artist'] == 'あいどる'
    assert e['links']['ticketdive'] == 'https://ticketdive.com/event/x' and e['genre'] == 'new'
    # 発売前＝発売〜締切で持つ・2027年は R9年
    b = json.loads(json.dumps(base))
    b['stages'][0]['start'] = '2027-01-05T10:00:00.000Z'
    b['infos'][0].update(startApply='2026-11-20T11:00:00.000Z', endApply='2027-01-04T14:59:00.000Z')
    t = build(b, today, now)[0]['tickets'][0]
    assert t == {'type': '一般販売（東京 R9年 1/5公演）11/20 20:00発売', 'date': '2027-01-04',
                 'startDate': '2026-11-20', 'url': 'https://ticketdive.com/event/x'}, t
    # 売り切れ＝全部 0
    b = json.loads(json.dumps(base))
    for x in b['infos'][0]['types']:
        x['remainingRate'] = 0
    t = build(b, today, now)[0]['tickets'][0]
    assert t.get('soldout') is True and t['type'] == '一般販売（東京 12/3公演）〜12/2 23:59', t
    # 状態が分からない（受付期間の内・残りあり・status closed）＝載せない
    b = json.loads(json.dumps(base))
    b['infos'][0]['status'] = 'closed'
    for x in b['infos'][0]['types']:
        x['status'] = 'closed'
    e2, why2 = build(b, today, now)
    assert e2 is None and '状態が分からない 1' in why2, why2
    # 締切が公演日より後＝公演日で締める
    b = json.loads(json.dumps(base))
    b['infos'][0]['endApply'] = '2026-12-10T14:59:00.000Z'
    assert build(b, today, now)[0]['tickets'][0]['type'] == '一般販売（東京 12/3公演）〜12/3', build(b, today, now)[0]['tickets']
    # 締切が過ぎた受付・未公開の受付は載せない
    b = json.loads(json.dumps(base))
    b['infos'][0]['endApply'] = '2026-11-11T14:59:00.000Z'
    assert build(b, today, now)[0] is None
    b = json.loads(json.dumps(base))
    b['infos'][0]['release'] = '2026-11-20T00:00:00.000Z'
    assert '未公開 1' in build(b, today, now)[1]
    # 同じ日に2公演＝開演時刻を入れる
    b = json.loads(json.dumps(base))
    b['stages'].append(dict(b['stages'][0], id='S2', start='2026-12-03T05:00:00.000Z'))
    for x in b['infos'][0]['types']:
        x['stageIds'] = ['S1', 'S2']
    ty = sorted(t['type'] for t in build(b, today, now)[0]['tickets'])
    assert ty == ['一般販売（東京 12/3 14:00公演）〜12/2 23:59', '一般販売（東京 12/3 19:00公演）〜12/2 23:59'], ty
    # 県が決まらない＝バッジから県を落とす（推測しない）
    b = json.loads(json.dumps(base))
    b['detail'] = ''
    b['stages'][0]['venue'] = 'Nakano space Q'
    e3 = build(b, today, now)[0]
    assert e3['prefecture'] == '' and e3['tickets'][0]['type'].startswith('一般販売（12/3公演）'), e3['tickets']
    assert e3['_prefFrom'] == ['unknown'] and e3['_review'], e3
    # 県：住所 > 会場名 > 紹介文の住所の行（2つ以上の県が出たら決めない）
    assert pref_of_stage({'address': '大阪府大阪市北区', 'venue': 'x'}, '') == ('大阪', 'address')
    assert pref_of_stage({'address': '', 'venue': 'J.Bridge(大阪府)'}, '') == ('大阪', 'venue_name')
    assert pref_of_stage({'address': '', 'venue': 'X'}, '会場：東京都渋谷区 / 大阪府大阪市')[0] == ''
    assert pref_of_stage({'address': '', 'venue': 'X'}, '大阪府大阪市のファンのみなさん')[0] == ''   # 会場の行でない
    assert pref_of_stage({'address': '', 'venue': 'GOTANDA G6'}, '', place_table=True) == ('東京', 'place_table')
    assert pref_of_stage({'address': '', 'venue': 'GOTANDA G6'}, '')[0] == ''
    # ジャンル：お笑いの語だけ＝お笑い（定期公演でもアイドルにしない）／語が無い＝空
    assert genre_of('ワラヤキ定期公演', '漫才師が出演')[0] == ['owarai']
    assert genre_of('ガオマンザイ', '最強漫才師限定ライブ')[0] == ['owarai']
    assert genre_of('〇〇 2nd LIVE', '')[0] == []
    # 出す側は載せない
    b = json.loads(json.dumps(base))
    b['name'] = '物販ブース出店申込'
    assert build(b, today, now)[0] is None
    print('selftest OK: 受付×公演の枠/発売前/R9年/売り切れ/分からない状態は載せない/公演日で締める/期限切れ・未公開/'
          '同日2公演/県の出所/ジャンルの語')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_ticketdive.json')
    ap.add_argument('--today', default=datetime.datetime.now(JST).date().isoformat())
    ap.add_argument('--place-table', action='store_true', help='TIGET の地名→県の表も使う（既定は使わない）')
    ap.add_argument('--index-venue', action='store_true',
                    help='他の売り場が index.html で同じ会場名に付けた県も使う（既定は使わない）')
    a = ap.parse_args()
    if a.index_venue:
        print('  index.html の会場→県の表 %d 会場' % load_index_venues())
    d = json.load(io.open(a.src, encoding='utf-8'))
    out, skipped = [], []
    for ev in d['events']:
        e, why = build(ev, a.today, place_table=a.place_table)
        if e:
            out.append(e)
        else:
            skipped.append({'url': ev.get('page'), 'name': ev.get('name'), 'why': why})
    out.sort(key=lambda e: (e['date'], e['name']))
    json.dump({'entries': out, 'skipped': skipped}, io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'=== 組み上がり {len(out)}件 / 載せない {len(skipped)}件 → {a.out} ===')
    why = {}
    for s in skipped:
        k = re.sub(r'（.*', '', s['why'])
        why[k] = why.get(k, 0) + 1
    for k, v in sorted(why.items(), key=lambda x: -x[1]):
        print(f'  載せない: {k}: {v}件')
    pf = {}
    for e in out:
        for k in e['_prefFrom']:
            pf[k] = pf.get(k, 0) + 1
    print('  県の出所:', pf, '/ 県が空のカード', sum(1 for e in out if not e['prefecture']))
    g = {}
    for e in out:
        g[e['_genre'] or '(空)'] = g.get(e['_genre'] or '(空)', 0) + 1
    print('  ジャンル:', g)
    nt = sum(len(e['tickets']) for e in out)
    print('  枠 %d（発売前 %d・売り切れ %d）/ 状態が分からず落とした枠があるカード %d'
          % (nt, sum(1 for e in out for t in e['tickets'] if t.get('startDate')),
             sum(1 for e in out for t in e['tickets'] if t.get('soldout')),
             sum(1 for e in out if e.get('_unknownState'))))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
