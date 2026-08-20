"""育成ドライラン結果を要約：枠が増える件・減る件・会場が全国化する件を仕分ける"""
import re

SRC = r'C:\Users\user\oshinavi\tmp\grow_jpop_0802.txt'
OUT = r'C:\Users\user\oshinavi\tmp\grow_summary_0802.txt'

txt = open(SRC, encoding='utf-8').read()
blocks = txt.split('=' * 72)

rows = []
for b in blocks:
    m = re.search(r'id=(\d+)\s+(.*?)\s+ぴあURL (\d+)本（既存(\d+) \+ 新規(\d+)）', b)
    if not m:
        continue
    eid, name = int(m.group(1)), m.group(2).strip()
    ms = re.search(r'枠 (\d+) → (\d+)（うち非ぴあ据置 (\d+)）', b)
    before, after, keep = (int(ms.group(1)), int(ms.group(2)), int(ms.group(3))) if ms else (None, None, None)
    mf = re.search(r'千秋楽 (\S+) → (\S+)', b)
    fin_b, fin_a = (mf.group(1), mf.group(2)) if mf else ('-', '-')
    mp = re.search(r'県\s+(\S+) → (\S+)', b)
    pref_b, pref_a = (mp.group(1), mp.group(2)) if mp else ('-', '-')
    # 追加される枠のテキスト
    cur = re.search(r'--- 今の枠 ---\n(.*?)\n  --- 作り直した枠 ---', b, re.S)
    new = re.search(r'--- 作り直した枠 ---\n(.*?)$', b, re.S)
    cur_t = [x.strip() for x in (cur.group(1).splitlines() if cur else []) if x.strip()]
    new_t = [x.strip() for x in (new.group(1).splitlines() if new else []) if x.strip()]
    added = [x for x in new_t if x not in cur_t]
    lost = [x for x in cur_t if x not in new_t]
    rows.append(dict(id=eid, name=name, before=before, after=after, keep=keep,
                     fin_b=fin_b, fin_a=fin_a, pref_b=pref_b, pref_a=pref_a,
                     added=added, lost=lost))

gain = [r for r in rows if r['after'] and r['before'] is not None and r['after'] > r['before']]
same = [r for r in rows if r['after'] == r['before']]
drop = [r for r in rows if r['after'] is not None and r['before'] is not None and r['after'] < r['before']]
natl = [r for r in gain if r['pref_b'] != '全国' and r['pref_a'] == '全国']

L = []
L.append('育成ドライラン要約  対象%d件' % len(rows))
L.append('  枠が増える: %d 件 / 変化なし: %d 件 / 枠が減る: %d 件' % (len(gain), len(same), len(drop)))
L.append('  うち県が「全国」に変わる(=ツアー化・別グループ混入を疑う): %d 件' % len(natl))
L.append('')
L.append('=== ① 枠が増える %d 件（増加数の多い順）===' % len(gain))
for r in sorted(gain, key=lambda x: -(x['after'] - x['before'])):
    flag = ' 🚨県→全国' if (r['pref_b'] != '全国' and r['pref_a'] == '全国') else ''
    L.append('id=%d  %s  枠 %d→%d (+%d)  千秋楽 %s→%s  県 %s→%s%s' % (
        r['id'], r['name'], r['before'], r['after'], r['after'] - r['before'],
        r['fin_b'], r['fin_a'], r['pref_b'], r['pref_a'], flag))
    for a in r['added']:
        L.append('      + %s' % a)
    for x in r['lost']:
        L.append('      - 消える: %s' % x)
L.append('')
L.append('=== ② 枠が減る %d 件（適用しない）===' % len(drop))
for r in drop:
    L.append('id=%d  %s  枠 %d→%d' % (r['id'], r['name'], r['before'], r['after']))
L.append('')
L.append('=== ③ 枠は変わらないが千秋楽が動く %d 件 ===' % len([r for r in same if r['fin_b'] != r['fin_a']]))
for r in same:
    if r['fin_b'] != r['fin_a']:
        L.append('id=%d  %s  千秋楽 %s→%s' % (r['id'], r['name'], r['fin_b'], r['fin_a']))

open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('rows=%d gain=%d same=%d drop=%d natl=%d' % (len(rows), len(gain), len(same), len(drop), len(natl)))
