# -*- coding: utf-8 -*-
"""e+ (イープラス) 発売前ハーベスター（段階1: 一覧カード収集＋DB突合）
使い方:
  python tools/eplus_harvest.py cards j-pop 1 3     # j-popジャンルのp1〜p3のカードを収集→tmp/eplus_cards.json
既存DBのartist名と突合し in_db フラグを付ける。
"""
import urllib.request, re, json, sys, time, datetime, unicodedata
import html as H

UA = {'User-Agent': 'Mozilla/5.0'}

_HALF_KANA_RE = re.compile(r'[｡-ﾟ]+')


def fix_half_kana(s):
    """e+は名前や会場に半角カナを返すことがある（アンジェラ･アキ／ナオト･インティライミ の半角中黒、
    ｽﾞ等）。OSHINAVI既存は全角なので**半角カナの連続だけ** NFKC で全角化する。
    全角ラテンや（）／〜には触らない＝最小限（ぴあ側 norm_fw との違い）。
    2026-07-30 の目視で発覚（既存 id77/3016/3019/3031/3053/3082/3100/3103 が半角中黒）。
    """
    if not isinstance(s, str) or not s:
        return s
    return _HALF_KANA_RE.sub(lambda m: unicodedata.normalize('NFKC', m.group(0)), s)


def fetch(url, tries=4):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def parse_kouen(html):
    """一覧HTMLから公演カード(base_eid, perf_url, date, title, status)を出現順に抽出"""
    out = []
    for url, seg in re.findall(r'ticket-item--kouen"\s+href="([^"]+)">(.*?)</a>', html, re.S):
        base = re.search(r'/sf/detail/(\d+)', url)
        st = re.search(r'ticket-status__item[^>]*>([^<]+)<', seg)
        t = re.search(r'ticket-item__title">(.*?)</h3>', seg, re.S)
        title = re.sub(r'<[^>]+>', ' ', t.group(1)) if t else ''
        title = re.sub(r'\s+', ' ', H.unescape(title)).strip()
        yy = re.search(r'__yyyy">([^<]+)</span><span[^>]*__mmdd">([^<]+)<', seg)
        date = (yy.group(1) + yy.group(2)) if yy else ''
        out.append({'eid': base.group(1) if base else '',
                    'url': ('https://eplus.jp' + url) if url.startswith('/') else url,
                    'date': date,
                    'title': title,
                    'status': (st.group(1).strip() if st else '')})
    return out


def load_db_artists():
    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S)
    arr = json.loads(m.group(1))

    def norm(s):
        return re.sub(r'\s+', '', (s or '')).lower()
    names = set()
    eplus_ids = set()
    for e in arr:
        names.add(norm(e.get('artist')))
        names.add(norm(e.get('name')))
        ep = (e.get('links') or {}).get('eplus') or ''
        for mid in re.findall(r'/sf/detail/(\d+)', ep):
            eplus_ids.add(mid)
    return names, eplus_ids, norm


def parse_cards(html):
    """一覧HTMLからカード(id, artist, desc)を出現順に抽出"""
    out = []
    for m in re.finditer(r'block-card-ticket__trigger"\s+href="[^"]*?/sf/detail/(\d+)"(.*?)card-inner__license', html, re.S):
        eid = m.group(1)
        seg = m.group(2)
        t = re.search(r'card-inner__title[^>]*>([^<]+)<', seg)
        d = re.search(r'card-inner__text[^>]*>([^<]*)<', seg)
        out.append({'eid': eid,
                    'artist': (t.group(1).strip() if t else ''),
                    'desc': (d.group(1).strip() if d else '')})
    return out


# 🚨 2026-07-21 に書いた日付がハードコードされたまま1週間動いていなかった。
# その間「締切済み(ed < TODAY)」の判定が7/21基準のままで、7/22〜の締切枠を
# 「まだ買える」と誤判定して取り込んでいた（2026-07-28 LINDBERGで発覚＝
# 〜7/24締切の抽選プレオーダー4枠が生き枠として出てきた）。実日付を使う。
TODAY = datetime.date.today()

_WD = ('月', '火', '水', '木', '金', '土', '日')


