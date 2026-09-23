# -*- coding: utf-8 -*-
"""ZAIKOで MUSCLE BEACH TOKYO RETURNS 2026 と Verrückt／unchained の他の公演を探す（読むだけ）。
主催のページ（ageha.zaiko.io／cultureofasia.zaiko.io）と検索ページを引いて、イベントURLと名前を全部並べる。
使い方: python tmp/x0921/zaiko_newpool_probe.py
出力: tmp/x0921/zaiko_newpool_probe.txt
"""
import importlib.util
import io
import json
import os
import re
import sys
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')
spec = importlib.util.spec_from_file_location('zh', os.path.join(os.getcwd(), 'tools', 'zaiko_harvest.py'))
zh = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(zh)

PAGES = [
    'https://ageha.zaiko.io/ja',
    'https://ageha.zaiko.io/ja/events',
    'https://cultureofasia.zaiko.io/ja',
    'https://cultureofasia.zaiko.io/ja/events',
    'https://ageha.zaiko.io/ja/e/musclebeach26-musclebeach',
    'https://cultureofasia.zaiko.io/ja/e/verruckt-unchained',
]
for q in ['MUSCLE BEACH', 'musclebeach', 'Verrückt', 'Verruckt', 'unchained']:
    PAGES.append('https://zaiko.io/ja/search?q=' + urllib.parse.quote(q))
    PAGES.append('https://zaiko.io/ja/events/search?q=' + urllib.parse.quote(q))

o = io.open('tmp/x0921/zaiko_newpool_probe.txt', 'w', encoding='utf-8')
for u in PAGES:
    try:
        h = zh.fetch(u)
    except Exception as ex:
        o.write('## %s\n  取れない: %r\n' % (u, ex))
        continue
    if not h:
        o.write('## %s\n  空\n' % u)
        continue
    d = zh.page_data(h)
    comp = (d or {}).get('component')
    o.write('## %s  component=%s  len=%d\n' % (u, comp, len(h)))
    urls = sorted(set(re.findall(r'https?://[a-z0-9\-]+\.zaiko\.io/(?:ja/)?e/[A-Za-z0-9_\-%]+', h.replace('\\/', '/'))))
    for x in urls:
        o.write('  URL %s\n' % x)
    blob = json.dumps(d, ensure_ascii=False) if d else h
    for m in re.finditer(r'"(?:title|name)":\s*"([^"]{3,160})"', blob):
        t = m.group(1)
        if re.search(r'muscle|verr|unchained', t, re.I):
            o.write('  名前 %s\n' % t)
    if d:
        props = d.get('props') or {}
        o.write('  props keys=%s\n' % list(props.keys())[:30])
o.close()
print('ok')
