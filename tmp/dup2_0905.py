# -*- coding: utf-8 -*-
"""投入前の重複チェック（きつめ版）。

前の版は「MM-DD × 会場」を総当たりで突き合わせたので、ツアーの会場リスト同士が
掛け算になって誤検知だらけになった（ライブハウスは毎日違うバンドが出る）。

ここでは次の2つだけを出す:
  A) e+ の公演ID（/sf/detail/の数字）が既にDBにある      … 本物の重複
  B) **アーティスト名が正規化して完全一致**する既存エントリ … 人が見て統合するか決める材料
     （部分一致はしない＝[[feedback_harvest_name_dedup_blindspot]]）
"""
import json, io, re, unicodedata


def nz(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\s　・･／/,、]', '', s)
    return s.lower()


hh = io.open('index.html', encoding='utf-8', newline='').read()
db = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))
dbids = set(re.findall(r'/sf/detail/(\d+)', hh))

byname = {}
for e in db:
    byname.setdefault(nz(e.get('artist')), []).append(e)

built = json.load(io.open('tmp/eplus_batch2_0905.json', encoding='utf-8'))

out = io.open('tmp/dup2_0905.txt', 'w', encoding='utf-8')
na = nb = 0
for b in built:
    eids = set(re.findall(r'/sf/detail/(\d+)', json.dumps(b, ensure_ascii=False)))
    if eids & dbids:
        na += 1
        out.write('🚨A id%d %s ／ %s ＝ eidが既にDBにある %s\n' % (b['id'], b['artist'], b['name'], sorted(eids & dbids)))

for b in built:
    hit = byname.get(nz(b.get('artist')), [])
    if hit:
        nb += 1
        out.write('■B id%d %s ／ %s\n' % (b['id'], b['artist'], b['name']))
        out.write('     候補 %s ｜ %s\n' % (b['dateLabel'], b['venue']))
        for e in hit:
            out.write('     既存 id%s %s ｜ %s ｜ %s ｜ 枠%d\n'
                      % (e['id'], e.get('name'), e.get('dateLabel'), e.get('venue'), len(e.get('tickets') or [])))

out.write('\nA(eid重複)=%d件 / B(同名の既存あり)=%d件 / 全%d件\n' % (na, nb, len(built)))
out.close()
print('A=%d B=%d N=%d' % (na, nb, len(built)))