def jp_date(iso):
    """2026-10-23 → 2026年10月23日(金)。dateLabel はテンプレ準拠の日本語形で出す
    （memory: feedback_entry_template_standard）。ISO のまま出すと画面が英数字になる
    ＝2026-07-28 LINDBERG の refresh で発覚。"""
    d = datetime.date.fromisoformat(iso)
    return f'{d.year}年{d.month}月{d.day}日({_WD[d.weekday()]})'


def md(iso):
    """公演日バッジのM/D。**翌年以降の公演には令和略記「R{N}年 」を付ける**。

    ぴあ側 build_pia_entries.era()/mdbadge() と同じ規則。e+側の md() は年を捨てており、
    2027公演のバッジが「1/23公演」になって来年公演が今年に見えていた
    （2026-07-29 茉ひる id3102＝実際は2027-01-23）。[[feedback_r9_year_notation]]"""
    y = int(iso[:4])
    e = f'R{y - 2018}年 ' if y > datetime.date.today().year else ''
    return f'{e}{int(iso[5:7])}/{int(iso[8:10])}'


def multi_time_dates(shows):
    """同じ公演日に開演時刻が2つ以上ある日付の集合。

    従来は「全公演数 > 日付の種類数」というツアー全体の判定だったので、1日だけ昼夜がある
    ツアーでも全枠に昼/夜が付いた。時刻を入れるのは**その日だけ**でよい
    （[[feedback_same_day_show_time_badge]]「こういったものだけ」）。"""
    by_date = {}
    for s in shows:
        by_date.setdefault(s['iso'], set()).add(s.get('time') or '')
    return {d for d, ts in by_date.items() if len([t for t in ts if t]) >= 2}


def sesslab(r, multi_dates):
    """公演descriptorの末尾。同日・時間違いの複数公演がある日だけ開演時刻を入れる。

    「昼公演/夜公演」だけだと画面に同じ表記が2つ並んで見分けられない
    （2026-07-23 BENI id3047 ユーザー指摘）。→「（神奈川県 11/1 15:00公演）」の形にする。
    🚨 renderCardの発売時刻抽出は「最後の閉じ括弧より後ろ」を見る前提なので、
    （…公演）の中に時刻を入れても発売時刻の表示は壊れない（[[feedback_same_day_show_time_badge]]）。"""
    if r['iso'] in multi_dates and r.get('time'):
        return f" {r['time']}公演"
    return '公演'


def parse_ld(html):
    """JSON-LD Event blob群 → [{name,date(YYYY-MM-DD),venue,pref}]（公演日/会場ごと）"""
    evs = []
    for blob in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        try:
            d = json.loads(blob)
        except Exception:
            continue
        items = d if isinstance(d, list) else [d]
        for it in items:
            if not isinstance(it, dict) or it.get('@type') != 'Event':
                continue
            sd = (it.get('startDate') or '')[:10]
            loc = it.get('location') or {}
            venue = loc.get('name') if isinstance(loc, dict) else ''
            pref = ''
            if isinstance(loc, dict):
                pref = ((loc.get('address') or {}).get('addressRegion') or '') if isinstance(loc.get('address'), dict) else ''
            full = (it.get('startDate') or '')
            tm = full[11:16] if 'T' in full else ''
            evs.append({'name': H.unescape(it.get('name') or '').strip(),
                        'date': sd, 'time': tm, 'venue': H.unescape(venue or '').strip(),
                        'pref': pref, 'url': (it.get('url') or '').strip()})
    # 公演日時+会場でユニーク化（昼夜を潰さない）
    uniq = {}
    for e in evs:
        uniq[(e['date'], e['time'], e['venue'])] = e
    return list(uniq.values())


def count_options(html):
    return len(re.findall(r'<option[^>]*>[^<]*20\d\d[^<]*</option>', html))


_DEAD = ('予定枚数終了', '受付終了', '販売終了', '完売', '受付は終了')
_PERIOD = re.compile(r'受付期間:(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})'
                     r'～(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})')


