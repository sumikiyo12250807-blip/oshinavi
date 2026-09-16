# -*- coding: utf-8 -*-
"""ぴあのまとめページの告知文にだけ出ている先行（pia.jp/v/ の専用申込ページ）を枠として足す（2026-09-11）。

build_pia_entries は券種の行しか読まないので、告知文の「■プレイガイド先行 受付期間：…」を拾えない。
新着の独立再導出で3件見つかったうち、**会場が1つで対象公演が決まる2件だけ**足す。
  ・id7749 星新一朗読劇（b2670908）＝■プレイガイド先行 9/9 12:00〜9/15 23:59
  ・id7729 百鬼夜鏡（b2670967）＝■ぴあ抽選先行 9/9 12:00〜9/13 23:59
  ⏸ id7711 UVERworld は対象公演が特定できないので足さない
使い方: python tmp/add_tokubetsu_0911.py [--apply]
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ADD = {
    7749: {"type": "プレイガイド先行（東京 9/30〜10/7公演）〜9/15 23:59", "date": "2026-09-15",
           "url": "https://pia.jp/v/hoshishinichi26p/"},
    7729: {"type": "ぴあ抽選先行（東京 11/3〜11/26公演）〜9/13 23:59", "date": "2026-09-13",
           "url": "https://pia.jp/v/hyakki26pia/"},
}
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
for e in events:
    t = ADD.get(e['id'])
    if not t:
        continue
    if any(x.get('type') == t['type'] for x in e.get('tickets') or []):
        print('id%s すでにある' % e['id']); continue
    # 画面の飛び先が壊れないよう、url 空の既存枠にカードのリンクを焼き込んでから足す
    for x in e.get('tickets') or []:
        if not x.get('url') and (e.get('links') or {}).get('pia'):
            x['url'] = e['links']['pia']
    e['tickets'].insert(0, dict(t))
    print('id%s %s ＋%s' % (e['id'], e['name'][:30], t['type']))
if '--apply' in sys.argv:
    open('index.html', 'w', encoding='utf-8').write(
        src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
    print('書き込み完了')
