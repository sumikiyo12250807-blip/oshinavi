# -*- coding: utf-8 -*-
"""本当に危ない型だけを数える＝1枠に複数公演をまとめていて、締切がその最後の公演日になっているもの。
   （「公演当日の開演まで売る」形は楽天の普通なので嘘ではない＝除く）"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))

def rakuten_slot(t, e):
    u = (t.get('url') or '') or json.dumps(e.get('links') or {}, ensure_ascii=False)
    return 'rakuten' in u

rows = []
for e in EV:
    for t in e.get('tickets') or []:
        if not rakuten_slot(t, e):
            continue
        if t.get('soldout') or t.get('saleUntilSoldOut') or t.get('saleEndUnknown'):
            continue
        ty = t.get('type') or ''
        m = re.search(r'（([^（）]*?)公演）', ty)
        inner = m.group(1) if m else ''
        # 公演の指定が「複数日にまたがる」か「県が複数」か
        multi_day = '〜' in inner or '～' in inner
        prefs = [p for p in re.split(r'[・/]', inner.split(' ')[0]) if p]
        multi_pref = len(prefs) >= 2
        if not (multi_day or multi_pref):
            continue
        d = t.get('date') or ''
        if d and d == (e.get('date') or ''):
            rows.append((e['id'], (e.get('name') or '')[:32], d, len(prefs), inner[:44], ty[-22:]))

print('🚨 1枠に複数公演をまとめ、締切が最後の公演日になっている枠 = %d件' % len(rows))
print()
for i, name, d, np_, inner, tail in rows:
    print('id%-6d %-34s 締切=%s  県%d  （%s公演）… %s' % (i, name, d, np_, inner, tail))
