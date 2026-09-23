# -*- coding: utf-8 -*-
"""inject_tiget が「名前×公演日が一致」で止めた8件について、**足し先の既存エントリ**を特定する。
2026-09-23 夜。組み上がり＝tmp/built_tiget_0923pm.json、登録＝index.html。

🚨[[feedback_capture_all_deadlines_on_add]]＝突き合わせは券種名でなく「県・公演日・締切」。
🚨ここでは**調べるだけ**。足し込みは中身を見てから。
使い方: python tmp/x0923/tiget_rest8.py
"""
import io
import json
import re
import unicodedata


def norm(s):
    s = unicodedata.normalize('NFKC', s or '').lower()
    return re.sub(r'[\s　・･,，.。!！?？~〜\-—–_/／\(\)（）\[\]【】「」『』"\'’]', '', s)


text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
events, _ = json.JSONDecoder().raw_decode(text, m.start(1))
built = json.load(io.open('tmp/built_tiget_0923pm.json', encoding='utf-8'))
if isinstance(built, dict):
    built = built.get('entries') or []

have = set(re.findall(r'tiget\.net/events/(\d+)', text))

# 登録側の索引＝(正規化名, 公演日) → id
namedate = {}
for e in events:
    blob = json.dumps(e, ensure_ascii=False)
    days = set(re.findall(r'\d{4}-\d{2}-\d{2}', blob))
    for n in {norm(e.get('artist')), norm(e.get('name'))}:
        if not n:
            continue
        for d in days:
            namedate.setdefault((n, d), []).append(e['id'])

out = io.open('tmp/x0923/tiget_rest8.txt', 'w', encoding='utf-8')
n = 0
for e in sorted(built, key=lambda x: (x.get('date') or '')):
    ids = set(re.findall(r'/events/(\d+)', (e.get('links') or {}).get('tiget') or ''))
    if ids & have:
        continue                     # もう入っている
    na, nn = norm(e.get('artist')), norm(e.get('name'))
    hit = sorted(set(namedate.get((na, e['date']), []) + namedate.get((nn, e['date']), [])))
    if not hit:
        continue
    n += 1
    out.write('--- %s  %s  %s\n' % (e['date'], e.get('name'), (e.get('links') or {}).get('tiget')))
    out.write('    枠 %d：%s\n' % (len(e.get('tickets') or []),
                                 ' ｜ '.join((t.get('type') or '')[:46] for t in (e.get('tickets') or []))))
    for i in hit:
        ex = [x for x in events if x['id'] == i][0]
        out.write('    → 足し先候補 id%-6s [%s] %s ／ 枠%d ／ %s\n'
                  % (i, ex.get('genre'), (ex.get('name') or '')[:36], len(ex.get('tickets') or []),
                     ((ex.get('links') or {}).get('tiget') or (ex.get('links') or {}).get('pia')
                      or (ex.get('links') or {}).get('eplus') or '')[:56]))
        for t in (ex.get('tickets') or [])[:6]:
            out.write('        既存枠: %s\n' % (t.get('type') or '')[:60])
out.close()
print('WROTE tmp/x0923/tiget_rest8.txt  件数', n)
