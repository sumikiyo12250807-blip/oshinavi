# -*- coding: utf-8 -*-
"""7/4 クラシックCDリンク訂正。イベント名検索で汚れてただけの録音アーティスト/プロオケ13件を
「団体名/演奏家名のみ + CD」のクリーンな検索リンクで復活。純イベント/アマチュアは削除のまま。
ユーザー訂正(2026-07-04)「ないのは付けない・CDあるのは付ける」。"""
import re, json, sys, io, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

# id -> 検索する団体名/演奏家名(イベント語を除いた本体)
NAMES = {
    1928: '東京都交響楽団',
    1929: '東京都交響楽団',
    1937: 'ヴィクトリア・ムローヴァ',
    1944: 'ザハール・ブロン',
    1951: '兵庫芸術文化センター管弦楽団',
    1959: 'トーマス・トロッター',
    1960: '大阪フィルハーモニー交響楽団',
    1961: '大阪フィルハーモニー交響楽団',
    1964: '住谷美帆',
    1972: 'セントラル愛知交響楽団',
    1973: 'セントラル愛知交響楽団',
    1980: '前橋汀子',
    1982: '山形交響楽団',
}

def cd_url(name):
    k = urllib.parse.quote(name + ' CD')
    return f"https://www.amazon.co.jp/s?k={k}&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

done = []
for e in EVENTS:
    if e['id'] in NAMES:
        e.setdefault('links', {})
        e['links']['amazon'] = cd_url(NAMES[e['id']])
        done.append((e['id'], NAMES[e['id']]))
        print(f"  id={e['id']} → 「{NAMES[e['id']]} CD」")
print(f"復活 {len(done)}件")

if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0704_restorecd', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("✅ 完了 (backup: index.html.bak_0704_restorecd)")
