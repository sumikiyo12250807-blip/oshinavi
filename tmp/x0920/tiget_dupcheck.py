# -*- coding: utf-8 -*-
"""TIGETの「二重登録疑い186件」を、ネットを叩かずに仕分ける（読むだけ・2026-09-20）。

🚨判定の軸は名前ではなく**飛び先URL**（[[feedback_harvest_name_dedup_blindspot]]／[[feedback_dedup_badges_keeps_urls]]）。
対象＝組み上がり3,589件のうち、**TIGETのイベントidがまだ1つも登録されていない**もの（＝昨夜の⚠️186件）。
仕分け:
  A) 既存に「名前＋公演日」が一致するものがある → 同じ公演の別の回/別券種の疑い＝**足し込み候補**
  B) 名前だけ一致（公演日が違う） → 別の日の公演＝**新規候補**
  C) どちらも無い → **新規候補**
出力: tmp/x0920/tiget_dup.md ／ tmp/x0920/tiget_dup_new.txt（新規候補のTIGET URL）
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/x0919/built_tiget_rest.json', encoding='utf-8'))['entries']
h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))


def urls_of(e):
    out = set()
    for v in (e.get('links') or {}).values():
        if v:
            out.add(str(v))
    for t in (e.get('tickets') or []):
        if t.get('url'):
            out.add(t['url'])
    return out


def evids(e):
    return {mm.group(1) for u in urls_of(e)
            for mm in [re.search(r'tiget\.net/events/(\d+)', u)] if mm}


reg_evid = set()
for e in events:
    reg_evid |= evids(e)

by_nd, by_n = {}, {}
for e in events:
    n = (e.get('artist') or e.get('name') or '').strip()
    by_nd.setdefault((n, e.get('date')), []).append(e)
    by_n.setdefault(n, []).append(e)

todo = [b for b in built if evids(b) and not (evids(b) & reg_evid)]
rows = {'足し込み候補（名前＋公演日が一致）': [], '新規候補（同名だが公演日が違う）': [],
        '新規候補（同名も無い）': []}
for b in todo:
    n = (b.get('artist') or b.get('name') or '').strip()
    u = sorted(urls_of(b))
    u = u[0] if u else ''
    if by_nd.get((n, b.get('date'))):
        rows['足し込み候補（名前＋公演日が一致）'].append(
            (n, b.get('date'), b.get('dateLabel'), u, [e['id'] for e in by_nd[(n, b.get('date'))]]))
    elif by_n.get(n):
        rows['新規候補（同名だが公演日が違う）'].append(
            (n, b.get('date'), b.get('dateLabel'), u, [e['id'] for e in by_n[n]][:6]))
    else:
        rows['新規候補（同名も無い）'].append((n, b.get('date'), b.get('dateLabel'), u, []))

with io.open('tmp/x0920/tiget_dup.md', 'w', encoding='utf-8') as f:
    f.write('# TIGET「二重登録疑い」%d件の仕分け（2026-09-20・ネットは叩いていない）\n\n' % len(todo))
    f.write('判定はTIGETのイベントURL（=売り場）で。名前が同じでもURLが違えば別の売り場＝畳まない。\n')
    for k, v in rows.items():
        f.write('\n## %s … %d件\n\n' % (k, len(v)))
        for n, d, dl, u, ids in v[:70]:
            f.write('- %s（公演 %s／%s）%s\n  - %s\n'
                    % (n[:46], d, (dl or '')[:46], ('既存 id%s' % ids) if ids else '', u))
        if len(v) > 70:
            f.write('  … ほか %d件\n' % (len(v) - 70))
io.open('tmp/x0920/tiget_dup_new.txt', 'w', encoding='utf-8').write(
    '\n'.join(u for k in ('新規候補（同名だが公演日が違う）', '新規候補（同名も無い）')
              for _, _, _, u, _ in rows[k]))
print('対象 %d件' % len(todo), {k: len(v) for k, v in rows.items()})
