# -*- coding: utf-8 -*-
"""true_missing_*.json（明日〜3日後の本当の抜け）から、ぴあで組み立てる候補を作る（2026-09-19 夜）。
  足し込み＝足す先(target)が1つに決まっているもの：そのエントリのぴあURL全部＋抜けのURLで引き直す
  新規＝足す先の候補が0件のもの：同じ名前をまとめて1エントリ
  保留＝足す先の候補が2つ以上（どれに足すか決められない）→ 報告だけ
出力: tmp/x0920/cands_merge.json / cands_new.json / cands_hold.txt"""
import glob, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}
rows = []
for f in sorted(glob.glob('tmp/x0920/true_missing_0*.json')):
    rows += json.load(io.open(f, encoding='utf-8'))


def pia_urls(e):
    us = [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets') or []]
    return [u for u in dict.fromkeys(us) if u and 'pia.jp' in u and 'w.pia.jp' not in u]


merge, new, hold = {}, {}, []
for r in rows:
    if r.get('target'):
        e = EV[r['target']]
        d = merge.setdefault(e['id'], {'newid': e['id'], 'artist': e['artist'], 'urls': pia_urls(e)})
        if r.get('url') and r['url'] not in d['urls']:
            d['urls'].append(r['url'])
    elif not r.get('cands'):
        if not r.get('url'):
            hold.append('URLなし ' + r['date'] + ' ' + r['artist'])
            continue
        d = new.setdefault(r['artist'], {'newid': 90100 + len(new), 'artist': r['artist'], 'urls': []})
        if r['url'] not in d['urls']:
            d['urls'].append(r['url'])
    else:
        hold.append('足す先が決まらない %s %s 候補=%s %s' % (r['date'], r['artist'], r['cands'], r.get('url')))
json.dump(list(merge.values()), io.open('tmp/x0920/cands_merge.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(list(new.values()), io.open('tmp/x0920/cands_new.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open('tmp/x0920/cands_hold.txt', 'w', encoding='utf-8').write('\n'.join(hold) + '\n')
print('足し込み', len(merge), '/ 新規', len(new), '/ 保留', len(hold))
for x in hold:
    print('  ', x[:150])
