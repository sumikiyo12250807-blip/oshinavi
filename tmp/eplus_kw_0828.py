# -*- coding: utf-8 -*-
"""e+ のキーワード検索（/sf/search?keyword=）で生きた枠があるか調べる。
削除の除外条件「他社に生き枠」を潰すため（feedback_delete_nonpia_blindspot）。"""
import sys, json, re, urllib.parse, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36'}
for kw in sys.argv[1:]:
    url = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
    try:
        req = urllib.request.Request(url, headers=UA)
        html = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
    except Exception as e:
        print('■ %s → 取得失敗 %s' % (kw, e)); continue
    names = re.findall(r'"eventName"\s*:\s*"([^"]{2,80})"', html)
    if not names:
        names = re.findall(r'"name"\s*:\s*"([^"]{2,80})"', html)
    seen, out = set(), []
    for n in names:
        if n in seen: continue
        seen.add(n); out.append(n)
    print('■ %s → %d件' % (kw, len(out)))
    for n in out[:12]:
        print('    -', n)
