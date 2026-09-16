# -*- coding: utf-8 -*-
"""振り分けてよい新着の id を機械で決める（読むだけ・2026-09-16 朝）。出力＝tmp/assign_ok_ids_0916.txt
条件（全部そろった id だけ）:
  ① 読み直しの結果がある・note（読めなかった）が無い
  ② 読み直しの受付中・発売前が1枠以上ある（買える枠0は振り分けず残す）
  ③ ジャンル以外のズレが無い（tmp/recheck_flags_0916.py と同じ読み方）。ただし「終わった公演の県」だけのズレは通す＝PAST_PREF_OK
  ④ ジャンルが独立に確かめられた＝ページのジャンル番号が _piaSub の分類名と一致（compare_genre_0916 か genre_from_html_0916 の方法）
     または 大分類が一致して、行き先が大分類そのもの（クラシック→classic・スポーツ→sports）
  ⑤ HOLD に入っていない
使い方: python tmp/assign_ok_build_0916.py
"""
import glob
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')
from build_pia_entries import PIA_GENRE_CD  # noqa: E402

SP = r'C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\166bfbc5-2524-465f-aba5-b0b622c14861\scratchpad'
HOLD = {
    8378, 8379, 8380, 8381, 8382, 8384, 8432, 10762,  # ぴあ以外＝ユーザーの確認後
    8765, 8790,  # 応援グッズの県＝ユーザーに聞いている
    9382,        # ピクサー展 9/16入場分がぴあで受付中（登録は締切切れ）＝枠を当ててから
    8351,        # Chevon＝9/15 から保留（公演の続きの扱い）
}
HOLD |= {7558, 8172}  # 前からの保留＝Tommy february6（照合STALE）・瑛人×SANIMYOK（ぴあの区分とアーティストが食い違う）
PAST_PREF_OK = {9007, 9516}  # 県のズレは終わった公演（山梨7/4・広島7/23）だけ＝いま買える枠とは関係ない
# 「枠 登録N／実M」は、エージェントが公演日ごとのカードを数えただけ＝「券種名＋締切」の組で数え直して一致（tmp/recheck_windows_0916.py）
# 10474・10475・10479 は組の数が合わなくても登録が正しいことを1件ずつ確かめた（同じ名前の一般発売が2つの映画館で別売り・先行3＋一般3）
PAST_PREF_OK |= {10443, 10444, 10446, 10447, 10448, 10453, 10454, 10455, 10456, 10457, 10458, 10459, 10460, 10470,
                 10472, 10474, 10475, 10479, 10498, 10536, 10624, 10628, 10638, 10647, 10661, 10717}

src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
pool = {e['id']: e for e in ev if e.get('genre') == 'new'}
rows = {}
for p in glob.glob(os.path.join(SP, 'recheck_*_result.json')):
    for r in json.load(io.open(p, encoding='utf-8')):
        rows[r['id']] = r
files = {}
CANON = re.compile(r'(?:canonical|og:url)[^>]*?event(?:Bundle)?Cd=(b?\d+)|event(?:Bundle)?Cd=(b?\d+)[^>]*?(?:canonical|og:url)')
for p in glob.glob(os.path.join(SP, '**', '*.htm*'), recursive=True):
    if p.endswith('.url'):
        continue
    base = os.path.basename(p).split('.')[0]
    m = re.fullmatch(r'(?:B_|eventBundleCd_|E_|eventCd_)?(b?\d{7})', base)
    if m:
        files.setdefault(m.group(1), p)
        continue
    # 名前が番号でない保存（r3_cache のハッシュ名など）＝ページ自身の canonical / og:url から番号を取る
    try:
        head = io.open(p, encoding='utf-8', errors='replace').read(20000)
    except OSError:
        continue
    c = CANON.search(head)
    if c:
        files.setdefault(c.group(1) or c.group(2), p)

PAST_PREF_OK |= {10719, 10723, 10745}  # S席/A席の2枠＝ぴあの券種番号2つ・宮城は終わった公演・カードを数えただけ
# 8544・8573・9946＝読み直しの結果どおりに直した（commit cf68ab08）＝いまは登録と実ページが一致
# 10264・9892・10274・10397・8404＝いま買える枠は登録と一致（ズレは終わった公演・別番号の延期／取扱なし・同じ範囲の枠のカード分け）
PAST_PREF_OK |= {8544, 8573, 9946, 10264, 9892, 10274, 10397, 8404}
PAST_PREF_OK |= {10718}  # 当日引換券（9/16 0:00発売）＝朝のヒールで「〜9/23 14:00」に＝実ページの受付中と一致


