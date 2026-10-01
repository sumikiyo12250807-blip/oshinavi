import os
os.chdir('C:/Users/user/oshinavi')
# -*- coding: utf-8 -*-
"""tmp/x1001/eve/pia_presale_<lg>_<st>.json を index.html の EVENTS と eventCd で突き合わせて仕分ける（読むだけ）。
（tmp/x0927/split.py の写し。日付とフォルダだけ変えた＋新規候補に「県＋公演日で登録済みらしい」の印を足した）
(a) eventCd が登録に無い＝新規候補  (b) eventCd は登録にあるが窓（発売日＋県）が無い＝足し込み候補
出力: tmp/x1001/eve/presale_split.json / pia_cands.json（build入力・新規） / pia_merge_in.json（build入力・足し込み）"""
import io, json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-10-01'
src = open('index.html', encoding='utf-8').read()
_i = src.index('const EVENTS = [') + len('const EVENTS = ')
ev, _ = json.JSONDecoder().raw_decode(src[_i:])
MAXID = max(e['id'] for e in ev)
cd2e = {}
for e in ev:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', u):
            cd2e.setdefault(c, [])
            if e not in cd2e[c]:
                cd2e[c].append(e)


def nz(s):
    return unicodedata.normalize('NFKC', s or '').replace(' ', '').replace('　', '').lower()


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
for lg in ['01', '02', '03', '04', '05', '06', '07']:
    st = stats.setdefault(lg, {'rows': 0, 'new_cd': set(), 'merge': 0, 'present': 0, 'files': []})
    for sfx in ('0102', '0202'):
        fn = 'tmp/x1001/eve/presale_%s_%s.json' % (lg, sfx)
        try:
            d = json.load(open(fn, encoding='utf-8'))
        except Exception as ex:
            st['files'].append('%s 読めず(%s)' % (sfx, ex)); continue
        st['files'].append('%s total=%s pages=%s/%s rows=%d' % (sfx, d.get('total'), d.get('fetched_pages'), d.get('pages'), len(d.get('rows') or [])))
        perf = {r['url'] + '|' + (r.get('saletype') or '') + '|' + (r.get('rlsdate') or ''): r.get('perfdate') for r in d.get('new') or []}
        seen = set()
        rows = list(d.get('rows') or [])
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
                        hit = True
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
                                 'pref': r.get('pref'), 'perfdate': r.get('perfdate'), 'lg': lg, 'kind': sfx})
            st['merge'] += 1


# 新規候補に「県＋公演日で登録済みらしい」の印（番号違いの同じ窓＝feedback_existing_entries_miss_new_windows 9/16）
def md_of(pd):
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', pd or '')
    return ('%d/%d' % (int(m.group(2)), int(m.group(3)))) if m else ''


def maybe_dup(g):
    hits = []
    an = nz(g['artist'])[:6]
    for r in g['rows']:
        md = md_of(r.get('perfdate'))
        pss = [pref_short(x) for x in re.split(r'[／/・]', r.get('pref') or '') if x]
        if not md:
            continue
        pat = re.compile(r'（(%s)[^）]*(?<![\d/])%s(?!\d)[^）]*公演' % ('|'.join(map(re.escape, pss)) or '.', re.escape(md)))
        for e in ev:
            if an and an not in nz((e.get('artist') or '') + (e.get('name') or '')):
                continue
            if any(pat.search(t.get('type') or '') for t in e.get('tickets') or []):
                hits.append(e['id'])
    return sorted(set(hits))


newid = MAXID + 1
cands = []
for k, g in new_by_cd.items():
    url = g['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')
    cands.append({'newid': newid, 'artist': g['artist'], 'urls': [url], 'lg': g['lg'], 'eventCd': g['cd'],
                  'maybe_dup': maybe_dup(g),
                  'windows': sorted({(r.get('saletype'), r['rls_iso'], r['kind'], r.get('pref'), r.get('perfdate')) for r in g['rows']})})
    newid += 1
merge_in = []
for (eid, cd), m in merge_by_key.items():
    url = m['url'].replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')
    merge_in.append({'newid': newid, 'artist': m['artist'] or '', 'urls': [url], 'target': eid, 'eventCd': cd})
    newid += 1
json.dump(cands, io.open('tmp/x1001/eve/pia_cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(merge_in, io.open('tmp/x1001/eve/pia_merge_in.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(list(merge_by_key.values()), io.open('tmp/x1001/eve/pia_merge_cands.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'new': [r for g in new_by_cd.values() for r in g['rows']],
           'merge': list(merge_by_key.values())}, io.open('tmp/x1001/eve/presale_split.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('MAXID', MAXID)
print('ジャンル | 見た行 | 登録済みの窓あり | 新規候補(公演=eventCd) | 足し込み候補(行)')
for lg, st in stats.items():
    print(' %s | %d | %d | %d | %d   %s' % (lg, st['rows'], st['present'], len(st['new_cd']), st['merge'], ' / '.join(st['files'])))
print('新規候補 %d公演 / 足し込み %d件（既存id×eventCd）/ 窓あり %d行' % (len(cands), len(merge_in), present))
print('--- 新規候補 ---')
for c in cands:
    print(' %d %s | %s | %s%s' % (c['newid'], c['artist'][:40], c['eventCd'], ' '.join('%s/%s/%s/%s' % (w[0], w[1], w[3], w[4]) for w in c['windows'])[:160],
                                  '  ⚠登録済みらしい=%s' % c['maybe_dup'] if c['maybe_dup'] else ''))
print('--- 足し込み候補 ---')
for m in merge_by_key.values():
    print(' id%s %s | %s | %s' % (m['id'], (m['artist'] or '')[:30], m['eventCd'],
                                 ' '.join('%s/%s/%s/%s' % (x['saletype'], x['rlsdate'], x['pref'], x['perfdate']) for x in m['missing'])[:200]))
