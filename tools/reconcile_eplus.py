#!/usr/bin/env python3
"""e+チケットを各公演の専用-P頁のJSON-LD(真値)と機械照合するQCゲート。

「日付・県は絶対に間違えない」を保証する。各e+チケットの t['url'](-P頁)を独立fetchし、
その頁の単一LD(公演日/時刻/会場/県)＝真値と突合。1件でもFAILなら exit 1（投入/pushブロック）。
文字列はすべてブール/日付で比較する＝端末の文字化けに一切依存しない（[[feedback_no_mojibake_japanese_read]]）。

使い方:
  python tools/reconcile_eplus.py --new         # genre:"new" だけ
  python tools/reconcile_eplus.py --ids 3047,3052
  python tools/reconcile_eplus.py --all         # e+ URLを持つ全エントリ(重い)

チェック: (a)締切<=公演日 (b)窓一致 (c)死枠(予定枚数終了/受付終了) (d)県一致
          (e)発売前なのに将来窓なし (f)公演日一致 (g)LD粒度==1 (h)同日複数公演の時刻一致
"""
import json, re, sys, datetime, html as H
sys.path.insert(0, 'tools')
from eplus_harvest import fetch, parse_ld

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

TODAY = datetime.date.today()

def load():
    h = open('index.html', encoding='utf-8').read()
    m = re.search(r'(?:const|var)\s+EVENTS\s*=\s*(\[.*?\]);', h, re.S) or re.search(r'events\s*=\s*(\[.*?\]);', h, re.S)
    return json.loads(m.group(1))

_PERIOD = re.compile(r'受付期間:(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})～(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)(\d{1,2}):(\d{2})')
_DEAD = ('予定枚数終了', '受付終了', '販売終了', '完売', '受付は終了')

def parse_blocks(html):
    """各 <section class="block-ticket"> → {sd,ed,et,status}。status=open/before/ended/unknown"""
    out = []
    for s in re.split(r'(?=<section class="block-ticket">)', html):
        if not s.startswith('<section class="block-ticket">'):
            continue
        body = s.split('</section>', 1)[0]
        txt = re.sub(r'<[^>]+>', ' ', H.unescape(body))
        m = _PERIOD.search(re.sub(r'\s+', ' ', txt))
        if not m:
            continue
        g = m.groups()
        sd = datetime.date(int(g[0]), int(g[1]), int(g[2]))
        ed = datetime.date(int(g[5]), int(g[6]), int(g[7]))
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
        out.append({'sd': sd, 'ed': ed, 'st': f'{int(g[3])}:{g[4]}', 'et': f'{int(g[8])}:{g[9]}', 'status': status})
    return out

def norm_pref(p):
    return re.sub(r'[都道府県]$', '', (p or '').strip())

def hm(s):
    """'18:00'/'9:00' → (18,0)/(9,0)。表記ゆれを吸収して時刻比較する。"""
    m = re.match(r'(\d{1,2}):(\d{2})', s or '')
    return (int(m.group(1)), int(m.group(2))) if m else None

def badge_deadline(ty):
    """type の（…公演）より後ろから締切/発売の時刻を取る。
    受付中「〜M/D HH:MM」→('close','HH:MM')／発売前「M/D HH:MM発売」→('sale','HH:MM')。無→None"""
    seg = re.sub(r'^.*[）)]', '', ty)
    m = re.search(r'〜\s*\d{1,2}/\d{1,2}(?:\s+(\d{1,2}:\d{2}))?', seg)
    if m:
        return ('close', m.group(1))
    m = re.search(r'\d{1,2}/\d{1,2}\s+(\d{1,2}:\d{2})\s*発売', seg)
    if m:
        return ('sale', m.group(1))
    return None

def parse_type(ty):
    """type '…（県 M/D [HH:MM]公演）…' → (pref, (M,D), 'HH:MM' or None)"""
    m = re.search(r'[（(]\s*([^\s0-9（()]+?)\s+(\d{1,2})/(\d{1,2})(?:\s+(\d{1,2}:\d{2}))?', ty)
    if not m:
        return (None, None, None)
    return (m.group(1), (int(m.group(2)), int(m.group(3))), m.group(4))

def eplus_tickets(e):
    for ti, t in enumerate(e.get('tickets') or []):
        u = t.get('url') or ''
        if 'eplus.jp/sf/detail/' in u:
            yield ti, t, u

