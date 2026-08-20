# -*- coding: utf-8 -*-
"""e+詳細ページを生HTMLで機械パース（reference_eplus_machine_parse の方式）。
公演日ドロップダウン＝全公演／block-ticket__header＝販売枠(受付期間・状態)。"""
import urllib.request, re, sys, html as _html
sys.stdout.reconfigure(encoding='utf-8')

DID = sys.argv[1] if len(sys.argv) > 1 else '0051510042'
URL = f'https://eplus.jp/sf/detail/{DID}'
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
print('URL', URL, '/ HTML長', len(h))

def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()

ttl = re.search(r'<title>(.*?)</title>', h, re.S)
print('title:', txt(ttl.group(1)) if ttl else '?')

print('\n=== 公演日option ===')
opts = re.findall(r'<option[^>]*value="[^"]*"[^>]*>(.*?)</option>', h, re.S)
for o in opts:
    t = txt(o)
    if t and t not in ('選択してください',):
        print('  ', t)

print('\n=== 販売枠 block-ticket__header ===')
blocks = re.split(r'(?=<header class="block-ticket__header")', h)
for b in blocks[1:]:
    head = txt(re.search(r'<header class="block-ticket__header".*?</header>', b, re.S).group(0)) if re.search(r'<header class="block-ticket__header".*?</header>', b, re.S) else ''
    period = re.search(r'受付期間[:：]\s*([^<]{4,60})', txt(b))
    stat = re.findall(r'ticket-status__item[^>]*>(.*?)<', b, re.S)
    print(f"  [{head[:60]}] 受付={period.group(1).strip() if period else '?'} 状態={[txt(s) for s in stat][:3]}")
