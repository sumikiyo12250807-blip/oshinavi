# -*- coding: utf-8 -*-
"""ぴあの詳細検索フォーム search_dtl_input.do から、rlsInfo.do に渡せる
絞り込みパラメータ名（エリア・サブジャンル等）を洗い出す。
1000件頭打ちを「どの軸で割れるか」を決めるための下調べ。"""
import re, sys, http.client, html
sys.stdout.reconfigure(encoding='utf-8')

conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
conn.request('GET', '/pia/search_dtl_input.do',
             headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
r = conn.getresponse()
body = r.read().decode('utf-8', 'replace')
print('status', r.status, 'bytes', len(body))

names = {}
for m in re.finditer(r'<(input|select)\b[^>]*>', body):
    tag = m.group(0)
    nm = re.search(r'name="([^"]+)"', tag)
    if not nm:
        continue
    val = re.search(r'value="([^"]*)"', tag)
    names.setdefault(nm.group(1), []).append(val.group(1) if val else '(select)')

for k, v in names.items():
    print('%-16s %d個  例=%s' % (k, len(v), ','.join(v[:8])))

print()
print('=== select の中身（option value / ラベル）===')
for m in re.finditer(r'<select\b[^>]*name="([^"]+)"[^>]*>(.*?)</select>', body, re.S):
    nm = m.group(1)
    opts = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', m.group(2), re.S)
    opts = [(a, html.unescape(re.sub(r'<[^>]+>', '', b)).strip()) for a, b in opts]
    print('--- %s (%d) ---' % (nm, len(opts)))
    for a, b in opts[:60]:
        print('   %-8s %s' % (a, b))