def _window_from(header_text, status):
    """受付期間テキスト → 枠dict。締切が過去 or 売り切れ/終了なら None。"""
    m = _PERIOD.search(header_text)
    if not m:
        return None
    g = m.groups()
    sd = datetime.date(int(g[0]), int(g[1]), int(g[2]))
    ed = datetime.date(int(g[5]), int(g[6]), int(g[7]))
    if ed < TODAY or status == 'ended':
        return None
    s = header_text
    kind = '抽選' if '抽選' in s[:8] else ('先着' if '先着' in s[:8] else '')
    label = re.sub(r'受付期間.*', '', s).strip()
    label = re.sub(r'[★☆◇◆■◎●▲△▼▽※]', '', label)          # 装飾記号除去
    label = re.sub(r'(先着|抽選)\s*(先着|抽選)', r'\1', label)   # 「先着 先着」重複除去
    label = re.sub(r'\s+', '', label).strip() or (kind + '一般発売')
    return {'kind': kind, 'label': label, 'sd': sd, 'status': status,
            'st': f'{int(g[3])}:{g[4]}', 'ed': ed, 'et': f'{int(g[8])}:{g[9]}'}


def _flat(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(x))).strip()


def parse_windows(html):
    """販売枠 [{kind,label,sd,st,ed,et,status}]。**売り切れ/受付終了の枠は返さない**。

    🚨 旧版は `block-ticket__header` の中だけを読んでいた。ところが e+ は販売状態
    （「予定枚数終了」「受付終了」）を **header の外**＝section本体に書く。
    そのため受付期間だけを見て「11/4まで買える」と判断し、**売り切れ枠を生存登録していた**
    （2026-07-29 REBECCA id3052＝実ページは「受付期間:…～2026/11/4(水)18:00 予定枚数終了」。
    reconcile_eplus が死枠と正しく出したのに refresh が生き枠として書き戻し、
    両者が食い違って発覚）。[[project_eplus_harvester_bug_and_qc]]の欠陥Bの本修正。

    判定は `<section class="block-ticket">` 単位で状態spanを読む＝reconcile_eplus.parse_blocks
    と同じ規則にして、ハーベスタと検証ゲートの見解が割れないようにする。"""
    out = []
    secs = [s for s in re.split(r'(?=<section class="block-ticket">)', html)
            if s.startswith('<section class="block-ticket">')]
    if not secs:
        # section形式で取れないページは状態不明。枠を全部捨てると取りこぼすので拾い、
        # status='unknown' を付けて reconcile_eplus 側の照合に委ねる。
        for inner in re.findall(r'block-ticket__header[^>]*>(.*?)</header>', html, re.S):
            w = _window_from(_flat(inner), 'unknown')
            if w:
                out.append(w)
        return out
    for sec in secs:
        body = sec.split('</section>', 1)[0]
        span = re.search(r'<span class="ticket-status__item[^"]*">([^<]+)</span>', body)
        stxt = span.group(1) if span else ''
        if any(w in stxt for w in _DEAD):
            status = 'ended'
        elif '受付中' in stxt:
            status = 'open'
        elif '受付前' in stxt:
            status = 'before'
        else:
            status = 'unknown'
        hm_ = re.search(r'block-ticket__header[^>]*>(.*?)</header>', body, re.S)
        w = _window_from(_flat(hm_.group(1) if hm_ else body), status)
        if w:
            out.append(w)
    return out


def artist_key(title):
    t = re.sub(r'^[\s　]*(先着|抽選)[\s　]+', '', title).strip()
    t = re.split(r'ワンマンツアー|ワンマンライブ|LIVE TOUR|Concert Tour|Billboard Live|THE LIVE|BIRTHDAY|[<「（(【]', t)[0]
    t = re.split(r'[\s　]', t)[0].strip()
    return t or re.sub(r'^[\s　]*(先着|抽選)[\s　]+', '', title).strip()


