# -*- coding: utf-8 -*-
"""rlsIn の値ごとに何件返るかを実測する（読むだけ・データは触らない）。"""
import re, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        final = r.geturl(); body = r.read().decode('utf-8','replace')
    if 'sorry.pia' in final:
        return None, 'SORRY'
    return body, final

def total_of(h):
    # 「全◯件」「◯件中」などの総件数表記を拾う（複数パターン）
    for pat in [r'(\d[\d,]*)\s*件中', r'全\s*(\d[\d,]*)\s*件', r'検索結果[^\d]{0,10}(\d[\d,]*)\s*件']:
        m = re.search(pat, h)
        if m: return int(m.group(1).replace(',','')), pat
    return None, None

def pages_of(h):
    ps = [int(x) for x in re.findall(r'page=(\d+)', h)]
    return max(ps) if ps else None

LG='01'
for rls in ['01','02','03','04','05','06','']:
    f = ('rlsIn=%s&' % rls) if rls else ''
    url = 'https://t.pia.jp/pia/rlsInfo.do?lg=%s&%spage=1' % (LG, f)
    h, final = get(url)
    if h is None:
        print('rlsIn=%-3s SORRY(混雑)' % (rls or 'なし')); time.sleep(5); continue
    t,pat = total_of(h)
    mp = pages_of(h)
    nrows = len(re.findall(r'eventCd=(\d+)', h))
    print('rlsIn=%-3s 総件数=%s  最大page=%s  1ページ内eventCdリンク=%d' % (rls or 'なし', t, mp, nrows))
    time.sleep(3)
