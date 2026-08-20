# -*- coding: utf-8 -*-
"""7/10 新着プール49件(2249-2298) ジャンル振り分け。
下書き_genre = ぴあカテゴリ由来なので原則そのまま([[project_vendor_genre_autoassign]])。
人が直すのは _piaSub 空/その他 のフォールバック誤りと、ぴあが1カテゴリに混ぜてる子だけ。"""
import re, json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

# 下書き補正（理由つき）
override = {
    2264: 'jpop',     # WATWING(_piaSub空→engekiフォールバック)。Zepp Sapporo のダンスボーカルGライブ＝音楽
    2270: 'fes',      # ONE PARK HANGOUTFES in OYABE(_piaSub空)。屋外特設・雨天決行10-20時＝fes定義該当
    2274: 'classic',  # マーチング・イン・オカヤマ(音楽その他→fes下書き)。屋内(岡山市総合文化体育館)＝fes非該当・吹奏楽
    2272: 'dento',    # 三曲ジュニアフェスティバル(演歌・邦楽→enka下書き)。箏/三味線/尺八＝邦楽
}
# 両方方式（主ジャンル＋extraGenres）[[feedback_genre_both_when_unclear]]
extra = {
    2295: ['engeki'],  # 熊川哲也 K-BALLET『クレオパトラ』＝バレエ(classic+engeki)
    2296: ['engeki'],  # 熊川哲也 K-BALLET『白鳥の湖』＝バレエ(classic+engeki)
    2269: ['anime'],   # プロセカ ファンミーティング＝ゲーム/ボカロ由来
}
# プール外だが plan.md の宿題（ジャンル相談2件）
outside = {
    2144: ('jpop', ['engeki']),   # 真風涼帆 特別公演＝元宝塚トップ・歌と舞台の両面
    2240: ('engeki', ['jpop']),   # カズキのタネ(s**t kingz kazuki)＝ダンス+音楽
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
tally = Counter(); n = 0
for e in EVENTS:
    i = e['id']
    if i in outside:
        g, ex = outside[i]
        e['genre'] = g; e['extraGenres'] = ex
        print(f'  [宿題] {i} {e["artist"][:22]} -> {g} + {ex}')
        continue
    if e.get('genre') != 'new': continue
    g = override.get(i, e.get('_genre'))
    if not g or g == 'new':
        print("!! unresolved", i, e.get('_genre')); continue
    e['genre'] = g
    if i in extra:
        e['extraGenres'] = extra[i]
    for k in ('_genre', '_piaSub', '_extraGenres'):
        e.pop(k, None)
    tally[g] += 1; n += 1
print(f"\n=== assigned {n} 件 ===")
for k, v in sorted(tally.items(), key=lambda x: -x[1]):
    print(f"   {k}: {v}")
newh = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
if re.search(r'(const NEW_ORDER = )\[[^\]]*\](;)', newh):
    newh = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\1[]\2', newh, count=1)
    print("NEW_ORDER cleared")
if DRY:
    print("(DRY)")
else:
    open('index.html.bak_0710_assign','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(newh)
    print("written (backup: index.html.bak_0710_assign)")
