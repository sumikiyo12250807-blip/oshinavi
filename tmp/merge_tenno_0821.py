# -*- coding: utf-8 -*-
"""天皇杯2回戦の重複を統合する（3337 ← 4789）。

ジャンル判定エージェントの指摘で発覚。
  既存 3337（sports）＝eventCd=2626454 の単発ページ由来で **10会場・枠10**
  新着 4789（new）  ＝eventBundleCd=b2670118 の大会バンドル由来で **32会場・枠35**
同じ「第106回天皇杯 2回戦（8/26）」。**4789 のほうが完全**なので中身を 3337 に寄せ、
4789 を欠番にする（既存idを残す＝振り分け済みのidを生かす）。

独立検証（別エージェント）の読み取り＝2回戦32会場＋等々力のグループ席1＋駐車券2＝**買える35枠**、
締切は大半が 8/25(火)23:59。1回戦24枠は販売終了で対象外。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}
old, new = by[3337], by[4789]
print('before 3337: 枠%d / genre=%s' % (len(old['tickets']), old.get('genre')))
print('       4789: 枠%d / genre=%s' % (len(new['tickets']), new.get('genre')))

# 3337 側にしか無い枠が無いことを確認（あるなら足す）
seen = {(t.get('url'), t.get('date')) for t in new['tickets']}
extra = [t for t in old['tickets'] if (t.get('url'), t.get('date')) not in seen]
print('3337 にしか無い枠: %d件' % len(extra))
for t in extra:
    print('   ! ', t.get('type'), t.get('url'))

old['name'] = new['name']
old['artist'] = new.get('artist') or new['name']
old['venue'] = new['venue']
old['prefecture'] = new['prefecture']
old['date'] = new['date']
old['dateLabel'] = new.get('dateLabel')
old['links'] = dict(old.get('links') or {}, pia=(new.get('links') or {}).get('pia'))
old['tickets'] = new['tickets'] + extra
old['verifiedAt'] = '2026-08-21'
print('after  3337: 枠%d / genre=%s（据え置き）' % (len(old['tickets']), old.get('genre')))

KEEP = [e for e in EVENTS if e['id'] != 4789]
assert len(KEEP) == len(EVENTS) - 1
shutil.copyfile('index.html', 'index.html.bak_0821_tenno')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== %d件 → %d件（4789を欠番に） ===' % (len(EVENTS), len(KEEP)))
