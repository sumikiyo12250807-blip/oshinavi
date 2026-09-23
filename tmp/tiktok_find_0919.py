# TikTokerのイベントを探す＝①登録の名前・出演者 ②TIGETから取った元データ（説明文つき）で「TikTok/ティックトック」を含むもの
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
KW = re.compile(r'tik\s*tok|ティックトック|ティックトッカー|TikToker', re.I)
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', io.open('index.html', encoding='utf-8').read(), re.S).group(1))
byurl = {}
for e in E:
    for u in [(e.get('links') or {}).get('tiget')] + [t.get('url') for t in e.get('tickets') or []]:
        m = re.search(r'tiget\.net/events/(\d+)', u or '')
        if m:
            byurl[m.group(1)] = e
print('== ① 登録の名前・出演者')
for e in E:
    t = (e.get('name') or '') + ' ' + (e.get('artist') or '')
    if KW.search(t):
        print(' ', e['id'], e['genre'], e.get('extraGenres'), t[:90])
print('== ② TIGETの説明文にTikTokとある登録済みイベント')
raw = json.load(io.open('tmp/tiget_0918_all.json', encoding='utf-8'))
items = raw if isinstance(raw, list) else (raw.get('events') or raw.get('items') or list(raw.values())[0])
n = 0
for d in items:
    if not isinstance(d, dict):
        continue
    eid = str(d.get('eid') or d.get('id') or '')
    blob = json.dumps(d, ensure_ascii=False)
    m = KW.search(blob)
    if m and eid in byurl:
        e = byurl[eid]
        i = m.start()
        print(' ', e['id'], e['genre'], e.get('extraGenres'), (e.get('name') or '')[:50], '｜', blob[max(0, i - 40):i + 40].replace('\\n', ' '))
        n += 1
print('説明文ヒット', n)
