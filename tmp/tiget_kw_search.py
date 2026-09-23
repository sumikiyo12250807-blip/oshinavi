# TIGETを言葉で検索（q[words]）し、ヒットしたイベントの名前・公演日と、OSHINAVIに載っているかを出す
#   python tmp/tiget_kw_search.py TikTok ティックトック
import io, json, re, sys, time, urllib.parse, urllib.request, html as H
sys.stdout.reconfigure(encoding='utf-8')
UA = {'User-Agent': 'Mozilla/5.0'}
src = io.open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', src, re.S).group(1))
reg = {}
for e in E:
    for u in [(e.get('links') or {}).get('tiget')] + [t.get('url') for t in e.get('tickets') or []]:
        m = re.search(r'tiget\.net/events/(\d+)', u or '')
        if m:
            reg[m.group(1)] = e
seen = {}
for kw in sys.argv[1:]:
    for page in range(1, 6):
        url = 'https://tiget.net/events?' + urllib.parse.urlencode({'q[words]': kw, 'page': page})
        s = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        ids = list(dict.fromkeys(re.findall(r'href="/events/(\d+)"', s)))
        new = [i for i in ids if i not in seen]
        if not new:
            break
        for i in new:
            seen[i] = kw
        time.sleep(1)
print('ヒット', len(seen))
for i, kw in seen.items():
    e = reg.get(i)
    if e:
        print('  登録あり id%s [%s %s] %s' % (e['id'], e['genre'], e.get('extraGenres') or '', (e.get('name') or '')[:60]))
    else:
        print('  未登録 https://tiget.net/events/%s（%s）' % (i, kw))
