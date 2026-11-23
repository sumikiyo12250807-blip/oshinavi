# -*- coding: utf-8 -*-
"""「最新CD」ボタンを Amazon の検索結果ではなく商品ページ（/dp/ASIN）へつなぐ試し（2026-11-23 すちこ「2と3を試してみて」）。

Why: いまの links.amazon は「名前 CD」の検索結果ページ。押した人がそこから選ぶ必要がある＝買われにくい。
     音楽の検索を「新しい順」で引き、商品名にその人の名前が入る1枚目の商品ページへつなぐ。
やり方: links.amazon（検索）はそのまま残し、links.amazonDp（商品ページ）と links.amazonDpTitle（商品名）を足すだけ＝消すのは1行で戻せる。
     画面（renderCard）は amazonDp があればそれを「最新CD」の飛び先にする。
🚨 Amazon は続けて読むと「商品ゼロ」の偽のページを返す（reference_amazon_affiliate）＝8秒あける・0件は20秒あけて1回だけ読み直す・6件続けて0なら止める。
  python tools/amazon_dp.py --pick 40            … 候補を選んで tmp/amazon_dp.json に（読みに行く）
  python tools/amazon_dp.py --apply              … tmp/amazon_dp.json を index.html に（鍵 tmp/x1112/index.lock を取る）
"""
import io, json, os, re, sys, time, unicodedata, urllib.request, urllib.parse, gzip, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools'))
import compact_events as C
OUT = os.path.join(R, 'tmp', 'amazon_dp.json')
LOG = os.path.join(R, 'tmp', 'amazon_dp.txt')
TAG = 'oshinavi0a-22'
MUSIC = {'jpop', 'rock', 'idol', 'kpop', 'hiphop', 'classic', 'anime', 'seiyuu', 'vtuber', 'enka', 'jazz'}
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
norm = lambda s: re.sub(r'[\s　・･\-－_]', '', unicodedata.normalize('NFKC', s or '')).lower()


def fetch(q):
    url = 'https://www.amazon.co.jp/s?' + urllib.parse.urlencode({'k': q, 'i': 'specialty-aps', 'srs': '26200021051', 's': 'date-desc-rank'})
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'ja-JP,ja;q=0.9', 'Accept-Encoding': 'gzip'})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
        if r.headers.get('Content-Encoding') == 'gzip':
            b = gzip.decompress(b)
    return b.decode('utf-8', 'replace')


def results(html):
    out = []
    for m in re.finditer(r'data-asin="([A-Z0-9]{10})"[^>]*data-component-type="s-search-result"(.*?)(?=data-component-type="s-search-result"|$)', html, re.S):
        asin, body = m.group(1), m.group(2)
        t = re.search(r'<h2[^>]*>(.*?)</h2>', body, re.S)
        title = re.sub(r'<[^>]+>', '', t.group(1)).strip() if t else ''
        out.append((asin, re.sub(r'\s+', ' ', title)))
    return out


