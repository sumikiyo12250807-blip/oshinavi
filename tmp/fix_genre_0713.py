# -*- coding: utf-8 -*-
"""新着87件のジャンル下書き(_genre)補正。
_piaSub が空だと build が engeki にフォールバックする（41件全部これ）。実態で振り直す。
ユーザー指示(7/11)＝科学/恐竜/施設はイベントアート(art)、子ども体験はキッズ(kids)。
fes定義＝複数組＋屋外（屋内はfesにしない）。
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

FIX = {
    # 展覧会・美術展・企画展・科学/恐竜/施設系 → art（イベントアート）
    2519: 'art',   # 真アギト展
    2522: 'art',   # WIND BREAKER 展
    2523: 'art',   # 長嶋茂雄追悼展
    2525: 'art',   # THE FACT MUSIC AWARDS EXHIBITION
    2528: 'art',   # エリック・カール展
    2532: 'art',   # ジャパンレプタイルズショー(爬虫類展示即売)
    2534: 'art',   # 大恐竜展
    2537: 'art',   # 未確認生物(UMA)展
    2540: 'art',   # 岩合光昭 写真展
    2541: 'art',   # トムとジェリー展
    2542: 'art',   # 銀魂展
    2543: 'art',   # ふれあい昆虫ランド（科学・展示）
    2545: 'art',   # ごんぎつね40周年展
    2546: 'art',   # チームラボ 学ぶ!未来の遊園地（施設）
    2547: 'art',   # 大英博物館日本美術コレクション
    2550: 'art',   # しあわせのぬいぐるみパーク展
    2551: 'art',   # 光が死んだ夏展
    2579: 'art',   # みほとけのキセキIII
    2580: 'art',   # 巴水・夢二・暁斎 美紙展
    2581: 'art',   # 華麗なる武家の纏うKIMONO
    2582: 'art',   # シンシナティ美術館展
    2583: 'art',   # 藝大式 美術の“ミカタ”
    2520: 'art',   # 三重の酒を楽しむ会（体験イベント）
    # 子ども向け → kids
    2518: 'kids',  # 里山夕涼み Night Bubble Show（シャボン玉ショー）
    2533: 'kids',  # 0歳からのファミリーコンサート
    2544: 'kids',  # ウルトラヒーローズ THE LIVE
    2549: 'kids',  # 家族で楽しむコンサート（よしお兄さん）
    2552: 'kids',  # おかあさんといっしょ ファンターネ!
    # 音楽
    2538: 'jpop',  # wacci
    2585: 'jpop',  # One Dream FESTIVAL in 琴似（ペニーレーン24＝屋内なのでfesにしない）
    # お笑い
    2539: 'owarai',  # あばれる君 熱血授業
    # 演劇・ダンス・朗読
    2526: 'engeki',  # DANCE ATTACK!!（ダンス＝engeki据置）
    2529: 'engeki',  # 今宵、怪談へ行く。北野文芸座（怪談ライブ）
    2530: 'engeki',  # 今宵、怪談へ行く。弥彦体育館
    # 花火
    2535: 'hanabi',  # なにわ淀川花火大会 ぴあシート
    # 伝統
    2524: 'dento',   # 長崎くんち（伝統祭・観覧券）
    # youtuber
    2521: 'youtuber',  # 莉犬(すとぷり)のSTPRadio! STPR文化祭
}

# ⚠️相談（ユーザー判断が要るもの）
SODAN = {
    2527: '⚠️アークラ大サーカス2026「会場内駐車場」＝駐車券のみのエントリ。公演本体でないので載せるか要判断',
    2531: '⚠️秋季金剛界結縁灌頂（高野山 金剛峯寺の宗教儀式・参加券）＝dento(伝統) か art(イベント) か',
    2536: '⚠️松本怜生トークショー（俳優のトークショー・大学講義室）＝engeki か art か',
    2548: '⚠️夏井いつき句会ライブ（俳句ライブ）＝owarai か art か engeki か',
    2503: '⚠️飛生芸術祭2026「トビウの祝祭」＝屋外の芸術祭。下書きfesだが art の可能性',
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

changed = []
for e in E:
    i = e['id']
    if i in FIX and e.get('genre') == 'new':
        old = e.get('_genre')
        if old != FIX[i]:
            e['_genre'] = FIX[i]
            changed.append((i, e.get('artist', '')[:38], old, FIX[i]))

print(f'=== ジャンル下書き補正 {len(changed)}件 ===')
for i, a, o, n in changed:
    print(f'  id{i} {a} : {o} → {n}')

print(f'\n=== ⚠️相談 {len(SODAN)}件 ===')
byid = {e['id']: e for e in E}
for i, msg in SODAN.items():
    e = byid.get(i)
    print(f"  id{i} [{e.get('_genre') if e else '?'}] {msg}")

bak = f'index.html.bak_{datetime.date.today():%m%d}_genre_draft'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print(f'\n(backup {bak})')
