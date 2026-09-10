# -*- coding: utf-8 -*-
"""9/11発売のX投稿の素材を、投稿の束ごとに組み立てる（Fableに渡す1枚を作る）。

台本＝X_SCRIPT.md
 ・明日発売は**その束の分を1件も削らず**並べる（1行＝「時刻 名前／県」）
 ・2〜3日後は**5件くらい・箱の大きさで選ぶ**＋「他にも◯件以上」（10の位で切り下げ・10未満は実数）
 ・件数の実数は本文に書かない（「他にも◯件以上」だけが例外）
"""
import collections
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

TOMORROW, D2, D3 = '2026-09-11', '2026-09-12', '2026-09-13'

# 投稿の束＝(見出し, ジャンル記号のリスト, URLに使うgenre)
BUNDLES = [
    ('クラシックとジャズ', ['classic', 'jazz'], 'classic'),
    ('落語・お笑い', ['owarai'], 'owarai'),
    ('音楽（JPOP・ロック・K-POP・演歌ほか）', ['jpop', 'rock', 'kpop', 'enka', 'dinnershow',
                                'hougaku', 'musicetc', 'yougaku'], 'jpop'),
    ('舞台・伝統芸能・スポーツ・展示', ['musical', 'engeki', 'dento', 'art', 'gakusai',
                          'sports', 'kids', 'fes', '2.5ji', 'seiyuu', 'aisatsu',
                          'fanevent', 'anime', 'idol'], 'engeki'),
]

# 箱の大きさ＝会場名で大まかに判定（2〜3日後の5件を選ぶため）
BIG = re.compile(r'アリーナ|ドーム|Zepp|ZEPP|国際フォーラム|大ホール|hitaru|ホールA|'
                 r'サントリーホール|フェスティバルホール|オーチャード|NHKホール|'
                 r'武道館|文化会館|市民会館|センチュリーホール|フォーラム|パシフィコ|'
                 r'グランドホール|コンサートホール|歌劇場|劇場')

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))


def timeof(t):
    m = re.search(r'(\d{1,2}):(\d{2})', t.get('type') or '')
    return '%02d:%02d' % (int(m.group(1)), int(m.group(2))) if m else '99:99'


def is_senko(t):
    ty = t.get('type') or ''
    return any(w in ty for w in ('先行', 'プレリザーブ', 'プリセール', 'プレリク',
                                 'プレオーダー', '抽選'))


def rows(day, genres=None):
    out = []
    for e in EVENTS:
        g = e.get('genre')
        if g == 'new':
            continue
        if genres and g not in genres:
            continue
        for t in e.get('tickets') or []:
            if t.get('startDate') == day and not t.get('soldout'):
                out.append((e, t))
    return out


PREF_IN_TYPE = re.compile(r'（([^）0-9]+?)\s*(?:R[0-9]+年\s*)?[0-9]{1,2}/[0-9]{1,2}')


def line(e, t):
    nm = (e.get('artist') or e.get('name') or '').strip()
    # 🚨県は**その枠の県**を使う。エントリの prefecture だとツアーで全県が並び、
    #   「その県も明日発売」と誤読される（2026-09-10 春風亭昇太で実際に起きた）
    m = PREF_IN_TYPE.search(t.get('type') or '')
    pref = (m.group(1).strip() if m else (e.get('prefecture') or '').strip())
    return '%s %s／%s%s' % (timeof(t).replace('99:99', '--:--'), nm, pref,
                           '（先行）' if is_senko(t) else '')


