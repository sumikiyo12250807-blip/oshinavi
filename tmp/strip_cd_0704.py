# -*- coding: utf-8 -*-
"""7/4 クラシック新着の「最新CD」リンク掃除。ハーベスタがイベント名/定期公演名まるごと
+CDで検索URLを作り「最新CD」として不成立(合ってない)なもの26件のlinks.amazonを削除。
演奏家/団体名のみのクリーンな検索10件は残す。ユーザー指示(2026-07-04)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

# イベント名検索=合ってない=削除
DEL = {1928,1929,1933,1934,1937,1939,1944,1947,1951,1959,1960,1961,1964,
       1967,1968,1969,1970,1971,1972,1973,1974,1975,1976,1980,1982,1983}
# 演奏家/団体名のみ=残す(参考)
KEEP = {1931,1938,1940,1941,1942,1943,1946,1950,1977,1981}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

done = []
for e in EVENTS:
    if e['id'] in DEL:
        L = e.get('links') or {}
        if L.get('amazon'):
            L.pop('amazon', None)
            e.pop('amazonLabel', None)
            done.append(e['id'])
print(f"CDリンク削除 {len(done)}件: {sorted(done)}")
notfound = DEL - set(done)
if notfound:
    print("⚠️ amazon無し(既に無い):", sorted(notfound))
# 残す側の確認
kept = [e['id'] for e in EVENTS if e['id'] in KEEP and (e.get('links') or {}).get('amazon')]
print(f"残したCDリンク {len(kept)}件: {sorted(kept)}")

if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0704_stripcd', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("✅ 完了 (backup: index.html.bak_0704_stripcd)")
