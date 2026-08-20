# -*- coding: utf-8 -*-
"""同名で当たった新着候補を「既存エントリへ枠を足す」形にするための cand を作る。
既存のぴあURL＋既存の枠URL＋新候補のURL を全部まとめて build し直す（union は merge 側でやる）。
出力: tmp/mergecand_0819.json（build_pia_entries 用）／tmp/mergedrop_0819.json（畳む相手のid）
"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(open('tmp/built_0819.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・\-–—~〜"\'`()（）【】\[\]!！?？。、,.:：/／★☆]', '', s).lower()


def urls_of(e):
    out = []
    u = (e.get('links') or {}).get('pia')
    if u:
        out.append(u)
    for t in (e.get('tickets') or []):
        if t.get('url') and 't.pia.jp' in t['url']:
            out.append(t['url'])
    return out


by_name = {}
for e in EVENTS:
    by_name.setdefault(norm(e.get('artist') or e.get('name')), []).append(e)

cand, drop, keep_ids, merged_new = [], {}, set(), set()
for b in built:
    same = by_name.get(norm(b.get('artist') or b.get('name'))) or []
    if not same:
        continue
    same = sorted(same, key=lambda e: e['id'])
    keep = same[0]
    others = [e['id'] for e in same[1:]]
    urls = []
    for e in same:
        urls += urls_of(e)
    urls += urls_of(b)
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u); uniq.append(u)
    cand.append({'newid': keep['id'], 'artist': keep.get('artist') or keep['name'], 'urls': uniq})
    if others:
        drop[keep['id']] = others
    keep_ids.add(keep['id'])
    merged_new.add(b['id'])
    print('%d %s ← 新%d ／ 畳む%s ／ URL %d本'
          % (keep['id'], (keep.get('artist') or '')[:24], b['id'], others or '無し', len(uniq)))

json.dump(cand, open('tmp/mergecand_0819.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({str(k): v for k, v in drop.items()}, open('tmp/mergedrop_0819.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(sorted(merged_new), open('tmp/merged_newids_0819.json', 'w', encoding='utf-8'))
print('=== 統合先 %d件 / 畳む既存 %d件 / 投入から外す新候補 %d件 ==='
      % (len(cand), sum(len(v) for v in drop.values()), len(merged_new)))
