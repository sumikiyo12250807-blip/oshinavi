# -*- coding: utf-8 -*-
"""受付中スイープ(sg×rg分割)から、発売前で足りない分を穴埋めする候補を選ぶ。

受付中の一覧には**締切が載っていない**ので、
 - 公演が30日以上先のものを優先（締切まで余裕がある可能性が高い）
 - 同名の既存があるものは投入せず統合へ
 - build後に「締切が4日以内」のものを落とす（この段階では分からない）
"""
import json, io, sys, re, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today()
NEED = int(sys.argv[1]) if len(sys.argv) > 1 else 49

d = json.load(io.open('tmp/sw01_music.json', encoding='utf-8'))
rows = d['new']
print('受付中(音楽)の未掲載: %d件' % len(rows))

# すでに発売前で拾った分の eventCd は除く
already = set()
for p in ['tmp/pick_0825.json']:
    for it in json.load(io.open(p, encoding='utf-8')):
        already.add(it['_cd'])


def cd_of(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else u


def perf_date(it):
    m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', it.get('perfdate') or '')
    if not m:
        return None
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


seen = set()
cand = []
drop = collections.Counter()
for it in rows:
    cd = cd_of(it['url'])
    if cd in already or cd in seen:
        drop['重複'] += 1
        continue
    seen.add(cd)
    if it.get('name_in_db'):
        drop['同名の既存あり（統合へ）'] += 1
        continue
    pd = perf_date(it)
    if pd is None:
        drop['公演日が読めない'] += 1
        continue
    n = (pd - TODAY).days
    if n < 30:
        drop['公演まで30日未満'] += 1
        continue
    it['_cd'] = cd
    it['_pdays'] = n
    cand.append(it)

print('除外:', ', '.join('%s %d' % kv for kv in drop.items()))
print('残り候補: %d件' % len(cand))

# 公演が遠い順（＝締切にも余裕がある可能性が高い）
cand.sort(key=lambda x: -x['_pdays'])
pick = cand[:NEED]
print('\n=== 受付中からの穴埋め %d件 ===' % len(pick))
print('公演まで: 最短%d日 / 最長%d日' % (
    min(x['_pdays'] for x in pick), max(x['_pdays'] for x in pick)))
for x in pick[:10]:
    print('  %-42s %s %s' % (x['artist'][:40], x['perfdate'], x['pref']))
print('  …')

json.dump(pick, open('tmp/pick2_0825.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\nwritten tmp/pick2_0825.json')
