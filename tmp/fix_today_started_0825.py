# -*- coding: utf-8 -*-
"""「〆切日に発売時刻がくっつく」型の残り3件を手で当てる。
ヒールの安全弁が止めたのは、3件とも**複数eventCdにまたがるツアー**で、
links.pia だけを引き直すと別eventCdの生きた枠が消えるから（安全弁は正しい）。
そこで**該当の1枠だけ**を、実ページ(pia_tickets)で確認した締切に書き換える。

実ページ確認（2026-08-25 12:59）:
  eventCd=2629318 モーニング娘。'26★2次受付〔北海道〕      受付中 〜 2026/9/2(水) 11:00
  eventCd=2619577 jo0ji〔北海道〕※ファミリーマートWEB抽選先行 受付中 〜 2026/9/7(月) 23:59
  eventCd=2628955 ◎【CANDY ROOM】会員限定◎矢野顕子先行受付  受付中 〜 2026/9/2(水) 23:59
"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

FIX = [
    (3422, '2次受付（北海道 10/25公演）8/25 11:00発売',
           '2次受付（北海道 10/25公演）〜9/2 11:00'),
    (4054, '先行（北海道 11/22公演）8/25 10:00発売',
           '先行（北海道 11/22公演）〜9/7 23:59'),
    (4103, '先行【CANDY ROOM】（岡山・広島 11/24〜11/26公演）8/25 12:00発売',
           '先行【CANDY ROOM】（岡山・広島 11/24〜11/26公演）〜9/2 23:59'),
]

path = 'index.html'
s = io.open(path, encoding='utf-8', newline='').read()

for eid, old, new in FIX:
    m = re.search(r'"id":\s*%d\s*,' % eid, s)
    assert m, eid
    i = s.rfind('{', 0, m.start())
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{': depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0: break
    b = s[i:j + 1]
    assert b.count('"type": "%s"' % old) == 1, 'id%d: 該当typeが見つからない' % eid
    b2 = b.replace('"type": "%s"' % old, '"type": "%s"' % new)

    # この枠の startDate（発売前の印）を落とす＝もう受付中なので
    tm = re.search(r'\{[^{}]*"type": "%s"[^{}]*\}' % re.escape(new), b2, re.S)
    assert tm, 'id%d: 枠ブロックが取れない' % eid
    blk = tm.group(0)
    blk2 = re.sub(r',\s*\r?\n\s*"startDate": "2026-08-25"', '', blk)
    b2 = b2[:tm.start()] + blk2 + b2[tm.end():]

    s = s[:i] + b2 + s[j + 1:]
    print('id%-5s %s' % (eid, new))

assert '\r\r\n' not in s
io.open(path, 'w', encoding='utf-8', newline='').write(s)
print('CRLF', s.count('\r\n'), 'bareLF', len(re.findall(r'(?<!\r)\n', s)))
