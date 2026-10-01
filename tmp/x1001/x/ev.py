import json, sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('index.html', encoding='utf-8').read()
i = s.index('const EVENTS = ['); j = s.index('\n];', i)
E = json.loads(s[i + len('const EVENTS = '):j + 2])
BY = {e['id']: e for e in E}
def show(i):
    e = BY[i]
    print(i, {k: e.get(k) for k in ('artist', 'name', 'venue', 'prefecture', 'date', 'dateLabel', 'genre', 'links')})
    for t in e.get('tickets') or []:
        print('   ', t)
if __name__ == '__main__':
    for a in sys.argv[1:]:
        show(int(a))
