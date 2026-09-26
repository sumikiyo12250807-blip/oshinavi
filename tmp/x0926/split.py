# -*- coding: utf-8 -*-
"""tmp/x0926/presale_<lg>_<st>.json を index.html の EVENTS と eventCd で突き合わせて仕分ける（読むだけ）。
(a) eventCd が登録に無い＝新規候補  (b) eventCd は登録にあるが窓（券種名＋発売日）が無い＝足し込み候補
出力: tmp/x0926/presale_split.json / pia_cands.json（build入力・新規） / pia_merge_in.json（build入力・足し込み）"""
import io, json, re, sys, unicodedata, glob, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-26'
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
MAXID = max(e['id'] for e in ev)
cd2e = {}
for e in ev:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', u):
            cd2e.setdefault(c, [])
            if e not in cd2e[c]:
                cd2e[c].append(e)


def nz(s):
    return unicodedata.normalize('NFKC', s or '').replace(' ', '')


def iso(d):
    if d == 'TODAY':
        return TODAY
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', d or '')
    return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))) if m else ''


def cd_of(u):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
    return m.group(1) if m else None


def pref_short(p):
    p = p or ''
    return p if p == '北海道' else re.sub(r'[都府県]$', '', p)


stats, new_by_cd, merge_by_key, present = {}, {}, {}, 0
unsure = []
for lg in ['01', '02', '03', '04', '05', '06', '07']:
    st = stats.setdefault(lg, {'rows': 0, 'new_cd': set(), 'merge': 0, 'present': 0, 'files': []})
    for sfx in ('0102', '0202'):
        fn = 'tmp/x0926/presale_%s_%s.json' % (lg, sfx)
        try:
            d = json.load(open(fn, encoding='utf-8'))
        except Exception as ex:
            st['files'].append('%s 読めず(%s)' % (sfx, ex)); continue
        st['files'].append('%s total=%s pages=%s/%s rows=%d' % (sfx, d.get('total'), d.get('fetched_pages'), d.get('pages'), len(d.get('rows') or [])))
        perf = {r['url'] + '|' + (r.get('saletype') or '') + '|' + (r.get('rlsdate') or ''): r.get('perfdate') for r in d.get('new') or []}
        seen = set()
        rows = list(d.get('rows') or [])
        # new にだけあって rows に無い行も拾う（念のため）
        rk = {(r['url'], r.get('saletype'), r.get('rlsdate')) for r in rows}
        rows += [r for r in d.get('new') or [] if (r['url'], r.get('saletype'), r.get('rlsdate')) not in rk]
        for r in rows:
            k = (r['url'], r.get('saletype'), r.get('rlsdate'), r.get('venue'))
            if k in seen:
                continue
            seen.add(k)
            st['rows'] += 1
            cd = cd_of(r['url'])
            r = dict(r, lg=lg, kind=sfx, rls_iso=iso(r.get('rlsdate')),
                     perfdate=r.get('perfdate') or perf.get(r['url'] + '|' + (r.get('saletype') or '') + '|' + (r.get('rlsdate') or '')))
            es = cd2e.get(cd) if cd else None
            if not es:
                g = new_by_cd.setdefault(cd or r['url'], {'cd': cd, 'url': r['url'], 'artist': r['artist'], 'lg': lg, 'rows': []})
                g['rows'].append(r)
                st['new_cd'].add(cd or r['url'])
                continue
            # 一覧の saletype は「一般発売/先行抽選」の分類だけで券種名そのものではない（一般販売・プレリザーブ・
            # 限定企画チケット等に化ける）ので、窓は「発売日＋県」で見る。会場別URL/まとめURLのずれがあるので券は全枚見る。
            pss = [pref_short(x) for x in re.split(r'[／/・]', r.get('pref') or '') if x]
            hit = False
            for e in es:
                for t in e.get('tickets') or []:
                    ty = t.get('type') or ''
                    if pss and not any(p in ty for p in pss):
                        continue
                    if t.get('startDate') == r['rls_iso']:
                        hit = True
                    elif r['rls_iso'] and r['rls_iso'] <= TODAY and not t.get('startDate') and (t.get('date') or '') >= TODAY:
                        hit = True   # 本日発売で既に発売中の形に直っている枠
                    if hit:
                        break
                if hit:
                    break
            if hit:
                st['present'] += 1; present += 1
                continue
            e = es[0]
            key = (e['id'], cd)
            m = merge_by_key.setdefault(key, {'id': e['id'], 'artist': e.get('artist'), 'eventCd': cd,
                                              'url': r['url'], 'other_ids': [x['id'] for x in es[1:]], 'missing': []})
            m['missing'].append({'saletype': r.get('saletype'), 'rlsdate': r['rls_iso'], 'venue': r.get('venue'),
                                 'pref': r.get('pref'), 'lg': lg, 'kind': sfx})
            st['merge'] += 1

# 出力
newid = MAXID + 1
cands, split_new = [], []
for k, g in new_by_cd.items():
    url = g['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')
    cands.append({'newid': newid, 'artist': g['artist'], 'urls': [url], 'lg': g['lg'], 'eventCd': g['cd'],
                  'windows': sorted({(r.get('saletype'), r['rls_iso'], r['kind']) for r in g['rows']})})
    newid += 1
merge_in = []
for (eid, cd), m in merge_by_key.items():
    url = m['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')
    merge_in.append({'newid': newid, 'artist': m['artist'] or '', 'urls': [url], 'target': eid, 'eventCd': cd})
    newid += 1
json.dump(cands, io.open('tmp/x0926/pia_cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(merge_in, io.open('tmp/x0926/pia_merge_in.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(list(merge_by_key.values()), io.open('tmp/x0926/pia_merge_cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'new': [r for g in new_by_cd.values() for r in g['rows']],
           'merge': list(merge_by_key.values())}, io.open('tmp/x0926/presale_split.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ジャンル | 見た行 | 登録済みの窓あり | 新規候補(公演=eventCd) | 足し込み候補(行)')
for lg, st in stats.items():
    print(' %s | %d | %d | %d | %d   %s' % (lg, st['rows'], st['present'], len(st['new_cd']), st['merge'], ' / '.join(st['files'])))
print('新規候補 %d公演 / 足し込み %d件（既存id×eventCd）/ 窓あり %d行' % (len(cands), len(merge_in), present))
