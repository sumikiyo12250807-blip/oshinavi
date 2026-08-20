# -*- coding: utf-8 -*-
"""音楽ジャンルなのに links.amazon が無いエントリへ「最新CD」リンクを実測で付ける。

なぜ落ちていたか＝ぴあのbundleページでカテゴリが取れず _genre が engeki に倒れていたため、
build_pia_entries の「音楽ジャンルならCDリンク」判定に載らなかった（振り分けで是正済み）。

🚨 推測で貼らない＝Amazonを実際に叩いて data-asin のユニーク数で在庫を確認する。
🚨 連続アクセスすると「商品ゼロのページ」を無言で返してくる（[[reference_amazon_affiliate]]）。
   間隔8秒・0件は20秒空けて必ず単独リトライする。
"""
import re, io, sys, json, time, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
TARGETS = {
    4388: 'HOSHIKUMA MINAMI',
    4397: 'TOOBOE',
    4409: '清水翔太',
    4412: 'T.M.Revolution',
    4413: 'DeNeel',
    4415: 'Tohji',
    4416: 'PENTAGON',
    4420: 'Suchmos',
}
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')


def amazon_url(kw):
    return ('https://www.amazon.co.jp/s?k=%s&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22'
            % urllib.parse.quote(kw))


def count_hits(kw):
    req = urllib.request.Request(amazon_url(kw), headers={'User-Agent': UA})
    try:
        html = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'ignore')
    except Exception as ex:
        return -1, str(ex)[:50]
    asins = set(re.findall(r'data-asin="([A-Z0-9]{10})"', html))
    return len(asins), ''


results = {}
for i, (eid, name) in enumerate(TARGETS.items(), 1):
    kw = '%s CD' % name
    n, err = count_hits(kw)
    if n <= 1:
        time.sleep(20)          # 偽の0件を疑って単独リトライ
        n, err = count_hits(kw)
    results[eid] = {'kw': kw, 'hits': n, 'err': err}
    print('[%d/%d] id%s %-18s → %s件 %s' % (i, len(TARGETS), eid, name, n, err), flush=True)
    time.sleep(8)

ok = {k: v for k, v in results.items() if v['hits'] >= 3}
ng = {k: v for k, v in results.items() if v['hits'] < 3}
print('\n貼る %d件 / 貼らない %d件' % (len(ok), len(ng)))
for k, v in ng.items():
    print('  見送り id%s %s（%s件）' % (k, v['kw'], v['hits']))

if not APPLY:
    print('（判定のみ。適用するなら --apply）')
    sys.exit(0)

src = io.open('index.html', encoding='utf-8', newline='').read()
before = src.count('\r\n')
pos = [(int(m.group(1)), m.start()) for m in re.finditer(r'\n\s*"id": (\d+),', src)]
added = 0
for eid, v in ok.items():
    idx = next((i for i, (k, _) in enumerate(pos) if k == eid), None)
    if idx is None:
        print('  ⚠️ id%s が見つからない' % eid); continue
    s = pos[idx][1]
    e = pos[idx + 1][1] if idx + 1 < len(pos) else len(src)
    seg = src[s:e]
    if '"amazon"' in seg:
        print('  すでに amazon 有り id%s' % eid); continue
    m = re.search(r'("eplus": [^\n]*?)(\r?\n\s*\},)', seg)
    if not m:
        print('  ⚠️ links ブロックが見つからない id%s' % eid); continue
    tail = m.group(1).rstrip().rstrip(',')
    ins = '%s,\n      "amazon": "%s"%s' % (tail, amazon_url(v['kw']), m.group(2))
    seg2 = seg[:m.start()] + ins + seg[m.end():]
    src = src[:s] + seg2 + src[e:]
    pos = [(int(mm.group(1)), mm.start()) for mm in re.finditer(r'\n\s*"id": (\d+),', src)]
    added += 1
    print('  付けた id%s %s' % (eid, v['kw']))

print('CRLF: %d → %d' % (before, src.count('\r\n')))
if added:
    io.open('index.html.bak_0817_amazon', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました %d件（backup: index.html.bak_0817_amazon）' % added)