def pick(n):
    E = C.load(io.open(os.path.join(R, 'index.html'), encoding='utf-8', newline='').read())
    today = datetime.date.today().isoformat()
    soon = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
    cand = []
    for e in E:
        L = e.get('links') or {}
        if e.get('genre') not in MUSIC or not L.get('amazon') or L.get('amazonDp') or L.get('amazonLabel'):
            continue
        if not re.search(r'amazon\.co\.jp/s\?', L['amazon']):
            continue
        a = (e.get('artist') or '').strip()
        if not a or re.search(r'[／/×、]', a) or a == (e.get('name') or '').strip() and len(a) > 20:
            continue
        sd = min([t.get('startDate') or '9999' for t in e.get('tickets') or []] + ['9999'])
        if today <= sd <= soon:
            cand.append((sd, e['id'], a))
    cand.sort()
    log = io.open(LOG, 'w', encoding='utf-8')
    res, zeros = {}, 0
    seen = {}
    for sd, i, a in cand[:n]:
        key = norm(a)
        if key in seen:
            res[str(i)] = seen[key]
            log.write('id%s %s ＝前と同じ名前\n' % (i, a))
            continue
        q = a + ' CD' if not re.search(r'管弦楽団|交響楽団|フィル', a) else a
        rows = []
        for tr in range(2):
            try:
                rows = results(fetch(q))
            except Exception as ex:
                log.write('id%s %s 読めず %s\n' % (i, a, str(ex)[:60]))
            if rows:
                break
            time.sleep(20)
        if not rows:
            zeros += 1
            log.write('id%s %s 0件\n' % (i, a))
            if zeros >= 6:
                log.write('6件続けて0＝止めた\n')
                break
            time.sleep(8)
            continue
        zeros = 0
        # 🆕11/23 試しの1回目で「@JAM → 別グループのアクキー」＝CD でない商品・短すぎる名前は採らない
        GOODS = re.compile(r'アクキー|アクリル|ステッカー|缶バッジ|グッズ|キーホルダー|タオル|Tシャツ|写真集|ポスター|クリアファイル|ブロマイド')
        hit = next(((asin, t) for asin, t in rows if len(key) >= 3 and key in norm(t) and not GOODS.search(t)), None)
        if hit:
            res[str(i)] = {'artist': a, 'asin': hit[0], 'title': hit[1][:120], 'url': 'https://www.amazon.co.jp/dp/%s/?tag=%s' % (hit[0], TAG)}
            seen[key] = res[str(i)]
            log.write('id%s %s → %s %s\n' % (i, a, hit[0], hit[1][:70]))
        else:
            log.write('id%s %s 名前の入った商品なし（上位 %s）\n' % (i, a, ' / '.join(t[:30] for _, t in rows[:3])))
        log.flush()
        time.sleep(8)
    json.dump(res, io.open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log.write('=== 候補 %d・商品ページ %d ===\n' % (min(n, len(cand)), len(res)))


def apply():
    res = json.load(io.open(OUT, encoding='utf-8'))
    LK = os.path.join(R, 'tmp', 'x1112', 'index.lock')
    while True:
        try:
            fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'amazon_dp'); os.close(fd); break
        except FileExistsError:
            time.sleep(10)
    try:
        p = os.path.join(R, 'index.html')
        t = io.open(p, encoding='utf-8', newline='').read()
        E = C.load(t)
        n = 0
        GOODS = re.compile(r'アクキー|アクリル|ステッカー|缶バッジ|グッズ|キーホルダー|タオル|Tシャツ|写真集|ポスター|クリアファイル|ブロマイド')
        for e in E:
            r = res.get(str(e['id']))
            if r and (GOODS.search(r['title']) or len(norm(r['artist'])) < 3):
                r = None
            # 🆕11/23 試しの結果＝「CD コンサート券」の出品・まとめ売り・「FIRE」が Firebird に当たった＝外す
            if r and (re.search(r'券|まとめ売り', r['title']) or (re.fullmatch(r'[\x00-\x7f]+', r['artist']) and not re.search(r'(?<![a-z])' + re.escape(r['artist'].lower()) + r'(?![a-z])', r['title'].lower()))):
                r = None
            if r:
                e.setdefault('links', {})['amazonDp'] = r['url']
                e['links']['amazonDpTitle'] = r['title']
                n += 1
        s, end, _ = C.locate(t)
        t = t[:s] + C.dump(E, True, '\r\n') + t[end:]
        io.open(p, 'w', encoding='utf-8', newline='').write(t)
    finally:
        os.remove(LK)
    io.open(LOG, 'a', encoding='utf-8').write('apply %d枚\n' % n)


if __name__ == '__main__':
    if '--pick' in sys.argv:
        pick(int(sys.argv[sys.argv.index('--pick') + 1]))
    elif '--apply' in sys.argv:
        apply()
