# -*- coding: utf-8 -*-
"""Amazon「最新CD」リンクの実測監査ツール（2026-07-30 新設）

links.amazon の検索クエリを**実際にAmazonで叩いて**商品が並ぶかを確認する。
並ばないものは①イベント名を削った短いクエリで再測 → 当たればクエリ差し替え
②それでも空振りなら「録音が無い企画公演」＝リンクを外す候補にする。

  python tools/amazon_audit.py --sus            # イベント名混入の疑いだけ（既定）
  python tools/amazon_audit.py --new            # genre:new だけ
  python tools/amazon_audit.py --ids 3432,3434
  python tools/amazon_audit.py --all            # 全リンク(重い)
  python tools/amazon_audit.py --apply          # 上記結果(tmp/amazon_audit.json)を適用

【なぜ実測か】memory では「Amazonは503でブロックしWebFetch検証不可」だったが、
2026-07-30 に確認したら HTTP 200 で読める。判定は data-asin の個数（0〜1件＝空振り、
3件以上＝ヒット）。これで「CDが無いのは付けない・あるのは付ける」を推測でなく実測で決められる。
"""
import io, json, re, sys, time, datetime, urllib.parse, urllib.request, html as _html

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

OUT = 'tmp/amazon_audit.json'
WAIT = 8.0            # Amazonを叩く間隔（ブロック回避）
RETRY_WAIT = 20.0     # 0件と出た時に間を置いて単独リトライする待ち
HIT_MIN = 3           # data-asin がこれ以上ならヒットとみなす
STALL_STOP = 6        # これだけ連続で0件が続いたらスロットリング疑いで中断

# 🚨【2026-07-30 実測で判明】3秒間隔で連続アクセスすると Amazon は**商品ゼロの
# ページを返す**（CAPTCHAでもエラーでもない・偽の0件）。辻彩奈=0件/MOMO=0件/
# 神奈川フィル=0件と出たが、間を置いて単独で叩くと 6/26/24件ヒットした。
# → 0件は必ず単独リトライして裏を取る（reconcile_pia の「0枠リトライ」と同じ理屈）。
#   これを入れずに --apply すると**生きているCDリンクを大量に消す**。

# イベント名を示す語。クエリのこの語より前だけを残すと「団体名/演奏家名」になることが多い。
EVENT_RE = re.compile(
    r'(コンサート|リサイタル|演奏会|定期公演|定期|フェスティバル|フェス|音楽祭|'
    r'記念|周年|第[0-9０-９]+回|[0-9０-９]+回目|公演|ツアー|ライブ|ＬＩＶＥ|LIVE|'
    r'祭り|祭|展|EXPO|大会|シリーズ|ガラ|まつり|プロジェクト|教室|ショー|'
    r'スペシャル|プレミアム|ニューイヤー|クリスマス|デュオ|トリオ|カルテット|'
    r'弦楽三重奏|吹奏楽|オペラ|バレエ)')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120 Safari/537.36',
    'Accept-Language': 'ja,en;q=0.8',
}

def amazon_url(kw, with_cd=True):
    """with_cd=False は「名前だけ」で検索する形。クラシックの団体/演奏家は『CD』を
    足すと逆に絞られる（2026-07-30 ユーザー提示URLで判明＝神奈川フィルは
    名前のみ45件 / 「+CD」24件）。memory の「録音があるオケは名前のみで付ける」が正。"""
    k = kw + (' CD' if with_cd else '')
    return ('https://www.amazon.co.jp/s?k=' + urllib.parse.quote(k)
            + '&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22')

def _titles(h):
    out, seen = [], set()
    for t in re.findall(r'<h2[^>]*>.*?<span[^>]*>([^<]{4,160})</span>', h, re.S):
        t = _html.unescape(re.sub(r'\s+', ' ', t)).strip()
        if t and t not in seen:
            seen.add(t); out.append(t)
    return out

def _tokens(kw):
    """検索語の意味のあるトークン（2文字以上）。商品名との照合に使う"""
    parts = re.split(r'[\s　・&＆×／/「」『』《》（）()【】〜～\-－—,、。]+', kw)
    return [p for p in parts if len(p) >= 2]

def probe(kw, with_cd=True):
    """クエリを実測 → (関連ヒット数, err)。
    🚨data-asinの数で判定してはいけない＝Amazonは0件でも「関連商品」を24枚並べる。
    「くらら開館10周年記念事業…」が3件で当たり判定になり、由紀さおり・安田祥子が
    0件で捨てられかけた（2026-07-30）。**商品名に検索語が入っているか**で数える。"""
    req = urllib.request.Request(amazon_url(kw, with_cd), headers=HEADERS)
    try:
        h = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'replace')
    except Exception as ex:
        return None, str(ex)[:80]
    toks = _tokens(kw)
    if not toks:
        return 0, 'クエリ空（curatedリンク等）'
    rel = 0
    for t in _titles(h):
        if any(tok in t for tok in toks):
            rel += 1
    return rel, ''

