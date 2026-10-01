# -*- coding: utf-8 -*-
"""同じ日・同じ会場の二重登録／部・時間帯・回違いを畳む（ユーザー「他にもないか見て」10/1）
- dup_kind.json の same（名前まで同じ＝179組）は全部
- diff（名前が少し違う）は KEEP_SEPARATE に挙げた組（別の回の番号・別商品・別プラン）を除いて畳む
- 畳む先＝振り分け済みの最小id（全部新着なら最小id）。fold_parts.fold で枠を寄せ、同じ券種名×締切の枠は1つに（まとめページと公演ページの二重）
- ジャンルが違えば extraGenres に足す（迷ったら両方）
使い方: python tmp/x1001/dup_merge.py [--apply] → tmp/x1001/dup_merge.txt"""
import io, json, re, sys, datetime
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import fold_parts as FP
import heal_stale_deadlines as H
APPLY = '--apply' in sys.argv
root = 'C:/Users/user/oshinavi/'
TODAY = datetime.date.today().isoformat()
KEEP_SEPARATE = {15067, 15794, 23783, 25040, 25402, 25756, 25773, 25775, 25786, 25794, 26148, 26218, 26607}
dk = json.load(io.open(root + 'tmp/x1001/dup_kind.json'))
groups = dk['same'] + [g for g in dk['diff'] if not (set(g) & KEEP_SEPARATE)]
text = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(text, st)
by = {e['id']: e for e in E}
out = io.open(root + 'tmp/x1001/dup_merge.txt', 'w', encoding='utf-8')
gone, lost_total = set(), 0
for ids in groups:
    v = [by[i] for i in ids if i in by and i not in gone]
    if len(v) < 2:
        continue
    v.sort(key=lambda e: (e.get('genre') == 'new', e['id']))   # 振り分け済みを先頭に
    sk = lambda t: (FP.bare_type(re.sub(r'^【[^】]*】', '', t.get('type') or '')), t.get('url'))
    old_vis = {sk(t) for e in v for t in e.get('tickets') or [] if H.visible_slot(t, TODAY)}
    genres = []
    for e in v:
        for g in [e.get('_genre') if e.get('genre') == 'new' else e.get('genre')] + list(e.get('extraGenres') or e.get('_extraGenres') or []):
            if g and g != 'new' and g not in genres:
                genres.append(g)
    head = FP.fold(v)
    seen, tks = set(), []
    for t in head['tickets']:
        # 部の印は残して比べる（1部と2部を潰さない）・飛び先が違えば別の売り場＝畳まない（feedback_dedup_badges_keeps_urls）
        k = (t.get('type'), t.get('date'), bool(t.get('soldout')), t.get('url') or '')
        if k in seen:
            continue
        seen.add(k)
        tks.append(t)
    head['tickets'] = tks
    parts = head.get('_parts') or {}
    if len(set(parts.values())) > 1:   # 部が2つ以上ある組は全部の枠に部の印（A席が2枚並んでどっちの部か分からない、を防ぐ）
        for t in tks:
            lab = parts.get(t.get('url') or '')
            if lab and not (t.get('type') or '').startswith('【'):
                t['type'] = '【%s】%s' % (lab, t.get('type'))
    main = head.get('_genre') if head.get('genre') == 'new' else head.get('genre')
    extra = [g for g in genres if g != main]
    if extra:
        key = '_extraGenres' if head.get('genre') == 'new' else 'extraGenres'
        head[key] = list(dict.fromkeys(list(head.get(key) or []) + extra))
    head['date'] = max(e.get('date') or '' for e in v)
    new_vis = {sk(t) for t in head['tickets'] if H.visible_slot(t, TODAY)}
    lost = [k for k in old_vis if k not in new_vis and not any(k[0] == x[0] for x in new_vis)]
    lost_total += len(lost)
    for e in v[1:]:
        gone.add(e['id'])
    out.write(f"{head['id']} ← {[e['id'] for e in v[1:]]} | {head.get('name')[:50]} | {head.get('dateLabel')} | 枠{len(tks)}"
              + (f" | +{extra}" if extra else '') + (f' | 🚨消える枠{len(lost)}' if lost else '') + '\n')
out.write(f'\n畳む組 {len(groups)} / 欠番 {len(gone)} / 消える枠 {lost_total}\n')
if APPLY and lost_total == 0:
    E2 = [e for e in E if e['id'] not in gone]
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E2) + '\n]'
    text = text[:st] + body.replace('\n', '\r\n') + text[end:]
    mo = re.search(r'NEW_ORDER\s*=\s*\[([^\]]*)\]', text)
    ids2 = [x.strip() for x in mo.group(1).split(',') if x.strip() and int(x.strip()) not in gone]
    text = text[:mo.start(1)] + ','.join(ids2) + text[mo.end(1):]
    io.open(root + 'index.html', 'wb').write(text.encode('utf-8'))
    out.write('書いた\n')
elif APPLY:
    out.write('消える枠があるので書かない\n')
