# -*- coding: utf-8 -*-
"""pia_kw_search の結果と登録を突合して「ぴあにあるのに載っていない」枠を出す。
X投稿に出す公演の取りこぼし潰し用（feedback_pia_bundle_hides_shows）。
  python tmp/kwaudit_0828.py <検索語>
"""
import io, re, json, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')
kw = sys.argv[1]
subprocess.run([sys.executable, 'tools/pia_kw_search.py', kw], capture_output=True)
t = io.open('tmp/pia_kw_search.txt', encoding='utf-8').read()
blocks = re.split(r'\n(?=\[)', t)
rows = []
for b in blocks:
    if not b.startswith('['):
        continue
    u = re.search(r'URL   : (\S+)', b)
    d = re.search(r'公演日: (.+)', b)
    v = re.search(r'会場  : (.+)', b)
    r = re.search(r'発売日: (.+)', b)
    if u:
        rows.append({'url': u.group(1), 'perf': (d.group(1).strip() if d else ''),
                     'venue': (v.group(1).strip() if v else ''), 'rls': (r.group(1).strip() if r else ''),
                     'title': b.split('\n')[0]})
h = io.open('index.html', encoding='utf-8', newline='').read()
E = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
have = set()
for e in E:
    L = e.get('links') or {}
    for x in (L.get('pia'),):
        if x:
            have |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', x))
    for tk in (e.get('tickets') or []):
        if tk.get('url'):
            have |= set(re.findall(r'event(?:Bundle)?Cd=(\w+)', tk['url']))
miss = [r for r in rows if not (set(re.findall(r'event(?:Bundle)?Cd=(\w+)', r['url'])) & have)]
print('■ %s ぴあ %d件 / 未掲載 %d件' % (kw, len(rows), len(miss)))
for r in miss:
    print('   %s | %s | %s | 発売%s | %s' % (r['title'][:24], r['perf'][:26], r['venue'][:28], r['rls'], r['url']))
