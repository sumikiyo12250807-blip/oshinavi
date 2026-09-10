# -*- coding: utf-8 -*-
"""tools/x_check.py が見ない「ユーザーに直された癖」を機械で見る（2026-09-11分）。

出どころ＝memory feedback_x_user_edited_samples（ユーザーが実物を直した差分）。
  ・「ぶん」→「チケット」
  ・「動くわ」→「明日発売よ」
  ・「売り場が開く」→「買えるわよ」
  ・封印フレーズ／二人称／件数の実数
そのうえで、この日だけの事情も見る＝春風亭昇太の重複行が2つ出ていないか。

  python tmp/x_extra_check_0911.py tmp/x0911/post*.txt
"""
import glob
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

NG_WORD = [
    ('ぶん', '「ぶん」は使わない→「チケット」と名指しする'),
    ('動くわ', '「動くわ」は使わない→「明日発売よ」'),
    ('動きます', '「動く」は使わない→「発売」'),
    ('売り場が開', '運営目線→「まだチケットが買えるわよ」'),
    ('枠が開', '運営目線→「買える」'),
    ('あんた', '二人称「あんた」は禁止'),
    ('生で浴び', '封印フレーズ'),
    ('みなさん', '呼びかけは使わない'),
    ('皆さん', '呼びかけは使わない'),
    ('押さえる', '「押さえる」は使わない＝転売の入口'),
    ('両方おさえ', '「両方おさえる」は勧めない'),
    ('さっきの', '1本ずつ単独で読まれる＝他の投稿を指さない'),
    ('前の投稿', '1本ずつ単独で読まれる＝他の投稿を指さない'),
]
NG_RE = [
    # 台本＝10未満はそのままの数でよい。2桁以上の実数だけを見る
    (re.compile(r'(?<!他にも)\d{2,}\s*件(?!以上)(発売|が発売|の発売)'),
     '件数の実数を書かない（「他にも◯件以上」だけが例外）'),
    (re.compile(r'https?://\s*oshinavi'), 'URLに https:// を付けない'),
    # リスト行（先頭が HH:MM）は公演名に「／」が入るので対象外
    (re.compile(r'^(?!\d{1,2}:\d{2} )[^\n]*[／/][^\n]*[／/][^\n]*$', re.M),
     '「A／B／C」の羅列になっている行がある（1行1公演にする）'),
]
NEED = [
    ('▼チケット情報はこちら', 'CTAが無い'),
    ('oshinavi.jp', 'oshinavi.jp が無い'),
    ('#OSHINAVI', 'タグ #OSHINAVI が無い'),
    ('#明日発売', 'タグ #明日発売 が無い'),
    ('#チケット', 'タグ #チケット が無い'),
]
HEAD = re.compile(r'^OSHINAVIの"9/11チケット発売"ピックアップ🎫$')

files = []
for a in sys.argv[1:]:
    files.extend(sorted(glob.glob(a)))
if not files:
    print('ファイルを指定して')
    sys.exit(1)

tails = {}
bad_total = 0
for f in files:
    t = io.open(f, encoding='utf-8').read().rstrip('\n')
    lines = t.split('\n')
    ng = []
    if not HEAD.match(lines[0].strip()):
        ng.append('1行目が見出しでない: %r' % lines[0][:44])
    for w, why in NG_WORD:
        if w in t:
            ng.append('%s（%s）' % (w, why))
    for rx, why in NG_RE:
        m = rx.search(t)
        if m:
            ng.append('%s → %r' % (why, m.group(0)[:60]))
    for w, why in NEED:
        if w not in t:
            ng.append(why)
    # 「。」の直後が改行か（「モーニング娘。」は除く）
    for m in re.finditer(r'。(?!\n|$)', t):
        around = t[max(0, m.start() - 6):m.start() + 2]
        if 'モーニング娘。' in around:
            continue
        ng.append('「。」の直後が改行でない: %r' % t[max(0, m.start() - 12):m.start() + 8])
        break
    # 春風亭昇太の重複（この日だけの事情）
    if t.count('春風亭昇太') >= 2 and 'かめあり亭' in t:
        ng.append('春風亭昇太の12/10が2行になっている疑い（同じ公演なので1行にまとめる）')
    n = len(t.replace('\n', ''))
    # 締めは**タグ行の1つ前**（最終行はいつも #OSHINAVI…）
    body = [x for x in lines if x.strip() and not x.strip().startswith('#')]
    tails[f] = body[-1] if body else ''
    print('■ %s … %d字 %s' % (f, n, 'OK' if not ng else '🚨%d件' % len(ng)))
    for x in ng:
        print('    - %s' % x)
    bad_total += len(ng)

# 締めが全部違うか
print('')
print('--- 締めの1行（全部違うこと） ---')
seen = {}
for f, ln in tails.items():
    if ln in seen:
        print('🚨 %s と %s の締めが同じ: %r' % (seen[ln], f, ln[:40]))
        bad_total += 1
    seen[ln] = f
    print('  %s: %r' % (f, ln[:50]))

print('')
print('=== 指摘 %d件 ===' % bad_total)
