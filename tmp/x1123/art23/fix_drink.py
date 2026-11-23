# -*- coding: utf-8 -*-
# 記事の頼み書き・禁止語から「ドリンク」を外す（11/23 すちこ「ドリンク代は書いて」）＝写す元の 11/23 の3枚と、確かめの頼み書き
import io, re
D = 'C:/Users/user/oshinavi/tmp/x1123/art23/'
o = io.open(D + 'fix_drink.txt', 'w', encoding='utf-8')
for f in ('brief.md', 'check.py', 'fc_brief.md'):
    s = io.open(D + f, encoding='utf-8').read()
    n = s
    n = n.replace('・顔写真・ドリンク代）', '・顔写真）\n- 書く：ドリンク代（入場時に別に払う「別途ドリンク代◯円」も、料金に入っている「1ドリンク付き」も。11/23 すちこ「ドリンク代を入場の時に払うシステムは結構あるから書いて」）')
    n = n.replace('|撮影|録音|ドリンク', '|撮影|録音')
    n = n.replace('・会員登録・ドリンクなど）', '・会員登録など）／ドリンク代は書く側（抜けていたら🟠）')
    o.write('%s 変えた=%s ドリンクの禁止の残り=%s\n' % (f, n != s, bool(re.search(r'\|ドリンク|ドリンク代）|ドリンクなど', n))))
    io.open(D + f, 'w', encoding='utf-8').write(n)
