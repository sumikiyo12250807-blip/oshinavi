# -*- coding: utf-8 -*-
"""指定idの dateLabel / date / prefecture を HEAD と現物で並べる（読むだけ）。"""
import json, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
IDS = [int(x) for x in sys.argv[1].split(',')]


def load(t):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', t, re.S).group(1))}


old = load(subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8', 'replace'))
new = load(open('index.html', encoding='utf-8').read())
for i in IDS:
    a, b = old.get(i, {}), new.get(i, {})
    print('id%s %s' % (i, (b.get('name') or '')[:30]))
    print('   前 %s | %s' % (a.get('dateLabel'), a.get('prefecture')))
    print('   後 %s | %s' % (b.get('dateLabel'), b.get('prefecture')))
