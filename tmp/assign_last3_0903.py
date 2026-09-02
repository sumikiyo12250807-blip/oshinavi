# -*- coding: utf-8 -*-
"""9/2から保留していたe+の残り3件を振り分ける（学園祭ではないもの）。
根拠はすべて e+ の実ページ表記：
  6041 めろめろぱんちRound17 天体観測 … e+が「ライブ･コンサート／J-POP」と分類・出演メロメ → jpop
  6241 三越劇場プレミアムコンサート Vol.26 … 東京日本橋交響楽団/志村健一(指揮)/物集女純子(vn)
       特別ゲスト サーカス＝クラシック音楽・オーケストラ → classic
  6253 LOFT9 政則十番勝負2026 Part1 … 伊藤政則＋山本譲二/増子直純。e+の関連ジャンルは
       「イベント／トークショー･講演会／ストリーミング配信」＝OSHINAVIに該当タブが無い
       → musicetc（その他＝他で見つからない人が最後に開く砦。jpopの大箱に混ぜない）
🚨 今朝投入した新規64件は未チェックなので絶対に触らない。
"""
import re, json, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAP = {6041: 'jpop', 6241: 'classic', 6253: 'musicetc'}
PATH = 'index.html'

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = 0
for e in events:
    if e['id'] in MAP:
        assert e.get('genre') == 'new', 'id%d が genre:"new" でない' % e['id']
        e['genre'] = MAP[e['id']]
        for f in ('_genre', '_extraGenres', '_piaSub', '_srcgenre'):
            e.pop(f, None)
        hit += 1
        print('  id%d → %-9s %s' % (e['id'], MAP[e['id']], (e.get('name') or '')[:46]))

assert hit == len(MAP), '対象が %d件しか無い' % hit

m2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', src)
order = [i for i in json.loads(m2.group(2)) if i not in MAP]
remain = [e['id'] for e in events if e.get('genre') == 'new']
assert sorted(remain) == sorted(order), 'NEW_ORDER と genre:"new" が食い違う'

open('index.html.bak_0903_last3', 'w', encoding='utf-8', newline='').write(src)
dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start()] + m.group(1) + dumped + m.group(3) + src[m.end():]
out = out[:m2.start()] + m2.group(1) + json.dumps(order) + m2.group(3) + out[m2.end():]
open(PATH, 'w', encoding='utf-8', newline='').write(out)
print('=== 振り分け %d件 / 新着プール残り %d件（＝今朝投入した未チェック分）===' % (hit, len(remain)))
