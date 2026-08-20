# -*- coding: utf-8 -*-
"""ビルド2回分（本体25件＋429リトライ24件）を1本にまとめ、投入前の素性を確認する。"""
import io, sys, json, datetime, collections
sys.stdout.reconfigure(encoding='utf-8')

a = json.load(io.open('tmp/entries_0817e.json', encoding='utf-8'))
b = json.load(io.open('tmp/entries_0817e_retry.json', encoding='utf-8'))
cand = json.load(io.open('tmp/cand_0817e.json', encoding='utf-8'))
all_ids = {c['newid'] for c in cand}

ent = sorted(a + b, key=lambda e: e['id'])
got = {e['id'] for e in ent}
print('候補 %d件 / 組めた %d件 / まだ落ちている: %s' % (len(all_ids), len(ent), sorted(all_ids - got) or 'なし'))

dup = [k for k, v in collections.Counter(e['id'] for e in ent).items() if v > 1]
print('id重複:', dup or 'なし')

today = datetime.date(2026, 8, 17)


def d(s):
    return datetime.date(*[int(x) for x in s.split('-')]) if s else None


pre = onsale = 0
soon = []
for e in ent:
    ts = e.get('tickets') or []
    starts = [d(t.get('startDate')) for t in ts if t.get('startDate')]
    ends = [d(t.get('date')) for t in ts if t.get('date')]
    if [s for s in starts if s and s > today]:
        pre += 1
    else:
        onsale += 1
    # 発売前は全部残す。受付中で「もうじき終わる」ものだけ落とす（[[feedback_presale_first_harvest]]）
    if not [s for s in starts if s and s > today] and ends and max(ends) < today + datetime.timedelta(days=4):
        soon.append((e['id'], e.get('artist', '')[:30], max(ends).isoformat()))

print()
print('=== 投入予定の内訳 ===')
print('  発売前（これから売る） %d件 / もう売ってる %d件' % (pre, onsale))
print('  枠合計 %d本' % sum(len(e.get('tickets') or []) for e in ent))
print('  ジャンル下書き:', dict(collections.Counter(e.get('_genre', '(なし)') for e in ent)))
print()
if soon:
    print('⚠️ 受付中で4日以内に締切＝除外候補 %d件' % len(soon))
    for r in soon:
        print('   id%-5d %-30s 〜%s' % r)
else:
    print('✅ 受付中で4日以内に締切のものは無し（除外不要）')

json.dump(ent, io.open('tmp/entries_0817e_all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print()
print('→ tmp/entries_0817e_all.json（%d件）' % len(ent))
