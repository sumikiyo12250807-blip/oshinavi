# -*- coding: utf-8 -*-
"""新着47件のぴあURLを全件fetchして、死URL・別公演すり替わりを検出する。
（2026-07-16 神戸落語まつり=「ご確認ください」死URL の再発防止）
"""
import re, json, sys, time, urllib.request, html as _html, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = [e for e in json.loads(m.group(2)) if 2865 <= (e.get('id') or 0) <= 2914]
print('対象', len(E), '件\n')

UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def fetch(u):
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/（）()【】「」『』<>＜＞\'"”“!！?？~〜～.,、。:：#＃&＆-]', '', s).lower()

def title_of(doc):
    m = re.search(r'<title>(.*?)</title>', doc, re.S)
    t = _html.unescape(m.group(1)) if m else ''
    return re.sub(r'[|｜].*$', '', t).strip()

bad = 0
for e in E:
    urls = []
    p = (e.get('links') or {}).get('pia')
    if p:
        urls.append(p)
    for t in e.get('tickets', []):
        if t.get('url') and t['url'] not in urls:
            urls.append(t['url'])
    for u in urls:
        try:
            doc = fetch(u)
        except Exception as ex:
            print(f'❌FETCH id={e["id"]} {e.get("name")} | {u} | {ex}'); bad += 1
            continue
        ttl = title_of(doc)
        dead = ('ご確認ください' in doc and 'ticketSalesList' not in doc) or 'お探しのページ' in doc
        if dead:
            print(f'❌DEAD id={e["id"]} {e.get("name")} | {u} | title={ttl!r}'); bad += 1
            continue
        # タイトルと登録名の一致（どちらかがどちらかを含めばOK）
        a, b = norm(ttl), norm(e.get('name'))
        if a and b and not (b[:10] in a or a[:10] in b):
            print(f'⚠️名前不一致 id={e["id"]} 登録={e.get("name")!r}')
            print(f'      ぴあ={ttl!r}')
            print(f'      {u}')
            bad += 1
        time.sleep(0.4)

print(f'\n=== 指摘 {bad} 件 / 検証 {len(E)} エントリ ===')
