# -*- coding: utf-8 -*-
"""新着プール(genre:new)と既存エントリの【緩い】重複チェック。
完全一致の同名チェックをすり抜ける型を拾う：
  ・「劇団四季「オペラ座の怪人」1月／名古屋」 と 同 ＋「ぴあスペシャルシートS1席」＝同じ公演の別売り場
  ・演者名が会名の中に埋まっている（柳家三三 → 「紀尾井らくご 柳家三三独演会」）
判定は「片方の正規化名がもう片方に含まれる（4文字以上）」＋「同じ会場・同じ公演日帯」。
機械では決めきれないので、候補を出して人が見る用。
"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EVENTS if e.get('genre') == 'new']
old = [e for e in EVENTS if e.get('genre') != 'new']


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・\-–—~〜"\'`()（）【】「」『』\[\]!！?？。、,.:：/／★☆]', '', s).lower()


hits = 0
for n in sorted(new, key=lambda x: x['id']):
    kn = norm(n['name'])
    ka = norm(n.get('artist') or '')
    cand = []
    for o in old:
        ko = norm(o['name'])
        koa = norm(o.get('artist') or '')
        pair = False
        for a, b in ((kn, ko), (ka, koa), (ka, ko), (kn, koa)):
            if len(a) >= 4 and len(b) >= 4 and (a in b or b in a):
                pair = True
                break
        if pair:
            cand.append(o)
    if cand:
        hits += 1
        print('■ new %d %s' % (n['id'], n['name'][:52]))
        print('     会場 %s / 千秋楽 %s' % ((n.get('venue') or '')[:28], n.get('date')))
        for o in cand[:6]:
            print('   ← 既存 %d %s' % (o['id'], o['name'][:52]))
            print('        会場 %s / 千秋楽 %s / genre %s' % ((o.get('venue') or '')[:28], o.get('date'), o.get('genre')))
print('=== 新着 %d件中 %d件に「似た既存」あり ===' % (len(new), hits))