def main():
    cmd = sys.argv[1]
    if cmd == 'build':
        src = sys.argv[3] if len(sys.argv) > 3 else 'tmp/eplus_live_cand.json'
        cands = json.load(open(src, encoding='utf-8'))
        # DB突合（ローマ字/カナ差も拾うため部分一致blob）
        hh = open('index.html', encoding='utf-8').read()
        mm = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S)
        dbarr = json.loads(mm.group(1))

        def nz(s):
            return re.sub(r'\s+', '', (s or '')).lower()
        dbblob = ' | '.join(nz(e.get('artist')) + ' ' + nz(e.get('name')) for e in dbarr)
        # アーティストでグループ化（同一ツアーの別base-eidを束ねる）
        groups = {}
        for c in cands:
            ak = artist_key(c['title'])
            if nz(ak) and nz(ak) in dbblob:
                continue  # DB重複（ローマ字/カナ含む）
            groups.setdefault(ak, []).append(c)
        print(f'候補 {len(cands)}件 → 新規アーティスト {len(groups)}組')
        # md() はモジュール直下の令和略記つき版を使う（旧ローカル定義は年を捨てていた）

        def card_iso(cd):
            m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', cd or '')
            return f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}' if m else ''

        entries = []
        nid = int(sys.argv[2])  # 開始id
        page_cache = {}
        def to_date(iso):
            y, mo, d = iso.split('-'); return datetime.date(int(y), int(mo), int(d))

        for akey, members in groups.items():
            # JSON-LDの全公演を公演源に（各公演の-P個別URL付き）。base-idごとに1回だけ処理
            rows = []          # {iso,time,venue,pref,url,w,sess,name}
            for eid in dict.fromkeys(c['eid'] for c in members):
                if eid not in page_cache:
                    try:
                        page_cache[eid] = fetch(f"https://eplus.jp/sf/detail/{eid}")
                    except Exception as e:
                        print(f"  !! {eid} fetch失敗 {e}"); page_cache[eid] = ''
                    time.sleep(0.4)
                h = page_cache[eid]
                if not h:
                    continue
                ld = parse_ld(h)
                allw = parse_windows(h)
                if not ld or not allw:
                    continue
                nopt = count_options(h)
                if nopt > len(ld):
                    print(f'  ⚠️ {akey} {eid}: option{nopt} > JSON-LD{len(ld)} 取りこぼしの可能性')
                for ev in ld:
                    if not ev['date']:
                        continue
                    D = to_date(ev['date'])
                    # この公演を売る枠＝締切がD近傍(D-70日〜D+3日)。その最終枠が発売前(sd>今日)の時だけ採用
                    near = [w for w in allw
                            if D - datetime.timedelta(70) <= w['ed'] <= D + datetime.timedelta(3)]
                    if not near:
                        continue
                    w = max(near, key=lambda x: x['ed'])
                    if w['ed'] < TODAY:
                        continue  # 締切済＝もう買えない（発売前も発売中も網羅＝feedback_capture_all_not_select）
                    sess = '昼' if (ev['time'] and ev['time'] < '16:00') else ('夜' if ev['time'] else '')
                    url = ev['url'] or f"https://eplus.jp/sf/detail/{eid}"
                    rows.append({'iso': ev['date'], 'time': ev['time'], 'venue': ev['venue'],
                                 'pref': ev['pref'], 'url': url, 'w': w, 'sess': sess,
                                 'name': ev['name']})
            if not rows:
                print(f'  △ {akey}: 発売前公演なし → スキップ'); continue
            # 不完全JSON-LD(都道府県空)の重複行を除去（同一公演日に情報付き行があれば空行を捨てる）
            has_pref = {r['iso'] for r in rows if r['pref']}
            rows = [r for r in rows if r['pref'] or r['iso'] not in has_pref]
            # 公演(日+セッション)で重複排除。会場/都道府県のある方を優先（同一公演が複数券種ページに出るため）
            byshow = {}
            for r in rows:
                key = (r['iso'], r['sess'])
                cur = byshow.get(key)
                if cur is None or ((r['venue'] and not cur['venue']) or (r['pref'] and not cur['pref'])):
                    byshow[key] = r
            rows = sorted(byshow.values(), key=lambda x: (x['iso'], x['time']))

            def clean_name(n):
                n = re.sub(r'\s*[<（(]\s*(昼|夜)公演\s*[>）)]', '', n)
                return re.sub(r'\s+', ' ', n).strip()
            name = clean_name(min((r['name'] for r in rows if r['name']), key=len, default=akey))
            uniq_venues = list(dict.fromkeys(r['venue'] for r in rows if r['venue']))
            prefs = list(dict.fromkeys(r['pref'] for r in rows if r['pref']))
            dates = [r['iso'] for r in rows]
            d0, d1 = min(dates), max(dates)
            edate = d1
            single_venue = len(uniq_venues) <= 1
            multi_session = multi_time_dates(rows)
            if single_venue:
                pref = prefs[0] if prefs else '全国'
                venue = uniq_venues[0] if uniq_venues else ''
                dlabel = (f"{jp_date(d0)} {pref} {venue}" if d0 == d1
                          else f"{jp_date(d0)}〜{jp_date(d1)} {pref} {venue}")
            else:
                pref = '全国' if len(prefs) > 1 else (prefs[0] if prefs else '全国')
                venue = '全国ツアー（' + '／'.join(uniq_venues) + '）'
                dlabel = f"{jp_date(d0)}〜{jp_date(d1)} 全国ツアー"
            # チケット＝公演ごと（個別URL付与）
            tickets = []
            for r in rows:
                w = r['w']; kind = w['kind'] or '先着'
                scope = f"{r['pref']} {md(r['iso'])}{sesslab(r, multi_session)}"
                if w['sd'] >= TODAY:  # 発売前＋本日発売(今日開始)＝発売日表示・startDate付与／過去開始=受付中(締切表示)
                    typ = f"{kind}一般発売（{scope}）{w['sd'].month}/{w['sd'].day} {w['st']}発売"
                else:                 # 発売中
                    typ = f"{kind}一般発売（{scope}）〜{w['ed'].month}/{w['ed'].day} {w['et']}"
                tk = {'type': typ, 'date': str(w['ed']), 'url': r['url']}
                if w['sd'] >= TODAY:  # 今日開始含む発売前はstartDate付与(本日発売)／過去開始は販売中形(startDate無)
                    tk['startDate'] = str(w['sd'])
                tickets.append(tk)
            for _t in tickets:  # 表示テキストは出口で半角カナを全角化
                _t['type'] = fix_half_kana(_t['type'])
            entries.append({
                'id': nid, 'artist': fix_half_kana(akey), 'name': fix_half_kana(name), 'date': edate,
                'dateLabel': fix_half_kana(dlabel), 'venue': fix_half_kana(venue), 'prefecture': pref,
                'genre': 'new', 'price': None,
                'links': {'rakuten': None, 'lawson': None, 'pia': None,
                          'eplus': rows[0]['url'], 'amazon': None},
                'tickets': tickets, 'verified': True, 'verifiedAt': '2026-07-21'})
            print(f'  ○ id{nid} {akey} | 公演{len(rows)}(会場{len(uniq_venues)}) 枠{len(tickets)} | {d0}〜{d1}')
            nid += 1
        json.dump(entries, open('tmp/eplus_built.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'=== {len(entries)}エントリ生成 → tmp/eplus_built.json ===')
        return
    if cmd == 'refresh':
        # 投入済みのgenre:new e+エントリを、番号(id)据え置きのまま「買える公演を網羅」で現物更新
        def to_date(iso):
            y, mo, d = iso.split('-'); return datetime.date(int(y), int(mo), int(d))

        # md() はモジュール直下の令和略記つき版を使う（旧ローカル定義は年を捨てていた）
        # index.html は CRLF。newline='' 無しで読み書きすると全行 LF 化し、sort_guard が
        # 「並び順ロジックを書き換えた」と誤ブロックする（memory: feedback_index_html_crlf_preserve）
        h = open('index.html', encoding='utf-8', newline='').read()
        m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
        EVENTS = json.loads(m.group(2))
        cache, changed = {}, 0
        # --ids 2194,2195 を付けたエントリは genre に関係なく対象にする
        # （振り分け済みのツアーを e+ 側の実態で育て直す用。2026-07-28 LINDBERG で追加）
        only_ids = set()
        if '--ids' in sys.argv:
            only_ids = {int(x) for x in sys.argv[sys.argv.index('--ids') + 1].split(',') if x.strip()}
        # 対象＝genre:new または id3012-3035（振り分け後のe+純エントリ。玉置3011は混在なので除外）
        for e in EVENTS:
            if only_ids:
                if e.get('id') not in only_ids:
                    continue
            elif e.get('genre') != 'new' and not (3012 <= e.get('id', 0) <= 3035):
                continue
            urls = [(e.get('links') or {}).get('eplus') or ''] + [t.get('url', '') for t in e.get('tickets', [])]
            eids = list(dict.fromkeys(mm.group(1) for u in urls for mm in [re.search(r'/sf/detail/(\d+)', u)] if mm))
            if not eids:
                continue
            # 1) base群のJSON-LDから全公演を集める（各公演の-P URL付き）
            shows = {}
            for eid in eids:
                if eid not in cache:
                    try:
                        cache[eid] = fetch(f"https://eplus.jp/sf/detail/{eid}")
                    except Exception:
                        cache[eid] = ''
                    time.sleep(0.4)
                hh = cache[eid]
                if not hh:
                    continue
                for ev in parse_ld(hh):
                    if not ev['date']:
                        continue
                    sess = '昼' if (ev['time'] and ev['time'] < '16:00') else ('夜' if ev['time'] else '')
                    key = (ev['date'], sess)
                    if key not in shows or (ev['venue'] and not shows[key]['venue']):
                        shows[key] = {'iso': ev['date'], 'time': ev['time'], 'venue': ev['venue'],
                                      'pref': ev['pref'], 'sess': sess,
                                      'url': ev['url'] or f"https://eplus.jp/sf/detail/{eid}"}
            # 2) 各公演の-Pページを直接叩き、その公演の「買える枠」を1つ残らず拾う
            rows = []
            for sh in shows.values():
                pu = sh['url']
                if pu not in cache:
                    try:
                        cache[pu] = fetch(pu)
                    except Exception:
                        cache[pu] = ''
                    time.sleep(0.4)
                ph = cache[pu]
                if not ph:
                    continue
                for w in parse_windows(ph):
                    if w['ed'] < TODAY:
                        continue  # 締切済＝買えない
                    rows.append({**sh, 'w': w})
            if not rows:
                # 買える窓がゼロ＝削除候補。黙って continue すると「変化なし＝健全」に見え、
                # すでに載っている死枠がそのまま残る（2026-07-29 REBECCA/米倉利紀で発覚）。
                print(f"  ⚠️ id{e['id']} {e.get('artist')}: 買える窓ゼロ（全枠 受付終了/予定枚数終了）＝削除候補")
                continue
            uniq_shows = sorted(shows.values(), key=lambda x: (x['iso'], x['time']))
            uniq_venues = list(dict.fromkeys(s['venue'] for s in uniq_shows if s['venue']))
            prefs = list(dict.fromkeys(s['pref'] for s in uniq_shows if s['pref']))
            dates = [s['iso'] for s in uniq_shows]
            d0, d1 = min(dates), max(dates)
            multi_session = multi_time_dates(uniq_shows)
            rows = sorted(rows, key=lambda x: (x['iso'], x['time'], x['w']['sd']))
            if len(uniq_venues) <= 1:
                pref = prefs[0] if prefs else '全国'
                venue = uniq_venues[0] if uniq_venues else e['venue']
                dlabel = (f"{jp_date(d0)} {pref} {venue}" if d0 == d1
                          else f"{jp_date(d0)}〜{jp_date(d1)} {pref} {venue}")
            else:
                pref = '全国' if len(prefs) > 1 else (prefs[0] if prefs else '全国')
                venue = '全国ツアー（' + '／'.join(uniq_venues) + '）'
                dlabel = f"{jp_date(d0)}〜{jp_date(d1)} 全国ツアー"
            tickets = []
            seen_t = set()
            for r in rows:
                w = r['w']
                wlabel = re.sub(r'\s+', '', w['label']) or (w['kind'] or '先着') + '一般発売'
                scope = f"{r['pref']} {md(r['iso'])}{sesslab(r, multi_session)}"
                if w['sd'] >= TODAY:  # 発売前＋本日発売(今日開始)＝発売日表示／過去開始=受付中(締切)
                    typ = f"{wlabel}（{scope}）{w['sd'].month}/{w['sd'].day} {w['st']}発売"
                else:                 # 発売中
                    typ = f"{wlabel}（{scope}）〜{w['ed'].month}/{w['ed'].day} {w['et']}"
                k = (typ, r['url'])
                if k in seen_t:
                    continue
                seen_t.add(k)
                tk = {'type': typ, 'date': str(w['ed']), 'url': r['url']}
                if w['sd'] >= TODAY:  # 今日開始含む発売前はstartDate付与／過去開始は販売中形
                    tk['startDate'] = str(w['sd'])
                tickets.append(tk)
            before = [t['type'] for t in e['tickets']]
            after = [t['type'] for t in tickets]
            if after != before:
                changed += 1
                print(f"  id{e['id']} {e.get('artist')}: 枠{len(before)}→{len(after)}")
                for t in tickets:
                    mark = '  ＋' if t['type'] not in before else '   '
                    print(f"{mark} {t['type']}")
            for _t in tickets:  # 表示テキストは出口で半角カナを全角化（e+は半角中黒を返す）
                _t['type'] = fix_half_kana(_t['type'])
            e['tickets'] = tickets
            e['venue'] = fix_half_kana(venue)
            e['prefecture'] = pref
            e['dateLabel'] = fix_half_kana(dlabel)
            e['date'] = d1
            e['links']['eplus'] = rows[0]['url']
        if 'apply' in sys.argv:
            # index.html は CRLF。json.dumps は \n を吐くので元の改行に戻してから書く。
            # newline='' 無し／replace漏れのどちらでも全行LF化し sort_guard が誤ブロックする
            # （memory: feedback_index_html_crlf_preserve・inject_built.py と同じ書き方に揃えた）
            NL = '\r\n' if '\r\n' in h else '\n'
            bak = f'index.html.bak_{datetime.date.today():%m%d}_eplus_refresh'
            open(bak, 'w', encoding='utf-8', newline='').write(h)
            new = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
            with open('index.html', 'w', encoding='utf-8', newline='') as f:
                f.write(h[:m.start()] + m.group(1) + new + m.group(3) + h[m.end():])
            print(f'  (backup {bak})')
            print(f'=== refresh適用：{changed}エントリ更新（id据え置き）===')
        else:
            print(f'=== [ドライラン] {changed}エントリが変化。書込むなら refresh apply ===')
        return
    if cmd == 'presale':
        # python eplus_harvest.py presale j-pop <p_start> <p_end> [need]
        genre = sys.argv[2]
        p0 = int(sys.argv[3]); p1 = int(sys.argv[4])
        need = int(sys.argv[5]) if len(sys.argv) > 5 else 60
        status_filter = sys.argv[6] if len(sys.argv) > 6 else '受付前'
        names, eplus_ids, norm = load_db_artists()
        found = {}   # base_eid -> card
        for p in range(p0, p1 + 1):
            url = f'https://eplus.jp/sf/live/{genre}' + ('' if p == 1 else f'/p{p}')
            try:
                html = fetch(url)
            except Exception as e:
                print(f'p{p} ERR {e}'); continue
            cards = parse_kouen(html)
            # 券種で選考しない＝その status の全カードを拾う（[[feedback_capture_all_not_select]]）
            pre = [c for c in cards if c['status'] == status_filter]
            for c in pre:
                if c['eid'] in found:
                    continue
                c['in_db'] = (c['eid'] in eplus_ids) or (norm(c['title']) in names)
                found[c['eid']] = c
            newn = sum(1 for c in found.values() if not c['in_db'])
            print(f"p{p}: {len(cards)}枚 受付前{len(pre)} | 累計uniq受付前 {len(found)} (DB未収録 {newn})")
            time.sleep(0.6)
            if newn >= need:
                print('  → 目標到達'); break
        cand = [c for c in found.values() if not c['in_db']]
        json.dump(cand, open('tmp/eplus_presale.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'=== 受付前(発売前) DB未収録 {len(cand)}件 → tmp/eplus_presale.json ===')
        for c in cand:
            print(f"  {c['eid']} | {c['date']} | {c['title'][:50]}")
        return
    if cmd == 'cards':
        genre = sys.argv[2]
        p0 = int(sys.argv[3]); p1 = int(sys.argv[4])
        names, eplus_ids, norm = load_db_artists()
        allcards = []
        seen = set()
        for p in range(p0, p1 + 1):
            url = f'https://eplus.jp/sf/live/{genre}' + ('' if p == 1 else f'/p{p}')
            try:
                html = fetch(url)
            except Exception as e:
                print(f'p{p} ERR {e}'); continue
            cards = parse_cards(html)
            for c in cards:
                if c['eid'] in seen:
                    continue
                seen.add(c['eid'])
                c['in_db'] = (c['eid'] in eplus_ids) or (norm(c['artist']) in names)
                allcards.append(c)
            print(f'p{p}: {len(cards)}枚 (累計uniq {len(allcards)})')
            time.sleep(0.3)
        json.dump(allcards, open('tmp/eplus_cards.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        new = [c for c in allcards if not c['in_db']]
        print(f'=== 合計 {len(allcards)}件 / DB未収録(新規候補) {len(new)}件 → tmp/eplus_cards.json ===')
        for c in new[:60]:
            print(f"  {c['eid']} | {c['artist']} | {c['desc'][:40]}")


if __name__ == '__main__':
    main()
