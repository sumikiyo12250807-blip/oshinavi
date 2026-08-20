# -*- coding: utf-8 -*-
"""玉置浩二: e+ワード検索で別公演/別券種が出ていないか（削除か育成かの裏取り）"""
import io, re, sys, urllib.parse, html as H
sys.path.insert(0, 'tools')
from eplus_harvest import fetch

W = urllib.parse.quote('玉置浩二')
URLS = [
    'https://eplus.jp/sf/word/%s' % W,
    'https://eplus.jp/sf/detail/0011860001',
]

out = []
for u in URLS:
    out.append('=== %s' % u)
    try:
        h = fetch(u)
    except Exception as ex:
        out.append('  ❌FETCH %s' % str(ex)[:150])
        continue
    out.append('  HTML長 %d' % len(h))
    # 公演リンク（/sf/detail/xxxx）を全部拾う
    ids = sorted(set(re.findall(r'/sf/detail/([0-9A-Za-z\-]+)', h)))
    out.append('  detailリンク %d件: %s' % (len(ids), ', '.join(ids[:40])))
    # 玉置を含む見出しテキスト
    txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(h)))
    for m in re.finditer(r'玉置浩二', txt):
        s = max(0, m.start() - 120)
        out.append('    …%s…' % txt[s:m.end() + 220])
    out.append('')

io.open('tmp/out_tamaki.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_tamaki.txt')
