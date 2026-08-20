# -*- coding: utf-8 -*-
"""X投稿5本の投入前チェック。文字数は必ず機械カウント（[[project_sns_promotion]]）。
3点チェック＝冒頭ピックアップ／署名／ハッシュタグ。CTA文言固定。URL。「。」で改行。"""
import io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

raw = io.open('tmp/x_posts_0818.txt', encoding='utf-8').read()
blocks = re.split(r'^===\d+ (.+?)===$', raw, flags=re.M)
posts = []
for i in range(1, len(blocks), 2):
    posts.append((blocks[i].strip(), blocks[i + 1].strip()))

CTA = '▼チケット情報はこちら → https://oshinavi.jp'
SIGN = '推しの"発売日"見逃さない｜OSHINAVI'
HEAD = 'OSHINAVIの"明日発売"ピックアップ🎫'

print('=== %d本 ===' % len(posts))
ng = 0
for name, body in posts:
    n = len(body)
    checks = {
        '冒頭': body.startswith(HEAD),
        'CTA': CTA in body,
        '署名': SIGN in body,
        'タグ': bool(re.search(r'#\S+', body)),
        'URL': body.count('https://oshinavi.jp') == 1,
        '300字前後': 200 <= n <= 400,
    }
    # 「。」のあとに改行が無い箇所（文末を除く）
    bad_kuten = re.findall(r'。(?!\n|$)', body)
    checks['。で改行'] = not bad_kuten
    bad = [k for k, v in checks.items() if not v]
    ng += len(bad)
    print('  %-22s %3d字  %s' % (name, n, 'OK' if not bad else '❌ ' + '/'.join(bad)))
    if bad_kuten:
        for m in re.finditer(r'.{0,18}。(?!\n|$).{0,18}', body):
            print('        改行なし: %s' % m.group(0).replace('\n', '⏎'))

print()
print('=== 言い回しの重複（本文だけ・2本以上に出る2字以上の語）===')
STOP = set('明日発売券種一般公演東京神奈川時分日火水木金土'.split())
words = collections.defaultdict(set)
for name, body in posts:
    core = '\n'.join(l for l in body.split('\n')
                     if l and not l.startswith(('OSHINAVI', '▼', '推しの', '#')))
    for w in re.findall(r'[ぁ-んァ-ヶ一-龠]{3,}', core):
        words[w].add(name)
dup = {w: v for w, v in words.items() if len(v) >= 2}
for w, v in sorted(dup.items(), key=lambda x: -len(x[1]))[:12]:
    print('  %-10s %d本: %s' % (w, len(v), '／'.join(sorted(v))))
if not dup:
    print('  重複なし')

print()
print('判定:', 'OK（そのまま出せる）' if ng == 0 else '❌ %d件の不備' % ng)
