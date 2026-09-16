# -*- coding: utf-8 -*-
"""新着の下書き _genre を直す（2026-09-11）。
  id7805 JUNNY＝ぴあ「音楽/海外ROCK・POPS」×韓国のR&Bシンガー → kpop（[[feedback_kpop_vs_yougaku]]）
    裏取り: https://kstyle.com/article.ksn?articleNo=2282117 ／ https://korepo.com/archives/1700712
使い方: python tmp/set_draft_genre_0911.py [--apply]
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
FIX = {7805: 'kpop'}
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
for e in events:
    if e['id'] in FIX and e.get('genre') == 'new':
        print('id%s %s: _genre %s → %s' % (e['id'], e['name'], e.get('_genre'), FIX[e['id']]))
        e['_genre'] = FIX[e['id']]
if '--apply' in sys.argv:
    open('index.html', 'w', encoding='utf-8').write(
        src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
    print('書き込み完了')
