# -*- coding: utf-8 -*-
"""X投稿5本の機械検品。字数／「。」の直後の改行／CTA／署名／URL／曜日。"""
import re, io, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

posts = io.open('tmp/xposts_0825.txt', encoding='utf-8').read().split('\n---\n')
W = '月火水木金土日'
ok_all = True
for i, p in enumerate(posts, 1):
    p = p.strip('\n')
    n = len(p)
    issues = []
    if not (250 <= n <= 330):
        issues.append('字数 %d（250〜330の外）' % n)
    # 「。」の直後が改行か（末尾の。は除く）
    for m in re.finditer(r'。(?!$)', p):
        nxt = p[m.end():m.end() + 1]
        if nxt and nxt != '\n':
            issues.append('「。」の後が改行でない: …%s' % p[max(0, m.start() - 12):m.end() + 6].replace('\n', '⏎'))
    if '▼チケット情報はこちら' not in p:
        issues.append('CTAが無い')
    if '#OSHINAVI' not in p:
        issues.append('署名タグが無い')
    if not re.search(r'(?<!/)oshinavi\.jp', p):
        issues.append('oshinavi.jp が無い')
    if re.search(r'oshinavi\.jp[/?]', p):
        issues.append('URLに余計な文字が付いている')
    # 曜日の照合
    for m in re.finditer(r'(\d{1,2})/(\d{1,2})\((.)\)', p):
        mo, d, w = int(m.group(1)), int(m.group(2)), m.group(3)
        y = 2026 if mo >= 8 else 2027
        real = W[datetime.date(y, mo, d).weekday()]
        if real != w:
            issues.append('曜日ちがい %d/%d(%s)→正しくは(%s)' % (mo, d, w, real))
    print('【%d本目】%d文字  %s' % (i, n, 'OK' if not issues else '🚨'))
    for x in issues:
        print('    - %s' % x)
        ok_all = False
print('\n総合:', 'OK' if ok_all else '🚨要修正')
