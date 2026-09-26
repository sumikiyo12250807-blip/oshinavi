# -*- coding: utf-8 -*-
"""pia_built_raw.json（build_pia_entries の出力）から、新規として出せないものを外す（読むだけ）。
外す: 枠0 / 公演が過去 / 出す側の申込。出力: pia_built_new.json・pia_excluded.json"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-26'
built = json.load(open('tmp/x0926/pia_built_raw.json', encoding='utf-8'))
cands = {c['newid']: c for c in json.load(open('tmp/x0926/pia_cands.json', encoding='utf-8'))}
SELLER = re.compile(r'出店|出展|出演者募集|出演者.{0,4}募集|ブース|ボランティア募集|スタッフ募集|応募者|オーディション')
UNSURE = re.compile(r'募集|エントリー|参加申込|参加券|出場')
keep, exc, unsure = [], [], []
got = set()
for e in built:
    got.add(e['id'])
    tks = e.get('tickets') or []
    txt = (e.get('artist') or '') + ' ' + (e.get('name') or '') + ' ' + ' '.join(t.get('type') or '' for t in tks)
    why = None
    if not tks:
        why = '枠0'
    elif (e.get('date') or '9999') < TODAY:
        why = '公演が過去(%s)' % e.get('date')
    elif SELLER.search(txt):
        why = '出す側の申込(%s)' % SELLER.search(txt).group(0)
    if why:
        exc.append({'newid': e['id'], 'artist': e.get('artist'), 'url': (e.get('links') or {}).get('pia'), 'reason': why})
        continue
    if UNSURE.search(txt):
        unsure.append({'newid': e['id'], 'artist': e.get('artist'), 'url': (e.get('links') or {}).get('pia'),
                       'word': UNSURE.search(txt).group(0), 'types': [t['type'] for t in tks]})
    keep.append(e)
for nid, c in cands.items():
    if nid not in got:
        exc.append({'newid': nid, 'artist': c['artist'], 'url': c['urls'][0], 'reason': 'build skip（買える枠・発売前の枠0 or 取得失敗）'})
nt = sum(len(e['tickets']) for e in keep)
pre = [e for e in keep if any(t.get('startDate') and t['startDate'] > TODAY or re.search(r'\d+/\d+ \d+:\d+発売', t.get('type') or '') for t in e['tickets'])]
json.dump(keep, io.open('tmp/x0926/pia_built_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({'excluded': exc, 'unsure': unsure}, io.open('tmp/x0926/pia_excluded.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('新規 %d件 / 枠 %d / 発売前の枠を持つ %d件 (%.0f%%)' % (len(keep), nt, len(pre), 100.0 * len(pre) / max(1, len(keep))))
print('外した %d件:' % len(exc))
for x in exc:
    print('  id%s %s | %s | %s' % (x['newid'], x['artist'], x['reason'], x['url']))
print('迷い %d件:' % len(unsure))
for x in unsure:
    print('  id%s %s | 語=%s | %s' % (x['newid'], x['artist'], x['word'], x['url']))
