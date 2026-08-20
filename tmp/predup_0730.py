# -*- coding: utf-8 -*-
"""投入前の重複チェック（[[feedback_harvest_dedup_check]]）。
① eventCd/eventBundleCd/楽天rtコード の一致（確実な重複）
② アーティスト名の NFKC 正規化での一致・部分一致（全角/半角差を吸収）
"""
import json
import re
import unicodedata

new = json.load(open('tmp/new50_0730.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))


def codes(e):
    s = json.dumps(e, ensure_ascii=False)
    out = set(re.findall(r'event(?:Bundle)?Cd=(\w+)', s))
    out |= set(re.findall(r'ticket\.rakuten\.co\.jp%2F(?:[a-z\-]+%2F)*(rt\w+)', s))
    out |= set(re.findall(r'ticket\.rakuten\.co\.jp/(?:[a-z\-]+/)*(rt\w+)', s))
    return out


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—]', '', s).lower()


old_codes = {}
for e in EVENTS:
    for c in codes(e):
        old_codes.setdefault(c, []).append(e)
old_names = {}
for e in EVENTS:
    old_names.setdefault(norm(e.get('artist')), []).append(e)

out = []
hit_cd = hit_nm = part = 0
for e in new:
    cs = codes(e)
    dup = [(c, x) for c in cs for x in old_codes.get(c, [])]
    if dup:
        hit_cd += 1
        out.append(f"🚨コード重複 new id={e['id']} {(e.get('artist') or '')[:40]}")
        for c, x in dup[:4]:
            out.append(f"      {c} ⇔ 既存 id={x['id']} {(x.get('artist') or '')[:40]}")
    n = norm(e.get('artist'))
    if n in old_names:
        hit_nm += 1
        out.append(f"🚨名前完全一致 new id={e['id']} {(e.get('artist') or '')[:40]}")
        for x in old_names[n][:4]:
            out.append(f"      ⇔ 既存 id={x['id']} {(x.get('artist') or '')[:40]} venue={x.get('venue')}")
    else:
        if len(n) >= 6:
            for on, xs in old_names.items():
                if len(on) >= 6 and (n in on or on in n):
                    part += 1
                    out.append(f"⚠️名前部分一致 new id={e['id']} {(e.get('artist') or '')[:40]}")
                    out.append(f"      ⇔ 既存 id={xs[0]['id']} {(xs[0].get('artist') or '')[:40]} venue={xs[0].get('venue')}")
                    break

out.append('')
out.append(f'=== コード重複 {hit_cd}件 / 名前完全一致 {hit_nm}件 / 名前部分一致 {part}件（新着{len(new)}件中） ===')
open('tmp/predup_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/predup_0730.txt  cd=%d name=%d part=%d' % (hit_cd, hit_nm, part))
