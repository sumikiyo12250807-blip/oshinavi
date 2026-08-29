# -*- coding: utf-8 -*-
"""独立再導出：_piaSub から正しいジャンルを自分で決めて _genre と突き合わせる。"""
import json, re, collections, unicodedata

new = json.load(open(r'C:\Users\user\oshinavi\tmp\qc_new.json', encoding='utf-8'))

# --- あたし自身の対応表（ルール：ぴあの言う通り／〜その他=musicetc／フェス=fes） ---
MY = {
 # 音楽
 'ジャズ・フュージョン': ('jazz', None),
 'J-POP・ROCK': ('jpop', None),
 '演歌・邦楽': ('SPLIT_HOGAKU', None),
 '童謡・日本のうた': ('douyou', None),
 'アニメ音楽': ('anime', None),
 'シャンソン': ('chanson', None),
 '海外ROCK・POPS': ('yougaku', None),   # 韓国なら kpop（後で名前で判定）
 '民族音楽': ('yougaku', None),
 'フェスティバル': ('fes', None),
 '音楽その他': ('musicetc', None),
 # 演劇
 '演劇': ('engeki', None),
 '朗読・リーディング': ('engeki', None),
 'ミュージカル・ショー': ('musical', None),
 '人形劇・キャラクター': ('kids', None),
 'バレエ・ダンス': ('classic', ['engeki']),
 'パフォーマンス': ('engeki', None),
 '歌舞伎・古典芸能': ('dento', None),
 '寄席・お笑い': ('owarai', None),
 '演劇その他': ('engeki', None),
 # スポーツ（全部 sports）
 'サッカー': ('sports', None), '野球': ('sports', None), 'ラグビー': ('sports', None),
 'バスケットボール': ('sports', None), 'バレーボール': ('sports', None), 'アメフト': ('sports', None),
 '球技その他': ('sports', None), 'プロレス': ('sports', None), 'ボクシング': ('sports', None),
 '格闘技': ('sports', None), '相撲・武道': ('sports', None), 'モータースポーツ': ('sports', None),
 'スイム・マリンスポーツ': ('sports', None),
 'フィギュアスケート・ウィンタースポーツ': ('sports', None),
 'ゴルフ': ('sports', None), 'eスポーツ': ('sports', None), 'ソフトボール': ('sports', None),
 'スポーツその他': ('sports', None),
 # 映画
 '邦画': ('engeki', None), '洋画': ('engeki', None), '舞台挨拶': ('aisatsu', None),
 '映画祭': ('engeki', None), 'ライブビューイング': ('engeki', None), '映画その他': ('musicetc', None),
 # アート
 'アート': ('art', None),
 # イベント
 '講演会・トークショー': ('engeki', None), '子供と楽しむ': ('kids', None),
 'サーカス': ('circus', None), 'マジック・イリュージョン': ('magic', None),
 'ショー・ファンイベント': ('fanevent', None),
 '祭り・花火大会': ('SPLIT_HANABI', None),
 'ディナーショー': ('dinnershow', None),
 '博覧会・展示会・見本市': ('art', None), 'スクール・レジャー': ('kids', None),
 '学園祭': ('gakusai', None), 'アミューズメント': ('kids', None),
 'イベントその他': ('musicetc', None),
 # クラシック（カテゴリ丸ごと classic。ぴあがクラシックと言っている）
 'オーケストラ': ('classic', None), '器楽・室内楽': ('classic', None),
 'オペラ・声楽': ('classic', None), '吹奏楽': ('classic', None), '合唱': ('classic', None),
 'クラシック邦楽': ('classic', None),
 'フェスティバル・ガラコンサート': ('classic', None),
 'クラシックその他': ('classic', None),
}

