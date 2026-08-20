# -*- coding: utf-8 -*-
"""新着プールの下書き _genre を是正する（振り分け前の下ごしらえ）。

なぜ直すのか＝ぴあのbundleページはカテゴリ(_piaSub)が取れず、名前ベースのfallbackが
engeki に倒れてしまう。fes も「音楽その他」マッピングで屋内公演に付いてしまう。
[[project_vendor_genre_autoassign]]（人の判断が要るのは _piaSub が空/その他 の少数だけ）
[[feedback_fes_definition]]（fes＝複数組＋屋外。屋内はfesにしない）

🚨 CRLF保持のため newline='' で読み書きし、JSONは作り直さない。
"""
import re, io, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv

# id: (旧, 新, 理由)
FIX = {
    4384: ('engeki', 'jpop',    'ぴあアリーナMM＝屋内。_piaSub=音楽/フェスティバルだがfesは屋外のみ'),
    4388: ('engeki', 'jpop',    'CLUB QUATTRO 3都市の音楽ツアー。bundleでカテゴリが取れず名前fallback'),
    4396: ('fes',    'jpop',    'TACHIKAWA STAGE GARDEN＝屋内。fesにしない'),
    4397: ('engeki', 'jpop',    '音楽アーティストのツアー。bundleでカテゴリが取れず名前fallback'),
    4405: ('fes',    'jpop',    'unravel tokyo＝屋内・単独公演。fesにしない'),
    4409: ('engeki', 'jpop',    '日本武道館の音楽ライブ。bundleでカテゴリが取れず名前fallback'),
    4412: ('engeki', 'jpop',    '音楽アーティストのツアー'),
    4413: ('engeki', 'jpop',    'ライブハウス3都市の音楽ツアー'),
    4414: ('engeki', 'jpop',    'ライブハウス開催のパンクイベント。屋内なのでfesでもない'),
    4415: ('engeki', 'jpop',    '東京ドームの音楽ライブ。日本のラップは既存運用でjpop（梅田サイファー準拠）'),
    4416: ('yougaku', 'kpop',   '韓国のグループ。既存のStray Kids/SEO EUNKWANGと同じkpop'),
    4420: ('engeki', 'jpop',    'アリーナ4会場の音楽ツアー'),
    4421: ('fes',    'classic', 'シネマコンサート＝オーケストラの生演奏。屋内なのでfesではない'),
}

src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')

# エントリ境界
def spans(text):
    pos = []
    for m in re.finditer(r'\n\s*"id": (\d+),', text):
        pos.append((int(m.group(1)), m.start()))
    return pos

done, miss = [], []
for eid, (old, new, why) in FIX.items():
    pos = spans(src)
    s = e = None
    for i, (k, p) in enumerate(pos):
        if k == eid:
            s = p
            e = pos[i + 1][1] if i + 1 < len(pos) else len(src)
            break
    if s is None:
        miss.append((eid, 'エントリが見つからない'))
        continue
    seg = src[s:e]
    pat = '"_genre": "%s"' % old
    if pat not in seg:
        cur = re.search(r'"_genre": "([^"]*)"', seg)
        miss.append((eid, '_genre が %s でない（実際は %s）' % (old, cur.group(1) if cur else 'なし')))
        continue
    seg2 = seg.replace(pat, '"_genre": "%s"' % new, 1)
    src = src[:s] + seg2 + src[e:]
    done.append((eid, old, new, why))

print('=== 下書きジャンルの是正 %d件 ===' % len(done))
for eid, old, new, why in done:
    print('  id%-5s %-8s → %-8s  %s' % (eid, old, new, why))
if miss:
    print('\n⚠️ 直せなかった %d件:' % len(miss))
    for eid, why in miss:
        print('  id%-5s %s' % (eid, why))
print('\nCRLF: %d → %d' % (before_crlf, src.count('\r\n')))

if APPLY:
    io.open('index.html.bak_0817_draft_genre', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました（backup: index.html.bak_0817_draft_genre）')
else:
    print('（判定のみ。適用するなら --apply）')