def soft_note(r):
    """1本目・4本目のエージェントは公演ページの券種カードは読めたが、その先の券種ごとの詳細ページ（ticketInformation.do）を読めなかった。
    カードに状態と締切は出ている＝全部の枠に状態が付いていれば、突き合わせには使える（詳細ページの読めなさは通す）。"""
    note = r.get('note') or ''
    slots = r.get('slots') or []
    return (note.startswith('券種ページを読めなかった') or note.startswith('詳細ページが読めなかった')) \
        and slots and all(s.get('state') for s in slots)


md = io.open('tmp/compare_recheck_0916.md', encoding='utf-8').read()
flagged = set()
for i, body in re.findall(r'- \*\*id(\d+) .*?\*\*.*?\n((?:  - .*\n)*)', md):
    real = [ln for ln in body.splitlines() if ln.startswith('  - ') and not ln.startswith('  - ジャンル')
            and not ln.startswith('  - note: 券種ページを読めなかった') and not ln.startswith('  - note: 詳細ページが読めなかった')]
    if real and int(i) not in PAST_PREF_OK:
        flagged.add(int(i))


def n(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or ''))


GC = re.compile(r'(?:genreCd|ntSgenreCd)["\']?\s*(?:value=|[:=])\s*["\']?(\d{7})')
BROAD = {'クラシック': 'classic', 'スポーツ': 'sports'}


# 保存ページが無かった15件は、ぴあのページのジャンル番号を引き直して _piaSub と一致を確かめた（tmp/genre_fetch_0916.py → tmp/genre_fetch_0916.txt）
GENRE_FETCHED = {9891, 9897, 9910, 9938, 9939, 9963, 9979, 9980, 9988, 9992, 10009, 10024, 10027, 10035, 10058}


def genre_ok(e, r):
    if e['id'] in GENRE_FETCHED:
        return '番号（引き直し）'
    top, _, leaf = (e.get('_piaSub') or '').partition('/')
    leaf = n(leaf)
    g = r.get('pia_genre') or ''
    got = {n(PIA_GENRE_CD.get(c, '')) for c in re.findall(r'ntSgenreCd[:：]\s*(\d{7})', g)}
    cls = re.search(r'分類[:：]\s*([^／/]+?)\s*(?:／|$)', g)
    if cls:
        got.add(n(cls.group(1)))
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]:
        m = re.search(r'event(?:Bundle)?Cd=(b?\d+)', u or '')
        if m and m.group(1) in files:
            h = io.open(files[m.group(1)], encoding='utf-8', errors='replace').read()
            got |= {n(PIA_GENRE_CD.get(c, '')) for c in GC.findall(h)}
    if leaf and leaf in got:
        return '番号'
    if BROAD.get(top) and e.get('_genre') == BROAD[top] and top in g:
        return '大分類'
    return ''


ok, why = [], {}
for i, e in sorted(pool.items()):
    r = rows.get(i)
    if i in HOLD:
        why[i] = '保留'
    elif not r or (r.get('note') and not soft_note(r)):
        why[i] = '読めていない'
    elif not [s for s in r.get('slots') or [] if s.get('state') in ('受付中', '発売前')]:
        why[i] = '買える枠0'
    elif i in flagged:
        why[i] = 'ズレあり'
    elif not genre_ok(e, r):
        why[i] = 'ジャンル未確認'
    else:
        ok.append(i)
io.open('tmp/assign_ok_ids_0916.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in ok) + '\n')
from collections import Counter  # noqa: E402
print('新着 %d件 → 振り分けてよい %d件 → tmp/assign_ok_ids_0916.txt' % (len(pool), len(ok)))
print('残す: ' + ' / '.join('%s %d' % kv for kv in Counter(why.values()).most_common()))
for k in ('買える枠0', 'ズレあり', 'ジャンル未確認'):
    ids = [i for i, w in why.items() if w == k]
    if ids:
        print('  %s: %s' % (k, ','.join(str(i) for i in ids[:60])))
