# index.html の大きさと EVENTS配列の大きさ・件数を測る
import os, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', h, re.S)
E = json.loads(m.group(1))
print('index.html %.2fMB / EVENTS %.2fMB / %d件 / 新着 %d件' % (
    os.path.getsize('index.html') / 1e6, len(m.group(1).encode('utf-8')) / 1e6, len(E),
    sum(1 for e in E if e['genre'] == 'new')))
