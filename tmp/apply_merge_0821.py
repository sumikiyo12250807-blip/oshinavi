# -*- coding: utf-8 -*-
"""ツアー分裂の回収＝既存エントリに「未登録だった公演の枠」を足す。

🚨【置換ではなく追加】既存の枠には会場名つきバッジなど手を入れた情報が入っていることがあり、
置換すると失う（2026-08-21朝、天皇杯で「登録側のほうが良い」実例を踏んだ）。
公演日(date)は**後ろへ伸びる時だけ**更新する（ツアーの千秋楽が延びる方向は正しい変化。
縮む方向は「1公演ぶんしか見ていない」サインなので触らない）。

入力＝tmp/rebuilt_merge_0821.json（build_pia_entries が既存URL＋未登録URLをまとめて再構築したもの）
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')


def key(t):
    u = re.sub(r'^https?://[^/]+', '', t.get('url') or '').replace('/pia/event/event.do', '/pia/event.do')
    return (t.get('type'), u)


reb = {e['id']: e for e in json.load(io.open('tmp/rebuilt_merge_0821.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

rows, added, moved = [], 0, 0
for e in EVENTS:
    b = reb.get(e['id'])
    if not b:
        continue
    old = e.get('tickets') or []
    seen = {key(t) for t in old}
    add = [t for t in b.get('tickets') or [] if key(t) not in seen]
    if not add and not (b.get('date') and b['date'] > (e.get('date') or '')):
        continue
    line = ['id=%d %s 枠%d→%d' % (e['id'], e.get('artist'), len(old), len(old) + len(add))]
    for t in add:
        line.append('    + %s | %s' % (t.get('type'), t.get('date')))
    if b.get('date') and b['date'] > (e.get('date') or ''):
        line.append('    公演日 %s → %s（千秋楽が後ろに伸びた）' % (e.get('date'), b['date']))
        e['date'] = b['date']
        if b.get('dateLabel'):
            e['dateLabel'] = b['dateLabel']
        if b.get('venue'):
            e['venue'] = b['venue']
        if b.get('prefecture'):
            e['prefecture'] = b['prefecture']
        moved += 1
    e['tickets'] = old + add
    e['verifiedAt'] = '2026-08-21'
    added += len(add)
    rows.append('\n'.join(line))

print('\n'.join(rows))
print('\n=== %d エントリに %d 枠を追加 / 千秋楽が伸びたもの %d件 ===' % (len(rows), added, moved))
shutil.copyfile('index.html', 'index.html.bak_0821_tourmerge')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
io.open('tmp/apply_merge_0821.txt', 'w', encoding='utf-8').write('\n'.join(rows))
