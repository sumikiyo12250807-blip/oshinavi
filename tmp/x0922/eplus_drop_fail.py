# -*- coding: utf-8 -*-
"""reconcile_eplus の FAIL 枠だけを、今回入れた e+ の新着（genre:new・tmp/x0922/eplus_ids.txt）から番号指定で抜く。
枠が0本になったエントリは新着から外す（載せられる枠が無い＝入れない）。
memory project_eplus_harvester_bug_and_qc の「後始末の型」どおり。バックアップで丸ごと戻さない。
"""
import collections, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ids = {int(x) for x in io.open('tmp/x0922/eplus_ids.txt').read().split(',')}
rep = io.open('tmp/x0922/reconcile_eplus.txt', encoding='utf-8').read()
drop = collections.defaultdict(set)
kinds = collections.Counter()
for cid, ti, code in re.findall(r'^  id(\d+) t(\d+) \[([a-h])-', rep, re.M):
    if int(cid) in ids:
        drop[int(cid)].add(int(ti))
        kinds[code] += 1
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
gone, out, dropped = [], [], 0
for e in events:
    if e['id'] in drop and e.get('genre') == 'new':
        before = len(e['tickets'])
        e['tickets'] = [t for i, t in enumerate(e['tickets']) if i not in drop[e['id']]]
        dropped += before - len(e['tickets'])
        if not e['tickets']:
            gone.append(e['id'])
            continue
    out.append(e)
nl = '\r\n' if '\r\n' in src else '\n'
new_src = src[:m.start()] + m.group(1) + json.dumps(out, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
# NEW_ORDER からも外す
if gone:
    mo = re.search(r'(const NEW_ORDER\s*=\s*)(\[[^\]]*\])', new_src)
    if mo:
        order = [x for x in json.loads(mo.group(2)) if x not in set(gone)]
        new_src = new_src[:mo.start()] + mo.group(1) + json.dumps(order) + new_src[mo.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(new_src)
io.open('tmp/x0922/eplus_gone_ids.txt', 'w').write(','.join(map(str, gone)))
print('抜いた枠 %d（%s）／枠0で外したエントリ %d件' % (dropped, dict(kinds), len(gone)))
print('残ったe+新着 %d件' % (len(ids) - len(gone)))
