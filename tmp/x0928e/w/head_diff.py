# -*- coding: utf-8 -*-
"""HEADと今で、足し込み先の枠が消えていないか数える（読むだけ）"""
import json, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
IDS = [2338, 3406, 3471, 22537, 23644]
def load(s):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', s, re.S).group(1))}
old = load(subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8'))
new = load(open('index.html', encoding='utf-8', newline='').read())
k = lambda t: json.dumps(t, ensure_ascii=False, sort_keys=True)
lost = 0
for i in IDS:
    o = [k(t) for t in old[i]['tickets']]; n = [k(t) for t in new[i]['tickets']]
    miss = [x for x in o if x not in n]
    lost += len(miss)
    print(i, '前', len(o), '後', len(n), '消えた', len(miss))
chg = [i for i in old if i in new and i not in IDS and k(old[i]) != k(new[i])]
print('消えた枠合計', lost, '／ほかに変わったid', chg[:10], '／消えたid', [i for i in old if i not in new][:10])
