# -*- coding: utf-8 -*-
"""ハロプロ2組のツアーを1エントリに統合し、抜けていた公演を全部入れる（2026-08-21）。

公式で確定させた事実（別エージェントの調査・一次ソース＝ハロー!プロジェクト公式）:
  ① アンジュルム 2026秋 風林火山・弐 … 既存 4022(大阪9/20単発) と 4490(4会場) は**同じツアー**。
     https://helloproject.com/event/eea32ca83d6d9dfe389e097519cca28e46fdf1a07e83372663ef7376a2c2ec36/
  ② Juice=Juice Room Tour 2026「5ROOMS」… 既存 3882(京都9/24) と 4538(厚木9/18-19) は**同じツアー**。
     https://helloproject.com/event/ac7ec0bd437f3af1f9fcdc9c579f31312e9112fe13471d9fbae91c755990d6f2/

ぴあをアーティスト名で掃き直して（tools/pia_kw_search.py）未登録のeventCdを拾い、
既存URLとまとめて再構築した。枠は**追加**、公演日は**後ろへ伸びる時だけ**更新。
統合元（4022 / 3882）は欠番にする。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')


def key(t):
    u = re.sub(r'^https?://[^/]+', '', t.get('url') or '').replace('/pia/event/event.do', '/pia/event.do')
    return (t.get('type'), u)


MERGE = {4490: 4022, 4538: 3882}   # 残す先: 畳む元
reb = {e['id']: e for e in json.load(io.open('tmp/built_hello_0821.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

for keep, drop in MERGE.items():
    e, b, d = by[keep], reb[keep], by[drop]
    old = e.get('tickets') or []
    seen = {key(t) for t in old}
    add = [t for t in (b.get('tickets') or []) if key(t) not in seen]
    # 畳む側にしか無い枠も拾う（期限切れでも履歴として持っておく）
    add += [t for t in (d.get('tickets') or []) if key(t) not in seen and key(t) not in {key(x) for x in add}]
    print('=== id=%d %s  枠%d → %d（id=%d を畳む）' % (keep, e.get('artist'), len(old), len(old) + len(add), drop))
    for t in add:
        print('    + %s | %s' % (t.get('type'), t.get('date')))
    e['tickets'] = old + add
    if b.get('date') and b['date'] > (e.get('date') or ''):
        print('    公演日 %s → %s' % (e.get('date'), b['date']))
        e['date'] = b['date']
        e['dateLabel'] = b.get('dateLabel')
    e['venue'] = b.get('venue') or e.get('venue')
    e['prefecture'] = b.get('prefecture') or e.get('prefecture')
    e['verifiedAt'] = '2026-08-21'

KEEP = [e for e in EVENTS if e['id'] not in MERGE.values()]
assert len(KEEP) == len(EVENTS) - 2
shutil.copyfile('index.html', 'index.html.bak_0821_hello')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 → %d件（4022・3882 を欠番に） ===' % (len(EVENTS), len(KEEP)))
