# -*- coding: utf-8 -*-
"""2026-08-21 朝の便：公演終了エントリの削除。

check_expired.py の削除候補12件のうち、
  ・2642 高校野球 ＝ **決勝(8/22)の枠が今日10:00発売** と reconcile が検出 → 救済済み（削除しない）
  ・1037 おどる絵本 ＝ **水戸芸術館9/5-6が残っている**（主催のみ販売）→ 救済済み（削除しない）
  ・2738 FREEDOMS ＝ ぴあに受付中の別興行4本が未登録。消すとサイトからFREEDOMSが消える → 保留（相談）
を除いた **9件** を削除する。

検証＝別エージェント2本に「削除は誤りという前提で」独立再導出させ、9件とも
「公演終了かつ買える枠ゼロ」で一致。機械照合＝reconcile_pia --ids で 登録0=ぴあ0 一致。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

DEL = [943, 963, 1294, 2689, 3230, 3479, 3649, 4330, 4348]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
before = len(EVENTS)
gone = [e for e in EVENTS if e['id'] in DEL]
assert len(gone) == len(DEL), [e['id'] for e in gone]
for e in gone:
    print('削除 id=%d %s | %s | %s' % (e['id'], e.get('name'), e.get('venue'), e.get('date')))
KEEP = [e for e in EVENTS if e['id'] not in DEL]
assert len(KEEP) == before - len(DEL)

io.open('tmp/deleted_0821.json', 'w', encoding='utf-8').write(json.dumps(gone, ensure_ascii=False, indent=1))
shutil.copyfile('index.html', 'index.html.bak_0821_morning_delete')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 → %d件（-%d） ===' % (before, len(KEEP), len(DEL)))