def probe2(kw, with_cd=True):
    """0件は必ず間を置いて単独リトライしてから確定する（偽0件対策）"""
    n, err = probe(kw, with_cd)
    if n is not None and n < HIT_MIN:
        time.sleep(RETRY_WAIT)
        n2, err2 = probe(kw, with_cd)
        if n2 is not None:
            n = max(n, n2)
    time.sleep(WAIT)
    return n, err

def shorten(kw):
    """イベント名を削って「団体名/演奏家名」だけにした候補を返す（最大2案）"""
    cands = []
    m = EVENT_RE.search(kw)
    if m and m.start() > 0:
        cands.append(kw[:m.start()].strip('　 ・-－—「」『』（）()＆&／/'))
    # 記号区切りの先頭要素（「濱田芳通&アントネッロ第23回定期」→「濱田芳通」）
    head = re.split(r'[&＆×／/「『（(]', kw)[0].strip('　 ・-－—')
    if head and head != kw:
        cands.append(head)
    # 「・」区切りの先頭（「由紀さおり・安田祥子」→「由紀さおり」／
    #  「シエナ・ウインド・オーケストラ わくわくシエナ祭り」→ 空白前まで）。
    # これが無くて由紀さおり・安田祥子（童謡でCD多数）が drop になりかけた（2026-07-30）。
    sp = kw.split(' ')[0].split('　')[0].strip('　 ・-－—')
    if sp and sp != kw:
        cands.append(sp)
    nak = re.split(r'[・]', kw)[0].strip('　 -－—')
    if nak and nak != kw and len(nak) >= 3:
        cands.append(nak)
    # 🚨ハイフン/ダッシュ/波ダッシュで**副題を切る**（2026-07-30 目視で発覚）。
    # 「白鳥の湖-湖に沈む誓い-」は本体が演目そのものなのに、ハイフンを区切りとして
    # 扱っていなかったため4通り全部0件で drop になりかけた（実測「白鳥の湖」=20件）。
    sub = re.split(r'\s*[-－—~〜～]\s*', kw)[0].strip('　 ・「」『』（）()')
    if sub and sub != kw and len(sub) >= 2:
        cands.append(sub)
    # 数字を含む語（生誕150周年・第39回・開館10周年）は検索を殺すので落とす
    nodigit = re.sub(r'[^\s　]*[0-9０-９]+[^\s　]*', ' ', kw)
    nodigit = re.sub(r'\s+', ' ', nodigit).strip('　 ・-－—')
    if nodigit and nodigit != kw and len(nodigit) >= 3:
        cands.append(nodigit)
    seen, out = set(), []
    for c in cands:
        c = re.sub(r'\s+', ' ', c).strip()
        if len(c) >= 2 and c != kw and c not in seen:
            seen.add(c); out.append(c)
    return out[:4]

def program_cands(name):
    """演目（作曲家＋曲名）の候補。オーケストラの企画公演は**団体名より演目**でCDが見つかる
    （2026-07-30 ユーザー指示＝神奈川フィルの第九公演には「ベートーヴェン「第九」」を貼る。
     公演に行く人が聴きたいのはその曲だから、こっちの方が推し活の役に立つ）。"""
    out = []
    for m in re.finditer(r'([^\s　・]{2,12})?[「『《]([^」』》]{2,20})[」』》]', name or ''):
        pre, inner = (m.group(1) or '').strip(), m.group(2)
        if pre:
            out.append('%s「%s」' % (pre, inner))
        out.append(inner)
    seen, uniq = set(), []
    for c in out:
        if c not in seen and len(c) >= 2:
            seen.add(c); uniq.append(c)
    return uniq[:2]

def load():
    h = io.open('index.html', encoding='utf-8', newline='').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    return h, m, json.loads(m.group(2))

def query_of(amz):
    mk = re.search(r'[?&]k=([^&]+)', amz or '')
    if not mk:
        return ''
    kw = urllib.parse.unquote(mk.group(1))
    return re.sub(r'\s*CD$', '', kw).strip()

def pick(events, mode, ids):
    sel = []
    for ev in events:
        amz = (ev.get('links') or {}).get('amazon')
        if not amz:
            continue
        if mode == 'ids' and ev['id'] not in ids:
            continue
        if mode == 'new' and ev.get('genre') != 'new':
            continue
        kw = query_of(amz)
        # ユーザーがcurateした amzn.to 短縮リンクは検索語を持たない＝監査対象外。
        # （触ると「ユーザー提供リンク優先」を壊す＝2026-07-30 神奈川フィルで危うく上書き）
        if not kw or 'amzn.to' in amz:
            continue
        if mode == 'sus' and not EVENT_RE.search(kw):
            continue
        # 新着プールは genre='new' で本ジャンルは _genre（下書き）にある。fes判定に使うので
        # 実効ジャンルを返す（[[reference_amazon_affiliate]]＝fesは個別CDを付けない）
        sel.append((ev['id'], kw, ev.get('name'), ev.get('_genre') or ev.get('genre')))
    return sel

