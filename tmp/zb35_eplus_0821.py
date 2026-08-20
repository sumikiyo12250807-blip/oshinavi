# -*- coding: utf-8 -*-
"""zb35（買える枠0エントリ35件）をe+のキーワード検索で総ざらいする。"""
import re, sys, io, time, urllib.request, urllib.parse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ITEMS = [
 ("1554","高嶋ちさ子"),
 ("1601","藍井エイル"),
 ("2748","熊本地震10年復興コンサート"),
 ("3473","AA="),
 ("3509","田辺花火大会"),
 ("3696","Stray Kids"),
 ("4035","紫 今"),
 ("4036","Little Parade"),
 ("4050","Bray me"),
 ("4051","K-Drama OST Tribute Concert"),
 ("4057","Faulieu."),
 ("4066","新サクラ大戦 the Stage"),
 ("4080","THE SOUND OF GUNDAM"),
 ("4081","梅田サイファー"),
 ("4083","汐れいら"),
 ("4089","花宮初奈"),
 ("4094","KAWAII LAB."),
 ("4098","高木いくの"),
 ("4100","Khalid"),
 ("4106","徹子の部屋"),
 ("4114","Yung Kai"),
 ("4115","THE MACKSHOW"),
 ("4117","RAINCOVER"),
 ("4150","FIVE O ONE"),
 ("4156","IRIS MONDO"),
 ("4159","わーすた"),
 ("4163","中本こまり"),
 ("4165","TAKERU"),
 ("4167","Ken Yokoyama"),
 ("4172","Bocchi"),
 ("4175","THE PREDATORS"),
 ("4422","yeti let you notice"),
 ("4423","The Performance Zero"),
 ("4424","シャッポ"),
 ("4425","スミワタルトリオ"),
]

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return urllib.request.urlopen(req, timeout=60).read().decode('utf-8','replace')

def search(kw):
    u = 'https://eplus.jp/sf/search?keyword=' + urllib.parse.quote(kw)
    h = fetch(u)
    rows, seen = [], set()
    for m in re.finditer(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h):
        blk = h[max(0,m.start()-4000):min(len(h),m.end()+4000)]
        def g(k):
            mm = re.search(r'"%s":"([^"]*)"' % k, blk)
            return mm.group(1).replace('\xa0',' ') if mm else ''
        url = 'https://eplus.jp' + m.group(1)
        if url in seen: continue
        seen.add(url)
        rows.append({
            'url': url,
            'kogyo': g('kogyo_name_1'), 'sub': g('kogyo_name_2'),
            'koenbi': g('koenbi_term') or g('koenbi_hyoji_mongon'),
            'venue': g('venue_name'),
            'pref': g('todofuken_name'),
            'status': g('uketsuke_name_pc'),
            'ustart': g('uketsuke_start_datetime'),
            'uend': g('uketsuke_end_datetime'),
        })
    rows.sort(key=lambda x: x['koenbi'])
    return len(h), rows

for eid, kw in ITEMS:
    print('='*70)
    print('### id=%s kw=%s' % (eid, kw))
    try:
        ln, rows = search(kw)
        print('htmllen=%d hits=%d' % (ln, len(rows)))
        rows=[o for o in rows if (o['uend'] or '99999999') >= '20260821']
        print('  live(受付終了>=今日) %d件' % len(rows))
        for o in rows:
            print('  %s | %s / %s | %s(%s) | %s | 受付 %s〜%s | %s' % (
                o['koenbi'][:24], o['kogyo'][:28], o['sub'][:30], o['venue'][:20], o['pref'][:5],
                o['status'][:14], o['ustart'][:12], o['uend'][:12], o['url']))
    except Exception as e:
        print('ERR %r' % (e,))
    time.sleep(1.2)
