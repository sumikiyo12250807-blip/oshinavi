# -*- coding: utf-8 -*-
"""玉置浩二の一般発売を主催者/公式から探す（文字コードを明示して読む）"""
import io, re, html as H, urllib.request

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/120 Safari/537.36'}

TARGETS = [
    ('キョードー西日本', 'https://www.kyodo-west.co.jp/artist_page.php?a_id=5'),
    ('公式ニュース一覧', 'https://saltmoderate.com/news'),
    ('公式ローチケ先行告知', 'https://saltmoderate.com/news/detail/20684'),
]

def get(url):
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30).read()
    enc = None
    m = re.search(rb'charset=["\']?([\w\-]+)', raw[:4000], re.I)
    if m:
        enc = m.group(1).decode('ascii', 'ignore')
    for e in ([enc] if enc else []) + ['utf-8', 'cp932', 'euc_jp']:
        try:
            return raw.decode(e)
        except Exception:
            continue
    return raw.decode('utf-8', 'replace')

out = []
for name, url in TARGETS:
    out.append('==================== %s' % name)
    out.append(url)
    try:
        h = get(url)
    except Exception as ex:
        out.append('  ❌ %s' % str(ex)[:120])
        continue
    txt = H.unescape(re.sub(r'<[^>]+>', ' ', h))
    txt = re.sub(r'[ \t]+', ' ', txt)
    # 玉置の周辺だけ抜く
    hits = [m.start() for m in re.finditer(r'玉置浩二', txt)]
    out.append('  玉置浩二 出現 %d回 / len=%d' % (len(hits), len(h)))
    for s in hits[:6]:
        seg = re.sub(r'\s+', ' ', txt[max(0, s - 200): s + 1400]).strip()
        out.append('  --- %s' % seg)
    # 発売・受付の記述だけ拾う
    for m in re.finditer(r'[^。\n]{0,80}(一般発売|一般販売|発売中|受付中|先行受付|発売日)[^。\n]{0,120}', txt):
        seg = re.sub(r'\s+', ' ', m.group(0)).strip()
        if seg:
            out.append('  [売] %s' % seg)
    out.append('')

io.open('tmp/out_tamaki_promoter.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_tamaki_promoter.txt')