def main():
    a = sys.argv
    _, _, events = load()
    if '--apply' in a:
        return apply_results()
    mode, ids = 'sus', set()
    if '--all' in a:
        mode = 'all'
    elif '--new' in a:
        mode = 'new'
    elif '--ids' in a:
        mode = 'ids'
        ids = {int(x) for x in re.findall(r'\d+', a[a.index('--ids') + 1])}
    sel = pick(events, mode, ids)
    limit = int(a[a.index('--limit') + 1]) if '--limit' in a else len(sel)
    sel = sel[:limit]
    print('=== amazon_audit mode=%s 対象%d件 (間隔%.1f秒) ===' % (mode, len(sel), WAIT))
    res, zero_streak = [], 0
    for n, (eid, kw, name, genre) in enumerate(sel, 1):
        rec = {'id': eid, 'genre': genre, 'name': name, 'kw': kw,
               'action': None, 'newkw': None, 'cd': True, 'hit': None}
        # 🚨fesは多人数名義で「最新CD」が合わないので個別リンクを付けない＝ジャンル共通の
        # 「フェスアイテム」ボタンに任せる（[[reference_amazon_affiliate]]）。
        # 実測すると「Sky Jamboree」等がそれなりにヒットして rewrite になってしまうため、
        # 叩く前に落とす（2026-07-30 id3517）。
        if genre == 'fes':
            rec['action'] = 'drop'
            rec['hit'] = 0
            rec['why'] = 'fesは個別CDを付けない（ジャンル共通ボタン）'
            res.append(rec)
            print('  [%d/%d] id=%s drop (fes=個別CDなし)' % (n, len(sel), eid))
            continue
        # 試す順＝①今のクエリ+CD ②今のクエリ(名前だけ) ③短縮+CD ④短縮(名前だけ)
        # クラシックの団体/演奏家は「CD」を足すと絞られるので②④が効く。
        plan = [(kw, True), (kw, False)]
        for c in shorten(kw):
            plan += [(c, True), (c, False)]
        for c in program_cands(name):          # 最後に演目（曲名）で探す
            plan += [(c, False)]
        hits = []
        for q, cd in plan:
            hit, err = probe2(q, cd)
            hits.append((q, cd, hit))
            if hit is None:
                rec['action'] = 'FETCH-ERR'
                rec['err'] = err
                break
            if hit >= HIT_MIN:
                rec['hit'] = hit
                rec['cd'] = cd
                if q == kw and cd:
                    rec['action'] = 'keep'
                else:
                    rec['action'] = 'rewrite'
                    rec['newkw'] = q
                break
        else:
            rec['action'] = 'drop'
            rec['hit'] = max((x[2] or 0) for x in hits)
        rec['tried'] = [[q, cd, h] for q, cd, h in hits]
        res.append(rec)
        zero_streak = zero_streak + 1 if rec['action'] == 'drop' else 0
        print('  [%d/%d] id=%s %s hit=%s%s'
              % (n, len(sel), eid, rec['action'], rec['hit'],
                 ' → k=%s%s' % (rec['newkw'], '' if rec['cd'] else ' (CD語なし)')
                 if rec['newkw'] else ('' if rec['cd'] else ' (CD語なし)')))
        if zero_streak >= STALL_STOP:
            print('  ⚠️ %d件連続で0件＝スロットリング疑い。ここで中断する（残りは未測定）。'
                  % zero_streak)
            break
    json.dump(res, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    c = {}
    for r in res:
        c[r['action']] = c.get(r['action'], 0) + 1
    print('\n=== 結果: %s → %s (適用は --apply) ===' % (json.dumps(c, ensure_ascii=False), OUT))
    if c.get('drop'):
        print('   ※dropは「4通り試して全部0件」＝録音が無い企画公演の候補。'
              '適用前に必ず目視すること（偽0件で生きたリンクを消さないため）。')

def apply_results():
    res = json.load(io.open(OUT, encoding='utf-8'))
    h, m, events = load()
    NL = '\r\n' if '\r\n' in h else '\n'
    M = {e['id']: e for e in events}
    nrw = ndr = 0
    for r in res:
        ev = M.get(r['id'])
        if not ev:
            continue
        lk = ev.get('links') or {}
        if r['action'] == 'rewrite' and r.get('newkw'):
            lk['amazon'] = amazon_url(r['newkw'], r.get('cd', True))
            nrw += 1
        elif r['action'] == 'keep' and not r.get('cd', True):
            lk['amazon'] = amazon_url(r['kw'], False)   # 同じ語だが「CD」を外す形が当たった
            nrw += 1
        elif r['action'] == 'drop':
            lk.pop('amazon', None)
            ndr += 1
    bak = 'index.html.bak_%s_amazon' % datetime.date.today().strftime('%m%d')
    io.open(bak, 'w', encoding='utf-8', newline='').write(h)
    new_arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
    io.open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('=== 適用: クエリ差し替え %d件 / リンク削除 %d件 (backup %s) ===' % (nrw, ndr, bak))

if __name__ == '__main__':
    main()
