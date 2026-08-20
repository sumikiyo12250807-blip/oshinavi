# -*- coding: utf-8 -*-
"""e+ /sf/detail/ ページから「どの公演か」（興行名・会場・公演日）と販売枠を機械抽出する。
検索JSONの会場対応がずれるので、個別ページのタイトル/JSON-LDで同定し直す用。"""
import re, sys, json, html, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')

def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s or ''))).strip()

for u in sys.argv[1:]:
    url = u if u.startswith('http') else 'https://eplus.jp/sf/detail/' + u
    try:
        h = get(url)
    except Exception as e:
        print("%s ERROR %s" % (u, e)); continue
    title = clean((re.search(r'<title>(.*?)</title>', h, re.S) or [None, ''])[1])
    # JSON-LD があれば公演日/会場を取る
    dates, places = [], []
    for m in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try:
            data = json.loads(m)
        except Exception:
            continue
        for d in (data if isinstance(data, list) else [data]):
            if not isinstance(d, dict):
                continue
            if d.get('startDate'):
                dates.append(d['startDate'])
            loc = d.get('location')
            if isinstance(loc, dict) and loc.get('name'):
                places.append(loc['name'])
    print("=" * 66)
    print(u)
    print("  title  :", title[:110])
    print("  公演日 :", ", ".join(sorted(set(dates))[:6]) or "(JSON-LD無し)")
    print("  会場   :", ", ".join(sorted(set(places))[:4]) or "-")
    for b in re.findall(r'(先着|抽選)\s*([^<]{0,40}?)受付期間:([^<]{10,60})', clean(h)):
        print("  枠     :", b[0], b[1].strip(), "受付", b[2].strip())
    st = set(re.findall(r'(受付中|受付終了|予定枚数終了|受付前|販売終了)', clean(h)))
    print("  状態   :", ", ".join(sorted(st)))
