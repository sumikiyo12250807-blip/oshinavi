# -*- coding: utf-8 -*-
"""新着プール(genre:"new")のうち、独立の読み直しで疑いが無かった id だけを _genre へ振り分ける（2026-09-15 朝）。
assign_apply_0914.py との違い＝対象を「tmp/assign_ok_ids_0915.txt に書いた id」に限る（プール全部を一括で動かさない）。
決まり＝ぴあの言う通りに写す・人が最終判断する枠を作らない（memory feedback_genre_pia_asis_and_other）。
🚨 保留id（迷った件・ぴあ以外・削除の検証待ち）は一覧に入っていても振り分けない（memory feedback_new_pool_ok_before_assign）。
NEW_ORDER（新着タブの並び）からも振り分けた id を外す（memory feedback_new_order_array）。改行は CRLF を保つ。

使い方:
  python tmp/assign_apply_0915.py            # 一覧だけ（書き換えない）
  python tmp/assign_apply_0915.py --apply    # 適用＋ logs/assigned_2026-09-15.md
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()

HOLD = {
    8172,  # 瑛人×SANIMYOK PUAN Live2026＝ぴあの区分は「演歌・邦楽」だが瑛人はJ-POP（9/13から保留）
    7558,  # Tommy february6 豪華アナログBOX＝照合がSTALE（9/12から）
    7946,  # 源 上映会＝ぴあのeventCdが無効・他の売り場も見つからない（ユーザーに聞いている最中）
    8351,  # Chevon 横浜アリーナ当日券＝公演9/13で終わり・続きの公演を足すか消すかをユーザーに聞いている
    # 楽天由来＝振り分けはユーザーの確認後（PLAYBOOK ⛔例外）
    8378, 8379, 8380, 8381, 8382, 8383, 8384, 8432,
}
OVERRIDE = {}
NOTE = ('9/14 に入れたぴあ由来の新着。別エージェントがぴあの実ページから公演・枠・ジャンル表記をゼロで読み直し、'
        '登録と食い違いが無かった分だけ（tmp/compare_recheck_0915.md・9/14 の読み直し分は tmp/compare_pushcheck_0914*.md）。')

APPLY = '--apply' in sys.argv
OK = {int(x) for x in re.findall(r'\d+', io.open('tmp/assign_ok_ids_0915.txt', encoding='utf-8').read())}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

targets, skipped = [], []
for e in events:
    if e.get('genre') != 'new':
        continue
    if e['id'] in HOLD or e['id'] not in OK:
        skipped.append(e['id'])
        continue
    g = OVERRIDE.get(e['id']) or e.get('_genre')
    if not g:
        print('⚠️ id%s は下書きジャンルが無い＝振り分けない' % e['id'])
        skipped.append(e['id'])
        continue
    targets.append(e)

pool = sum(1 for e in events if e.get('genre') == 'new')
print('新着 %d件 / 振り分ける %d件 / 残す %d件（一覧 %d件のうちプールに無い %d件）' % (
    pool, len(targets), len(skipped), len(OK), len(OK - {e['id'] for e in events if e.get('genre') == 'new'})))
by = {}
for e in targets:
    g = OVERRIDE.get(e['id']) or e.get('_genre')
    by[g] = by.get(g, 0) + 1
print('  内訳: ' + ' / '.join('%s %d' % kv for kv in sorted(by.items(), key=lambda x: -x[1])))
if not APPLY:
    print('（--apply で適用）')
    sys.exit(0)

rows = []
for e in targets:
    g = OVERRIDE.get(e['id']) or e.get('_genre')
    e['genre'] = g
    rows.append((e['id'], g, e.get('name') or '', (e.get('links') or {}).get('pia') or ''))

nl = '\r\n' if '\r\n' in src else '\n'
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start()] + m.group(1) + body + m.group(3) + src[m.end():]

# NEW_ORDER から振り分けた id を外す（並びはそのまま）
done = {r[0] for r in rows}
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
order = [int(x) for x in mo.group(1).split(',') if x.strip()]
left_order = [i for i in order if i not in done]
out = out[:mo.start()] + 'const NEW_ORDER = [%s];' % ', '.join(str(i) for i in left_order) + out[mo.end():]

ev2 = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', out, re.S).group(1))
left = sorted(e['id'] for e in ev2 if e.get('genre') == 'new')
assert len(ev2) == len(events), 'エントリ件数が変わった'
assert left == sorted(left_order), 'NEW_ORDER と新着プールの中身が合わない %s / %s' % (left[:10], left_order[:10])
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)

with io.open('logs/assigned_%s.md' % TODAY, 'a', encoding='utf-8') as f:
    f.write('# %s 振り分けたもの（朝）\n\n' % TODAY)
    f.write(NOTE + '\n')
    f.write('保留（プールに残した）＝%s ／ 読み直しで食い違いがあった・読めなかった分も残した\n\n' % ', '.join(str(i) for i in sorted(HOLD)))
    f.write('| id | 公演名 | ジャンル | 確認用URL |\n|---|---|---|---|\n')
    for i, g, n, u in rows:
        f.write('| %s | %s | %s | %s |\n' % (i, n.replace('|', '／'), g, u))
print('✅ %d件を振り分けた。新着プールの残り %d件（NEW_ORDER も同じ %d件）→ logs/assigned_%s.md' % (
    len(rows), len(left), len(left_order), TODAY))
