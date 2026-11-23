# -*- coding: utf-8 -*-
"""記事（今週のピックアップ）に載せたカードに「記事を読む」ボタンを出すための表を index.html に書く。
2026-11-24 朝 すちこ「記事に載ってるアーティストのところに、記事に行けるぼたんをつけてもいいわね」
  台帳 tools/pickup_articles.json の watch（見るエントリid）→ href を const PICKUP_BY_ID = {...}; に写す。
  記事を足したら回す（下ろした記事＝down も記事のページは残るので載せる）。
使い方: python tools/pickup_card_links.py [--apply] [--lock tmp/x1112/index.lock]"""
import argparse, io, json, os, re, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ap = argparse.ArgumentParser()
ap.add_argument('--apply', action='store_true')
ap.add_argument('--lock', default='')
a = ap.parse_args()
A = json.load(io.open('tools/pickup_articles.json', encoding='utf-8'))['articles']
m = {}
for x in A:
    for i in x.get('watch') or []:
        m.setdefault(str(i), x['href'])   # 1枚に記事が2本ある時は先に載せた方
line = 'const PICKUP_BY_ID = ' + json.dumps(m, ensure_ascii=False, separators=(',', ':')) + ';'
print('記事 %d本 → カード %d枚' % (len(A), len(m)))
if not a.apply:
    sys.exit(0)
if a.lock:
    while True:
        try:
            fd = os.open(a.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'pickup_card_links'); os.close(fd); break
        except FileExistsError:
            time.sleep(10)
try:
    t = io.open('index.html', encoding='utf-8', newline='').read()
    if 'const PICKUP_BY_ID = ' in t:
        t = re.sub(r'const PICKUP_BY_ID = \{[^\n]*\};', lambda _: line, t, count=1)
    else:
        k = t.index('  // ────────────────────────────────────────────────\r\n  //  フィルタリング + 遅延ロード')
        t = t[:k] + '  // 🆕2026-11-24 記事に載せたカード → 記事（tools/pickup_card_links.py が書く）\r\n  ' + line + '\r\n\r\n' + t[k:]
    io.open('index.html', 'w', encoding='utf-8', newline='').write(t)
    print('書いた')
finally:
    if a.lock:
        os.remove(a.lock)
