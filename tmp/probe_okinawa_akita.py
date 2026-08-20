# -*- coding: utf-8 -*-
"""沖縄(RBC)・秋田(AKT)の販売ページから「販売期間/締切」の記述を探す。
締切が明記されていなければ推測しない（feedback_unknown_end_date）。"""
import urllib.request, re, sys, html as _html
sys.stdout.reconfigure(encoding='utf-8')

def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def txt(h):
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S)
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', h)))

for name, u in [('沖縄RBC', 'https://www.rbc.co.jp/event/event_information/mn2026col/'),
                ('秋田AKT', 'https://www.akt.co.jp/events/doc2026')]:
    print(f'\n========== {name} {u}')
    t = txt(get(u))
    # チケット・発売まわりの文を抜く
    for kw in ('発売', 'チケット', '販売', 'ローソン', 'プレイガイド', 'Lコード', '取扱'):
        for m in re.finditer(kw, t):
            s = max(0, m.start() - 60)
            frag = t[s:m.start() + 90].strip()
            print(f'  … {frag}')
            break  # 各キーワード最初の1件だけ
