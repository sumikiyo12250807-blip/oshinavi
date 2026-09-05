# -*- coding: utf-8 -*-
"""ぴあ個別ページを生HTMLで取得し、公演名/公演日/会場/販売枠テキストを抜く。"""
import urllib.request, re, io, sys, time
import html as H
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
      'Accept-Language': 'ja,en;q=0.8'}

URLS = [
 (583,  'https://t.pia.jp/pia/event/event.do?eventCd=2622462'),
 (6944, 'https://t.pia.jp/pia/event/event.do?eventCd=2630866'),
 (6295, 'https://t.pia.jp/pia/event/event.do?eventCd=2630058'),
 (6080, 'https://t.pia.jp/pia/event/event.do?eventCd=2631878'),
 (6103, 'https://t.pia.jp/pia/event/event.do?eventCd=2628807'),
]

def flat(x):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', H.unescape(x))).strip()

lines = []
for eid, u in URLS:
    lines.append('##### id=%s %s' % (eid, u))
    h = None
    err = ''
    for i in range(5):
        try:
            h = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read().decode('utf-8', 'replace')
            break
        except Exception as e:
            err = str(e)
            time.sleep(3 + 3 * i)
    if h is None:
        lines.append('  !! 取得失敗: %s' % err)
        lines.append('')
        continue
    io.open(r'C:\Users\user\oshinavi\tmp\vfy_html_0905\pia_%s.html' % eid, 'w', encoding='utf-8').write(h)
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    lines.append('  title: %s' % (flat(t.group(1)) if t else ''))
    md = re.search(r'<meta name="description" content="([^"]*)"', h)
    lines.append('  meta: %s' % (H.unescape(md.group(1))[:400] if md else ''))
    # 公演情報（日付・会場）
    for m in re.finditer(r'class="[^"]*event-title[^"]*"[^>]*>(.*?)</', h, re.S):
        lines.append('  event-title: %s' % flat(m.group(1))[:200])
    # 販売枠テーブル/リスト
    for cls in ('release', 'ticket-status', 'rls', 'sales'):
        for m in re.finditer(r'<(?:li|tr|div)[^>]*class="[^"]*%s[^"]*"[^>]*>(.*?)</(?:li|tr|div)>' % cls, h, re.S):
            s = flat(m.group(1))
            if s and ('20' in s or '受付' in s or '発売' in s):
                lines.append('  [%s] %s' % (cls, s[:230]))
    # 生テキストから日付らしい行
    body = flat(h)
    for m in re.finditer(r'(20\d\d/\d{1,2}/\d{1,2}[^ ]{0,20}\s*[~〜～]?\s*(?:20\d\d/\d{1,2}/\d{1,2}[^ ]{0,20})?)', body):
        pass
    lines.append('  --- 本文抜粋 ---')
    lines.append('  ' + body[:1800])
    lines.append('')
    time.sleep(1.5)

io.open(r'C:\Users\user\oshinavi\tmp\vfy_pia_0905.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('ok')
