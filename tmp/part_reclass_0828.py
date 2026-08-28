# -*- coding: utf-8 -*-
"""部分一致20件を「同じ興行主体か」で仕分け直す。
🚨教訓＝「新日本フィル」は「日本フィル」を部分文字列として含む＝素の in 判定は別団体を畳む。
   ぶら下がり先の名前が、ぴあの公演名の**先頭から**現れる時だけ「同じ主体」とみなす。
   （ツアー名は『<アーティスト> <ツアー名>』の形で、頭にアーティスト名が来る）"""
import json, io, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･/／「」『』【】（）()\[\]～~ー-]', '', s).lower()

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}
d = json.load(io.open('tmp/batch_cand_0828.json', encoding='utf-8'))
part = [x for x in d['dup'] if x['why'].startswith('部分一致')]

same, diff = [], []
for x in part:
    it = x['it']
    eid = int(re.search(r'id(\d+)', x['why']).group(1))
    e = EV.get(eid)
    if not e:
        diff.append((eid, it, '既存が見つからない')); continue
    a = norm(it['artist'])
    for f in ('artist', 'name'):
        pass
    ea, en = norm(e.get('artist')), norm(e.get('name'))
    # 既存名がぴあ公演名の「頭」に出るか、ぴあ公演名が既存名の頭に出るか
    ok = any(a.startswith(v) or v.startswith(a) for v in (ea, en) if v)
    (same if ok else diff).append((eid, it, ('頭一致' if ok else '頭が違う＝別主体の疑い')))

o = io.open('tmp/dup_part_0828.md', 'w', encoding='utf-8')
o.write('# 2026-08-28 部分一致の仕分け直し（%d件）\n\n' % len(part))
o.write('判定＝**既存の名前がぴあの公演名の頭に来るか**。素の部分一致だと「新日本フィル」が「日本フィル」に畳まれる。\n\n')
o.write('## ✅ 同じ主体＝既存へ統合してよい（%d件）\n\n' % len(same))
o.write('| 既存id | 既存の名前 | ぴあの公演名 | 公演日 | 発売日 | URL |\n|---|---|---|---|---|---|\n')
for eid, it, why in same:
    o.write('| %d | %s | %s | %s | %s | %s |\n' % (eid, (EV[eid].get('name') or '')[:34],
            (it['artist'] or '').replace('|', '｜')[:40], (it.get('perfdate') or '')[:24], it.get('rlsdate', ''), it['url']))
o.write('\n## 🚨 別の主体の疑い＝畳まず新規で入れる候補（%d件）\n\n' % len(diff))
o.write('| ぶら下がった既存id | 既存の名前 | ぴあの公演名 | 公演日 | 発売日 | URL |\n|---|---|---|---|---|---|\n')
for eid, it, why in diff:
    o.write('| %d | %s | %s | %s | %s | %s |\n' % (eid, (EV.get(eid, {}).get('name') or '')[:34],
            (it['artist'] or '').replace('|', '｜')[:40], (it.get('perfdate') or '')[:24], it.get('rlsdate', ''), it['url']))
o.close()
json.dump({'same': [{'eid': e, 'it': i} for e, i, _ in same], 'diff': [{'eid': e, 'it': i} for e, i, _ in diff]},
          io.open('tmp/part_reclass_0828.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('同じ主体（統合してよい） %d件 / 別主体の疑い %d件' % (len(same), len(diff)))
for eid, it, _ in diff:
    print('   🚨 id%-5s %-34s ← %s' % (eid, (EV.get(eid, {}).get('name') or '')[:32], (it['artist'] or '')[:40]))
