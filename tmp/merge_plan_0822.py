# -*- coding: utf-8 -*-
"""同名の既存エントリがある候補（ツアー分裂の疑い）を、既存エントリへの統合計画に変換する。

🚨これは [[feedback_pia_bundle_hides_shows]] / [[feedback_harvest_name_dedup_blindspot]] の型。
ぴあのツアーまとめページに出てこない公演があり、アーティスト名で引くと出てくる。
2026-08-18 に「登録2枠→実は5枠」（来生たかお）が見つかっている。
"""
import io, re, json, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・:：\-−ー~〜/／]', '', s).lower()


cand = json.load(io.open('tmp/samename_night_0821.json', encoding='utf-8'))
h = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

# 既存エントリを正規化名で引けるようにする
idx = collections.defaultdict(list)
for e in EV:
    for key in (e.get('artist'), e.get('name')):
        if key:
            idx[norm(key)].append(e)

plans, unmatched = {}, []
for c in cand:
    hits = idx.get(norm(c['artist'])) or []
    # artist と name の両方でインデックスに入れているので、同じエントリが二重に入る。id で潰す。
    seen_id, uniq = set(), []
    for e in hits:
        if e['id'] not in seen_id:
            seen_id.add(e['id'])
            uniq.append(e)
    hits = uniq
    if not hits:
        unmatched.append(c)
        continue
    # 同名が複数あるときは公演日が近いものに寄せず、全部を候補として出す（人が見る）
    if len(hits) > 1:
        unmatched.append(dict(c, _reason='同名の既存が%d件あって寄せ先を決められない: %s' % (
            len(hits), ','.join(str(x['id']) for x in hits))))
        continue
    e = hits[0]
    p = plans.setdefault(e['id'], {
        'id': e['id'], 'artist': e.get('artist'), 'name': e.get('name'),
        'date': e.get('date'), 'tickets': len(e.get('tickets') or []),
        'urls': [], 'cand': []})
    exist_urls = {(e.get('links') or {}).get('pia')}
    exist_urls |= {t.get('url') for t in (e.get('tickets') or [])}
    exist_urls = {u for u in exist_urls if u}
    # ぴあの2つのホスト表記を揃えて比較する
    def key(u):
        return re.sub(r'^https?://[^/]+', '', u or '').replace('/pia/event/event.do', '/pia/event.do')
    have = {key(u) for u in exist_urls}
    if key(c['url']) not in have:
        p['cand'].append(c)
    p['urls'] = sorted(exist_urls | {c['url']})

plans = {k: v for k, v in plans.items() if v['cand']}
io.open('tmp/merge_plan_0822.json', 'w', encoding='utf-8').write(
    json.dumps(list(plans.values()), ensure_ascii=False, indent=1))
io.open('tmp/merge_unmatched_0822.json', 'w', encoding='utf-8').write(
    json.dumps(unmatched, ensure_ascii=False, indent=1))

L = []
for p in sorted(plans.values(), key=lambda x: -len(x['cand'])):
    L.append('id=%-5d 枠%-3d %s  ← 未登録の公演 %d件' % (p['id'], p['tickets'], p['artist'], len(p['cand'])))
    for c in p['cand']:
        L.append('        %s %s %s  %s' % (c['rlsdate'] or '(発売日不明)', c['perfdate'], c['pref'], c['url']))
io.open('tmp/merge_plan_0821.txt', 'w', encoding='utf-8').write('\n'.join(L))
print('統合先エントリ %d件 / 追加候補 %d件 / 寄せ先を決められなかった %d件'
      % (len(plans), sum(len(p['cand']) for p in plans.values()), len(unmatched)))
