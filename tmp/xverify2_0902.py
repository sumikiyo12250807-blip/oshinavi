# -*- coding: utf-8 -*-
"""9/4・9/5に出した5件が、こちらが渡した素材（箱の大きい5件）と一致しているかを見る。
＋残り件数の丸めが実数と矛盾していないか（多めに言っていないか）を数える。"""
import io, os, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIEF = io.open(os.path.join(ROOT, 'tmp', 'x_brief_0902.md'), encoding='utf-8').read()
POSTS = {b: io.open(os.path.join(ROOT, 'tmp', 'x0902', 'post%d.txt' % i), encoding='utf-8').read()
         for i, b in ((2, '音楽'), (3, 'クラシック'), (4, 'エンタメ'), (5, 'おでかけ'))}


def norm(s):
    return re.sub(r'[\s　]+', '', unicodedata.normalize('NFKC', s or '')).lower()


cur_b = cur_day = None
want = {}
rest = {}
for ln in BRIEF.split('\n'):
    m = re.match(r'## まとめ枠：(.+)', ln)
    if m:
        cur_b = m.group(1).strip(); continue
    m = re.match(r'### (9/\d)\(.\)発売（全(\d+)組のうち、箱の大きい5件だけ出す。残り(\d+)組', ln)
    if m and cur_b:
        cur_day = m.group(1)
        rest[(cur_b, cur_day)] = int(m.group(3))
        want[(cur_b, cur_day)] = []
        continue
    if re.match(r'### 明日', ln):
        cur_day = None
        continue
    m = re.match(r'^(\d{1,2}:\d{2}) (.+?)／', ln)
    if m and cur_b and cur_day:
        want[(cur_b, cur_day)].append(m.group(2))

ng = 0
for (b, day), names in sorted(want.items()):
    body = norm(POSTS[b])
    miss = [n for n in names if norm(n.split('／')[0]) not in body]
    print('%-6s %s … 渡した5件のうち載っている %d/%d  残り%d組'
          % (b, day, len(names) - len(miss), len(names), rest[(b, day)]))
    for n in miss:
        print('    🚨載っていない: %s' % n)
    ng += len(miss)

print('\n--- 丸めの検算（本文の「他にも◯件」 vs 実際の残り）')
for b, body in POSTS.items():
    days = [(m.group(1), int(m.group(2))) for m in
            re.finditer(r'(9/\d)\(.\)発売', body)]
    for m in re.finditer(r'他にも(\d+)件(近く|以上)?', body):
        print('  %-6s 本文「他にも%s件%s」' % (b, m.group(1), m.group(2) or ''))
    for m in re.finditer(r'他にも(\d+)件', body):
        pass
for (b, day), r in sorted(rest.items()):
    print('  %-6s %s の実際の残り = %d組' % (b, day, r))
print('\n=== 素材とのズレ %d ===' % ng)
