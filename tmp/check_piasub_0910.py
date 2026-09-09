# -*- coding: utf-8 -*-
"""疑わしい数件について、ぴあの実ページから <title> のカテゴリ表記と genreCd を読み直す。読み取り専用。"""
import re, sys, io, time, urllib.request, html as _html
sys.stdout = io.TextIOWrapper(open(sys.__stdout__.fileno(), 'wb', closefd=False), encoding='utf-8')

TARGETS = [
    ('7513', 'KIRARA', 'https://t.pia.jp/pia/event/event.do?eventCd=2634673'),
    ('7602', 'BOYNEXTDOOR', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669382'),
    ('7604', '八木山合奏団(海外ROCK扱い)', 'https://t.pia.jp/pia/event/event.do?eventCd=2634637'),
    ('7672', 'Garden Music Concert vol.2', 'https://t.pia.jp/pia/event/event.do?eventCd=2631307'),
]
CD = {'0100101': 'ジャズ・フュージョン', '0100102': 'J-POP・ROCK', '0100103': '演歌・邦楽',
      '0100104': '童謡・日本のうた', '0100105': 'アニメ音楽', '0100106': 'シャンソン',
      '0100108': '海外ROCK・POPS', '0100109': '民族音楽', '0100111': 'フェスティバル',
      '0100199': '音楽その他'}

for eid, name, url in TARGETS:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    except Exception as ex:
        print('id%s %s FETCH失敗 %s' % (eid, name, ex)); continue
    t = re.search(r'<title>([^<]*)</title>', h)
    title = _html.unescape(t.group(1)) if t else '(title無し)'
    g = re.search(r'genreCd"\s*value="(\d{7})"', h)
    gcd = g.group(1) if g else '(genreCd無し)'
    print('id%s %s' % (eid, name))
    print('   title = %s' % title.strip())
    print('   genreCd = %s → %s' % (gcd, CD.get(gcd, '?')))
    # 韓国っぽさの手掛かり（本文の国名表記）
    txt = re.sub(r'<[^>]+>', ' ', h)
    txt = _html.unescape(txt)
    for kw in ['韓国', 'K-POP', 'KPOP', 'ソウル', 'HYBE', 'KOZ']:
        if kw in txt:
            i = txt.index(kw)
            print('   [%s] …%s…' % (kw, re.sub(r'\s+', ' ', txt[max(0, i-60):i+60])))
    print()
    time.sleep(2)
