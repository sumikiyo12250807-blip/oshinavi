# -*- coding: utf-8 -*-
"""発売前スイープの「未掲載候補」から、本当に未登録のものだけを残す（読むだけ・2026-09-13 朝）。

ハーベスタの未掲載判定は eventCd 一致。だが同じ公演が**別URLで登録済み**のことがある
（統合・ツアーまとめ・後からぴあが作り直した bundle）。そのまま投入すると二重登録になる。
だから「正規化した名前 × 公演日」でもう一度当てて、1日でも登録済みなら候補から外す。
🚨 逆に、名前が違っても対バン名・フェス名で登録済みのことがある（project_big_artist_crosscheck）。
   ここで拾えるのは名前が同じ型だけ＝投入前の check_badges／reconcile と併せて見る。

使い方: python tmp/filter_new_cands_0913.py
出力: tmp/cands_0913.json（build_pia_entries にそのまま渡せる形）＋ tmp/cands_0913.txt
"""
import glob
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')

src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\']', '', s)


have, codes = set(), set()
for e in ev:
    n = norm(e.get('artist') or e.get('name'))
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in (e.get('tickets') or [])]:
        codes |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', u))
    for t in e.get('tickets') or []:
        mm = re.search(r'（([^（）]*)公演）', t.get('type') or '')
        if not mm:
            continue
        y = 2026
        for r9, mo, dd in re.findall(r'(R9年\s*)?(\d{1,2})/(\d{1,2})', mm.group(1)):
            if r9:
                y = 2027
            have.add((n, '%04d-%02d-%02d' % (y, int(mo), int(dd))))

seen, out, lines = set(), [], []
nid = 100000
for p in sorted(glob.glob('tmp/sweep_presale_0913/*.json')):
    lg = p.split('\\')[-1].split('/')[-1][:2]
    d = json.load(io.open(p, encoding='utf-8'))
    for r in d.get('new') or []:
        url = r.get('url') or ''
        mcd = re.search(r'event(?:Bundle)?Cd=(\w+)', url)
        cd = mcd.group(1) if mcd else ''
        if not cd or cd in codes or cd in seen:
            continue
        n = norm(r.get('artist'))
        days = ['%s-%02d-%02d' % (y, int(mo), int(dd))
                for y, mo, dd in re.findall(r'(\d{4})/(\d{1,2})/(\d{1,2})', r.get('perfdate') or '')]
        reg = [x for x in days if (n, x) in have]
        if days and len(reg) == len(days):
            lines.append('  ⏭ 登録済み lg=%s %-26s %s' % (lg, (r.get('artist') or '')[:26], days))
            continue
        seen.add(cd)
        nid += 1
        out.append({'newid': nid, 'artist': r.get('artist'), 'urls': [url], '_lg': lg,
                    '_perfdate': r.get('perfdate'), '_rlsdate': r.get('rlsdate'), '_pref': r.get('pref')})
        lines.append('  ✅ 候補   lg=%s %-26s 発売%s 公演%s %s' % (
            lg, (r.get('artist') or '')[:26], r.get('rlsdate'), days or r.get('perfdate'), url))

json.dump(out, io.open('tmp/cands_0913.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open('tmp/cands_0913.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('本当に未登録の候補 %d件 → tmp/cands_0913.json' % len(out))
print('\n'.join(lines))
