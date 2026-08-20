# -*- coding: utf-8 -*-
"""振り分け前の検査。
 ①_piaSubが空/「音楽その他」＝名前fallback＝人の確認が要る（[[project_vendor_genre_autoassign]]）
 ②_piaSubの示すジャンルと_genre下書きが噛み合っていないもの
 ③プール内・既存DBとの同名重複（ツアー統合の要否＝[[feedback_tour_consolidate]]）
"""
import io, re, sys, json, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')

idx = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))
pool = [e for e in EV if e.get('genre') == 'new']
other = [e for e in EV if e.get('genre') != 'new']


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


# ぴあサブカテゴリ → 期待ジャンル（memory project_vendor_genre_autoassign の確定マッピング）
EXPECT = {
    '音楽/J-POP・ROCK': 'jpop', '音楽/ジャズ・フュージョン': 'jazz', '音楽/クラシック': 'classic',
    '音楽/海外ROCK・POPS': 'yougaku', '音楽/アニメ音楽': 'anime',
    '音楽/演歌・邦楽': 'enka|dento',
    'クラシック/器楽・室内楽': 'classic', 'クラシック/オーケストラ': 'classic',
    'クラシック/声楽・オペラ': 'classic', 'クラシック/バレエ・ダンス': 'classic',
    '演劇/演劇その他': 'engeki', '演劇/寄席・お笑い': 'owarai', '演劇/歌舞伎・古典芸能': 'dento',
    '演劇/朗読・リーディング': 'engeki', '演劇/ミュージカル・ショー': 'musical',
    '演劇/バレエ・ダンス': 'classic', '演劇/人形劇・キャラクター': 'kids',
    'イベント/博覧会・展示会・見本市': 'art', 'イベント/ショー・ファンイベント': 'fanevent',
}
NEEDS_HUMAN = {'', '音楽/音楽その他'}

print('=== ① 名前fallback＝人の確認が要る ===')
for e in pool:
    sub = e.get('_piaSub') or ''
    if sub in NEEDS_HUMAN:
        print('  %5d _genre=%-8s piaSub=%-12s %s | %s %s' % (
            e['id'], e.get('_genre', '-'), sub or '(空)', e.get('artist', '')[:34],
            e.get('venue', '')[:22], e.get('prefecture', '')))

print()
print('=== ② ぴあカテゴリと下書きが噛み合っていない ===')
for e in pool:
    sub = e.get('_piaSub') or ''
    if sub in NEEDS_HUMAN or sub not in EXPECT:
        if sub and sub not in EXPECT:
            print('  %5d ⚠️マップに無いサブカテゴリ piaSub=%-16s _genre=%-8s %s'
                  % (e['id'], sub, e.get('_genre', '-'), e.get('artist', '')[:32]))
        continue
    exp = EXPECT[sub]
    if e.get('_genre', '') not in exp.split('|'):
        print('  %5d ❌ piaSub=%-22s 期待=%-12s なのに下書き=%-8s  %s'
              % (e['id'], sub, exp, e.get('_genre', '-'), e.get('artist', '')[:30]))

print()
print('=== ③ 同名重複（ツアー統合の検討が要る） ===')
by = collections.defaultdict(list)
for e in pool:
    by[norm(e.get('artist', ''))].append(e)
ex_names = collections.defaultdict(list)
for e in other:
    ex_names[norm(e.get('artist', ''))].append(e)

for k, v in sorted(by.items()):
    hit_ex = ex_names.get(k, [])
    if len(v) > 1 or hit_ex:
        print('  「%s」' % v[0].get('artist', '')[:34])
        for e in v:
            print('     プール %5d  %s %s  枠%d' % (e['id'], e.get('prefecture', ''), e.get('date', ''), len(e.get('tickets') or [])))
        for e in hit_ex:
            print('     既存   %5d  %s %s  genre=%s 枠%d' % (e['id'], e.get('prefecture', ''), e.get('date', ''), e.get('genre'), len(e.get('tickets') or [])))
