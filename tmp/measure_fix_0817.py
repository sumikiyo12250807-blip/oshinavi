# -*- coding: utf-8 -*-
"""presale_harvest の未掲載判定を「名前」→「eventCd」に直した効果を、
ぴあを叩き直さずに保存済みJSONだけで測る。"""
import io, re, sys, json, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')

idx = io.open('index.html', encoding='utf-8').read()


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


ex_names = {norm(m.group(1)) for m in re.finditer(r'"(?:artist|name)"\s*:\s*"([^"]+)"', idx)}
ex_cds = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', idx))

old = json.load(io.open('tmp/presale_music03_0817.json', encoding='utf-8'))
fixed = json.load(io.open('tmp/presale_music03_0817_FIXED.json', encoding='utf-8'))

print('=== 発売前・音楽 rlsIn=03（同じ在庫517件・パース393件を、判定だけ変えて比較）===')
print('  旧（名前の部分一致で除外）: 未掲載 %3d件' % len(old['new']))
print('  新（eventCd がDBに無い） : 未掲載 %3d件' % len(fixed['new']))
print('  → 毎日 %d件を取りこぼしていた' % (len(fixed['new']) - len(old['new'])))

strict = [it for it in fixed['new'] if norm(it['artist']) in ex_names]
print()
print('  新着150件のうち「同名の既存エントリあり」＝完全一致だけで数えると %d件' % len(strict))
print('   （＝投入時に既存エントリへ ticket を足す形で統合するか判断が要る分）')
for it in strict[:15]:
    print('    ⚠️ %-26s 発売 %-10s %s' % (it['artist'][:26], it['rlsdate'] or '(不明/本日)', it['pref']))

print()
print('=== 新しく拾えるようになった分の「発売までの日数」内訳 ===')
import datetime
TODAY = datetime.date(2026, 8, 17)


def days(r):
    if not r or r == 'TODAY':
        return None
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', r)
    return (datetime.date(*[int(x) for x in m.groups()]) - TODAY).days if m else None


c = collections.Counter()
for it in fixed['new']:
    d = days(it.get('rlsdate'))
    c['発売日不明/本日' if d is None else ('4日後以降' if d >= 4 else ('2〜3日後' if d >= 2 else ('明日' if d == 1 else '本日')))] += 1
for k in ['4日後以降', '2〜3日後', '明日', '本日', '発売日不明/本日']:
    if c[k]:
        print('  %-10s %3d件' % (k, c[k]))