def floor10(n):
    return n if n < 10 else (n // 10) * 10


out = io.open('tmp/x_material_0911.md', 'w', encoding='utf-8')
w = out.write

w('# 9/11(金)発売 X投稿の素材（2026-09-10 作成）\n\n')
w('今日＝2026-09-10(木)／明日＝**9/11(金)**／2日後＝9/12(土)／3日後＝9/13(日)\n\n')
w('🚨トレンド枠＝**今回は無し**。'
  'Xのトレンドはブラウザのウィンドウが最小化されていて読めなかった（取れなかったものは書かない）。\n\n')

w('---\n\n## ★主役枠（3本・1組1本）\n\n')
w('''### 主役1 なとり（id7328）
- **明日9/11(金)18:00** プレリザーブ受付開始（先行）／受付は9/28まで
- 公演＝**2027年6月25日(金)・26日(土) Zepp Sapporo（北海道）**
- 参考＝Xのフォロワー数は取得できず。**Instagram 32.5万／TikTok 43.8万**（2026-09-10 検索実測）
- 🚨**先行なので「誰でも買える」ように書かない**。「プレリザーブ＝先行受付」と明記する
- URL＝`oshinavi.jp/?q=なとり`

### 主役2 野村萬斎（id3000）
- **明日9/11(金)10:00** 一般発売
- 公演＝**還暦記念「狂言ござる乃座 in NAGOYA 29th」2026年10月12日(月) 名古屋能楽堂（愛知）**
- うちには野村萬斎の公演が12件ある（松戸10/16・立川11/13・座間11/25・京都11/15・
  かつしか12/4・鹿児島11/28・国立能楽堂10/21〜24 ほか）＝**「他の会場もある」と書ける**
- URL＝`oshinavi.jp/?q=野村萬斎`

### 主役3 春風亭昇太（id1141／id4620）
- **明日9/11(金)10:00** 一般発売
- 公演＝**2026年12月10日(木) かめありリリオホール（東京）の独演会**
- 🚨**うちに同じ12/10の独演会が2エントリある**（「春風亭昇太 独演会」と
  「かめあり亭 第93弾! 春風亭昇太 独演会 -春らんまん。Part.14-」）。
  **同じ公演なので、投稿では1行にまとめて書く**
- ほかに 小朝との二人会（R9年1/10 関内ホール）、柳家三三との新春公演（R9年1/6 なかのZERO）もうちにある
- URL＝`oshinavi.jp/?q=春風亭昇太`

''')

w('---\n\n## ★まとめ枠\n\n')
for title, genres, gkey in BUNDLES:
    rs = rows(TOMORROW, genres)
    if not rs:
        continue
    w('### 「%s」\n\n' % title)
    w('URL＝`oshinavi.jp/?genre=%s&status=urgent`\n\n' % gkey)
    w('**明日 9/11(金)発売（この束はこれで全部＝1件も削らない）**\n\n```\n')
    seen = set()
    for e, t in sorted(rs, key=lambda x: (timeof(x[1]), x[0]['id'])):
        ln = line(e, t)
        if ln in seen:          # 同じ組・同じ時刻・同じ県の重複行は畳む
            continue
        seen.add(ln)
        w(ln + '\n')
    w('```\n\n')

    for day, lab in ((D2, '9/12(土)'), (D3, '9/13(日)')):
        rs2 = rows(day, genres)
        if not rs2:
            continue
        big = [x for x in rs2 if BIG.search(x[0].get('venue') or '')]
        seen2, pick = set(), []
        for x in (big or rs2):
            ln = line(*x)
            if ln in seen2:          # 同じ組・同じ時刻・同じ県は畳む
                continue
            seen2.add(ln)
            pick.append(x)
            if len(pick) >= 5:
                break
        pick = sorted(pick, key=lambda x: timeof(x[1]))
        w('**%s発売（この束から5件・箱の大きい順に選んである）**\n\n```\n' % lab)
        for e, t in pick:
            w(line(e, t) + '\n')
        rest = len(rs2) - len(pick)
        if rest > 0:
            # 台本＝10の位で切り下げて「◯件以上」。**10未満はそのままの数**
            w('他にも%d件%s\n' % (floor10(rest), '以上' if rest >= 10 else ''))
        w('```\n\n')
    w('\n')

w('---\n\n## 数の確認（本文には実数を書かない）\n\n```\n')
for day, lab in ((TOMORROW, '明日 9/11'), (D2, '2日後 9/12'), (D3, '3日後 9/13')):
    rs = rows(day)
    byg = collections.Counter(e.get('genre') for e, t in rs)
    w('%s … %d本 / %dジャンル  %s\n' % (lab, len(rs), len(byg), dict(byg.most_common(8))))
w('```\n')
out.close()
print('→ tmp/x_material_0911.md')
