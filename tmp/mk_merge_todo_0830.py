# -*- coding: utf-8 -*-
"""統合待ちを「完全一致」と「部分一致」に分ける。
完全一致だけを自動の統合対象にし、部分一致は目視候補として別に出す
（部分一致は機械で決めきれない＝2026-08-23の教訓）。"""
import json, io, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('tmp/batch_cand_0830.json', encoding='utf-8'))
full, part = collections.defaultdict(list), []
for x in d['dup']:
    it, why = x['it'], x['why']
    m = re.search(r'id(\d+)', why)
    if not m:
        continue
    if why.startswith('完全一致'):
        full[m.group(1)].append({k: it.get(k) for k in ('url', 'artist', 'perfdate', 'rlsdate')})
    else:
        part.append((m.group(1), it, why))
io.open('tmp/merge_todo_0830.json', 'w', encoding='utf-8').write(json.dumps(full, ensure_ascii=False, indent=1))
o = io.open('tmp/dup_part_0830.md', 'w', encoding='utf-8')
o.write('# 2026-08-30 部分一致で統合待ち（機械で決めきれない＝目視候補）%d件\n\n' % len(part))
o.write('| 既存id | ぴあの公演名 | 公演日 | 発売日 | URL |\n|---|---|---|---|---|\n')
for eid, it, why in part:
    o.write('| %s | %s | %s | %s | %s |\n' % (eid, (it['artist'] or '').replace('|', '｜')[:44],
            (it.get('perfdate') or '')[:26], it.get('rlsdate', ''), it['url']))
o.close()
n = collections.Counter({k: len(v) for k, v in full.items()})
print('完全一致の統合対象: 既存%dエントリ / 枠%d' % (len(full), sum(len(v) for v in full.values())))
print('部分一致(目視候補): %d件 → tmp/dup_part_0830.md' % len(part))
multi = [(k, v) for k, v in n.most_common() if v >= 2]
print('同じ既存idに2つ以上ぶら下がる＝ツアー分裂の疑い: %d件' % len(multi))
for k, v in multi[:12]:
    print('   id%s に %d枠' % (k, v))
