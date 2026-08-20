# -*- coding: utf-8 -*-
"""投入前の最終チェック。50件そろったか／全角混入／バッジ形／発売前比率。
[[feedback_newpool_fullwidth_halfwidth]]（（）／〜は保護）／[[feedback_badge_date_full_form]]"""
import io, re, sys, json, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

ent = json.load(io.open('tmp/entries_0817e_all.json', encoding='utf-8'))
ent += json.load(io.open('tmp/entries_4505.json', encoding='utf-8'))
ent.sort(key=lambda e: e['id'])
cand = {c['newid'] for c in json.load(io.open('tmp/cand_0817e.json', encoding='utf-8'))}
got = {e['id'] for e in ent}
print('候補 %d / 組めた %d / 不足 %s / 余分 %s'
      % (len(cand), len(ent), sorted(cand - got) or 'なし', sorted(got - cand) or 'なし'))

# ①全角ローマ字・全角数字の混入（（）／〜～ は意味のある記号なので除外）
FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
hit = []
for e in ent:
    for k, v in e.items():
        if isinstance(v, str) and FW.search(v):
            hit.append((e['id'], k, v[:40]))
    for t in e.get('tickets') or []:
        for k, v in t.items():
            if isinstance(v, str) and FW.search(v):
                hit.append((e['id'], 'ticket.' + k, v[:40]))
print('\n=== 全角ローマ字/数字の混入 ===')
for r in hit[:20]:
    print('  id%-5d %-14s %s' % r)
print('  合計 %d件' % len(hit) if hit else '  なし ✅')

# ②バッジに公演日が完全なM/D形で入っているか
bad = []
for e in ent:
    for t in e.get('tickets') or []:
        ty = t.get('type', '')
        if '公演' not in ty:
            bad.append((e['id'], ty[:50]))
print('\n=== バッジに「公演」表記が無い枠 ===')
for r in bad[:20]:
    print('  id%-5d %s' % r)
print('  合計 %d件' % len(bad) if bad else '  なし ✅')

# ③発売前比率
today = datetime.date(2026, 8, 17)


def d(s):
    return datetime.date(*[int(x) for x in s.split('-')]) if s else None


pre = sum(1 for e in ent if [x for x in (d(t.get('startDate')) for t in e.get('tickets') or []) if x and x > today])
print('\n=== 投入内訳 ===')
print('  発売前 %d件 / もう売ってる %d件 / 枠合計 %d本'
      % (pre, len(ent) - pre, sum(len(e.get('tickets') or []) for e in ent)))
print('  ジャンル下書き:', dict(collections.Counter(e.get('_genre', '(なし)') for e in ent)))

json.dump(ent, io.open('tmp/entries_0817e_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n→ tmp/entries_0817e_final.json（%d件）' % len(ent))
sys.exit(1 if (hit or bad or len(ent) != len(cand)) else 0)
