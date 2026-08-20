import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
print("■ soldout枠のうち 枠ごとURL(t.url) を持つもの＝ぴあ以外が売り手の可能性")
for e in ev:
    for t in (e.get('tickets') or []):
        if t.get('soldout'):
            u = t.get('url') or '(枠URLなし→エントリのlinks)'
            lk = e.get('links') or {}
            print("  id%-5s %-9s | %-52s | 枠URL=%s | links: pia=%s eplus=%s" % (
                e['id'], '販売終了' if t.get('saleEnded') else '予定枚数終了',
                (t.get('type') or '')[:52], u[:64],
                'あり' if lk.get('pia') else 'なし', 'あり' if lk.get('eplus') else 'なし'))

# SSR / ai の 1149 行
ssr = h[h.index('<!-- AI_SSR_START -->'):h.index('<!-- AI_SSR_END -->')]
print("\n■ SSR の いぎなり東北産 行")
for m in re.finditer(r'<li>[^\n]*いぎなり東北産[^\n]*', ssr):
    print("  ", m.group(0)[:200])
print("\n■ SSR の 工藤静香 / 原田知世 / 宝塚星組 行")
for kw in ['工藤静香', '原田知世', 'RRR×TAKA']:
    for m in re.finditer(r'<li>[^\n]*' + re.escape(kw) + r'[^\n]*', ssr):
        print("  ", m.group(0)[:150])
print("\n■ SSR 集計: 予定枚数終了=%d / 販売終了=%d" % (ssr.count('⚫ 予定枚数終了'), ssr.count('⚪ 販売終了')))