def main():
    args = sys.argv[1:]
    evs = load()
    if '--ids' in args:
        ids = set(int(x) for x in args[args.index('--ids') + 1].split(','))
        targ = [e for e in evs if e.get('id') in ids]
    elif '--new' in args:
        targ = [e for e in evs if e.get('genre') == 'new']
    elif '--all' in args:
        targ = [e for e in evs if any(True for _ in eplus_tickets(e))]
    else:
        print('対象を指定して: --new / --ids a,b / --all'); return 2

    fails = []          # (id, ti, code, detail, url)
    cache = {}
    n_tk = 0
    for e in targ:
        # エントリ内の公演日ごとのチケット数（同日複数=昼夜検知）
        ld_dates = []
        rows = list(eplus_tickets(e))
        for ti, t, u in rows:
            n_tk += 1
            if u not in cache:
                try:
                    cache[u] = fetch(u)
                except Exception as ex:
                    cache[u] = None
            html = cache[u]
            if not html:
                fails.append((e['id'], ti, 'FETCH', 'ページ取得失敗', u)); continue
            ld = parse_ld(html)
            if len(ld) != 1:
                fails.append((e['id'], ti, 'g-粒度', f'LD公演数={len(ld)}(≠1)', u)); continue
            L = ld[0]
            tp, tmd, ttime = parse_type(t.get('type', ''))
            ld_dates.append((L['date'], u))
            # (f) 公演日
            if tmd and L['date']:
                lm, ld_ = int(L['date'][5:7]), int(L['date'][8:10])
                if (lm, ld_) != tmd:
                    fails.append((e['id'], ti, 'f-公演日', f'type={tmd[0]}/{tmd[1]} != LD={lm}/{ld_}', u))
            # (d) 県
            if tp is not None and L['pref']:
                if norm_pref(tp) != norm_pref(L['pref']):
                    fails.append((e['id'], ti, 'd-県', f'type_pref!=LD_pref (LD={L["pref"]})', u))
            # (a) 締切<=公演日
            if t.get('date') and L['date'] and t['date'] > L['date']:
                fails.append((e['id'], ti, 'a-締切>公演日', f"締切{t['date']} > 公演{L['date']}", u))
            # 窓＝実ページの窓を真値とし、storedを日付+時刻で比較する
            #   (Fable第4分析：一致窓を"探す"のでなく現在窓と"比較"＝表示ズレを必ず検出)
            blocks = parse_blocks(html)
            sd = t.get('startDate')
            bdl = badge_deadline(t.get('type', ''))
            if sd:   # 発売前（発売日sdで自分の窓を特定・同頁に複数before窓ありうる＝プレオーダー+一般）
                same = [b for b in blocks if b['sd'].isoformat() == sd]
                openw = [b for b in blocks if b['status'] == 'open' and b['sd'] <= TODAY <= b['ed']]
                if not same:
                    if openw:
                        fails.append((e['id'], ti, 'b-発売前化', f'発売前登録(sd={sd})だが実頁は受付中(sd一致before窓なし)', u))
                    else:
                        fails.append((e['id'], ti, 'b-発売日ズレ', f'発売日{sd}のbefore窓が実頁に無い', u))
                elif all(b['status'] == 'ended' for b in same):
                    fails.append((e['id'], ti, 'c-死枠', f'発売日{sd}の窓が受付終了/予定枚数終了', u))
                else:
                    W = same[0]
                    if t.get('date') and t['date'] != W['ed'].isoformat():
                        fails.append((e['id'], ti, 'b-締切ズレ', f"date {t['date']} != 実 {W['ed']}", u))
                    if bdl and bdl[0] == 'sale' and bdl[1] and hm(bdl[1]) != hm(W['st']):
                        fails.append((e['id'], ti, 'b-発売時刻ズレ', f"badge発売 {bdl[1]} != 実 {W['st']}", u))
            else:    # 受付中（open窓＝真値。storedのedがopen窓と一致するか＋締切時刻を照合）
                openw = [b for b in blocks if b['status'] == 'open' and b['sd'] <= TODAY <= b['ed']]
                if not openw:
                    beforew = [b for b in blocks if b['status'] == 'before' and b['ed'] >= TODAY]
                    if beforew:
                        # 受付中登録だが実頁は「これから発売」＝死枠でなく発売前化(救済＝startDate付与)
                        fails.append((e['id'], ti, 'b-発売前化', '受付中登録だが実頁は発売前(今後開く窓あり)', u))
                    else:
                        fails.append((e['id'], ti, 'c-死枠', '受付中だが実頁にopen/before窓なし(全窓終了)', u))
                else:
                    match = [b for b in openw if b['ed'].isoformat() == (t.get('date') or '')]
                    if match:
                        W = match[0]
                        if bdl and bdl[0] == 'close' and bdl[1] and hm(bdl[1]) != hm(W['et']):
                            fails.append((e['id'], ti, 'b-締切時刻ズレ', f"badge締切 {bdl[1]} != 実 {W['et']}", u))
                    else:
                        eds = ','.join(b['ed'].isoformat() for b in openw)
                        fails.append((e['id'], ti, 'b-締切ズレ', f"date {t.get('date')} != open窓ed[{eds}]", u))
        # (h) 同日複数公演の時刻。「同日で別URL(別公演)が2つ以上」の時だけ＝
        #     同URL(同一公演の別券種)は昼夜ではないので時刻を要求しない
        date_urls = {}
        for d, uu in ld_dates:
            date_urls.setdefault(d, set()).add(uu)
        for ti, t, u in rows:
            if not cache.get(u):
                continue
            ld = parse_ld(cache[u])
            if len(ld) != 1:
                continue
            L = ld[0]
            if len(date_urls.get(L['date'], set())) >= 2:   # 同日・別公演が2つ以上
                _, _, ttime = parse_type(t.get('type', ''))
                if L['time'] and ttime and ttime != L['time']:
                    fails.append((e['id'], ti, 'h-時刻', f'type時刻{ttime} != LD{L["time"]}', u))
                elif L['time'] and not ttime:
                    fails.append((e['id'], ti, 'h-時刻欠', f'同日複数公演だがバッジに時刻なし(LD={L["time"]})', u))

    # レポート（ASCII/日付のみ・日本語は出さない＝化けない）
    print(f"=== reconcile_eplus (today={TODAY}) 対象{len(targ)}エントリ / e+チケット{n_tk}枠 ===")
    if not fails:
        print("✅ FAIL 0 — 全チケットが実ページのLDと一致（機械検証済み）")
        return 0
    print(f"🚨 FAIL {len(fails)}件（この枠だけ実ページで見直す）:")
    for cid, ti, code, detail, url in fails:
        print(f"  id{cid} t{ti} [{code}] {detail}")
        print(f"        {url}")
    return 1

if __name__ == '__main__':
    sys.exit(main())
