# -*- coding: utf-8 -*-
"""楽天チケット：ジャンル一覧のリンク構造と、公演ページに販売期間が入っているかを調べる。"""
import sys, re, urllib.request, gzip, collections
sys.stdout.reconfigure(encoding='utf-8')

HDR = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept-Language': 'ja'}


def get(u):
    req = urllib.request.Request(u, headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        if 'gzip' in r.headers.get('Content-Encoding', ''):
            raw = gzip.decompress(raw)
        return raw.decode('utf-8', 'replace')


body = get('https://ticket.rakuten.co.jp/genre/music/')
hrefs = re.findall(r'href="([^"]+)"', body)
pat = collections.Counter()
for hh in hrefs:
    key = re.sub(r'[a-zA-Z0-9]{5,}', '<ID>', hh)
    pat[key] += 1
print('=== 音楽ジャンルページのリンクパターン ===')
for k, v in pat.most_common(25):
    print('  %3d  %s' % (v, k))

print('\n=== 公演リンクらしきもの（生） ===')
ev = [h for h in hrefs if '/event/' in h or re.match(r'^/[a-z0-9]{6,}/?$', h)]
for h in sorted(set(ev))[:20]:
    print('  ', h)

# トップから拾えた公演ページを1つ解析
u = 'https://ticket.rakuten.co.jp/event/rtvco5z/'
try:
    ev_body = get(u)
except Exception as ex:
    print('公演ページ取得エラー', ex)
    sys.exit(0)
print('\n=== 公演ページ %s / %d bytes ===' % (u, len(ev_body)))
t = re.search(r'<title[^>]*>(.*?)</title>', ev_body, re.S)
print('  title:', t.group(1).strip()[:100] if t else 'なし')
for kw in ('販売期間', '受付期間', '発売', '一般', '先行', '公演日', '会場', '完売', '受付終了'):
    print('  「%s」出現 %d回' % (kw, ev_body.count(kw)))
# 日付らしき文字列
ds = re.findall(r'20\d{2}[年/\.\-]\s?\d{1,2}[月/\.\-]\s?\d{1,2}', ev_body)
print('  日付らしき文字列 %d個:' % len(ds), ds[:12])