HOGAKU_RE = re.compile(r'和太鼓|太鼓|三味線|津軽|琴|箏|筝|尺八|雅楽|民謡|和楽器|邦楽|篠笛|笙|能楽|長唄|常磐津'
                       r'|琵琶|義太夫|清元|新内|小唄|端唄|地唄|浄瑠璃|詩吟|囃子|能舞台'
                       r'|taiko|shamisen|shakuhachi|gagaku|wagakki|biwa')

def my_genre(sub, name):
    if sub not in MY:
        return None, None, 'UNKNOWN_SUB'
    g, ex = MY[sub]
    if g == 'SPLIT_HOGAKU':
        n = unicodedata.normalize('NFKC', name or '').lower()
        return ('dento' if HOGAKU_RE.search(n) else 'enka'), None, ''
    if g == 'SPLIT_HANABI':
        return ('hanabi' if '花火' in (name or '') else 'fes'), None, ''
    return g, ex, ''

rows, mism, unknown, empty = [], [], [], []
for e in new:
    ps = e.get('_piaSub') or ''
    cat, _, sub = ps.partition('/')
    if not sub:
        cat, sub = '', ps
    name = e.get('name') or ''
    art = e.get('artist') or ''
    mine, myex, flag = my_genre(sub, name + ' ' + art)
    theirs = e.get('_genre')
    theirex = e.get('_extraGenres') or None
    rec = dict(id=e['id'], name=name, artist=art, sub=ps, theirs=theirs,
               theirex=theirex, mine=mine, myex=myex, flag=flag)
    rows.append(rec)
    if not ps.strip():
        empty.append(rec)
    elif flag == 'UNKNOWN_SUB':
        unknown.append(rec)
    elif mine != theirs or (myex or None) != (theirex or None):
        mism.append(rec)

out = []
w = out.append
w('=== 独立再導出 突き合わせ ===')
w(f'対象 {len(rows)}件 / 一致 {len(rows)-len(mism)-len(unknown)-len(empty)} / 不一致 {len(mism)} / 未知サブ {len(unknown)} / _piaSub空 {len(empty)}')
w('')
w('--- 不一致 ---')
for r in mism:
    w(f"id={r['id']} sub={r['sub']} _genre={r['theirs']}{r['theirex'] or ''} 判定={r['mine']}{r['myex'] or ''}")
    w(f"    name={r['name']}")
    w(f"    artist={r['artist']}")
w('')
w('--- 未知サブ ---')
for r in unknown:
    w(f"id={r['id']} sub={r['sub']} _genre={r['theirs']} name={r['name']}")
w('')
w('--- _piaSub空 ---')
for r in empty:
    w(f"id={r['id']} _genre={r['theirs']} name={r['name']} artist={r['artist']}")
w('')
w('--- 海外ROCK・POPS / 民族音楽 全件（K-POP判定用） ---')
for r in rows:
    if '海外ROCK' in r['sub'] or '民族音楽' in r['sub']:
        w(f"id={r['id']} sub={r['sub']} _genre={r['theirs']} name={r['name']} / artist={r['artist']}")
w('')
w('--- 演歌・邦楽 の分岐結果（dento/enka） ---')
for r in rows:
    if '演歌・邦楽' in r['sub']:
        w(f"id={r['id']} _genre={r['theirs']} 判定={r['mine']} name={r['name']}")
w('')
w('--- クラシック邦楽 全件 ---')
for r in rows:
    if 'クラシック邦楽' in r['sub']:
        w(f"id={r['id']} _genre={r['theirs']} 判定={r['mine']} name={r['name']}")
w('')
w('--- 音楽その他 / イベントその他 / 映画その他 / 演劇その他 全件 ---')
for r in rows:
    if 'その他' in r['sub']:
        w(f"id={r['id']} sub={r['sub']} _genre={r['theirs']} name={r['name']}")
open(r'C:\Users\user\oshinavi\tmp\qc_report.txt','w',encoding='utf-8').write('\n'.join(out))
json.dump(rows, open(r'C:\Users\user\oshinavi\tmp\qc_rows.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('written', len(out))
