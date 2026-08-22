# -*- coding: utf-8 -*-
"""再導出した結果を既存エントリに**足すだけ**当てる（2026-08-22の統合）。

🚨🚨 最初「再導出した tickets でまるごと置き換える」設計にして差分を見たら、
   **キュウソネコカミが 17→11 枠、高嶋ちさ子が 3→2 枠**のように**減る**エントリが8件出た。
   キュウソネコカミは昨日(8/21)に手で 8→14公演へ直したばかりの子で、置き換えたら**その修正が消える**。
   ＝[[feedback_dedup_badges_keeps_urls]]の「ヒールや統合の直後に常設ツールを流すと直した内容を壊す」型。
   build_pia_entries は (公演日,会場,券種名,状態) で行を潰すので、手で分けた枠も畳んでしまう。

→ **足すだけにする**。既存の枠は1つも消さない。増えた分だけ append する。
   減る方向の差分は「消す」のではなく**報告して人が見る**（tmp/merge_shrink_0823.txt）。

日付・会場も**伸びる方向にだけ**更新する（千秋楽が後ろに伸びた時だけ date を更新）。

使い方:
  python tmp/merge_apply_0823.py            # 差分を見るだけ
  python tmp/merge_apply_0823.py --apply
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

built = {e['id']: e for e in json.load(open('tmp/merge_built_0823.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}


def key(t):
    """同じ枠かどうかの判定＝バッジ文言＋締切。文言が同じでも締切が違えば別の枠。"""
    return (t.get('type'), t.get('date'))


log = io.open('tmp/merge_diff_0823.txt', 'w', encoding='utf-8')
shrink = io.open('tmp/merge_shrink_0823.txt', 'w', encoding='utf-8')
shrink.write('# 再導出のほうが枠が少なかったエントリ＝**消さずに残した**。実ページを見て人が判断する。\n')
added_total = 0
touched = 0
rows = []
for i, b in sorted(built.items()):
    e = by.get(i)
    if e is None:
        log.write('!! id%s が index に無い\n' % i)
        continue
    old = e.get('tickets') or []
    have = {key(t) for t in old}
    new = [t for t in b['tickets'] if key(t) not in have]
    only_old = [t for t in old if key(t) not in {key(x) for x in b['tickets']}]
    if len(b['tickets']) < len(old):
        shrink.write('id%-5d %-34s 登録%d枠 / 再導出%d枠 | %s\n'
                     % (i, (e.get('name') or '')[:34], len(old), len(b['tickets']),
                        (e.get('links') or {}).get('pia', '')))
        for t in only_old:
            shrink.write('    登録にだけある枠: %s | %s\n' % (t.get('type'), t.get('date')))
    if not new:
        continue
    touched += 1
    added_total += len(new)
    log.write('== id%-5d %s : 枠 %d → %d\n' % (i, e.get('name', ''), len(old), len(old) + len(new)))
    for t in new:
        log.write('   + %s | %s | %s\n' % (t['type'], t.get('date'), t.get('url') or '-'))
    if APPLY:
        for t in old:
            t.setdefault('url', (e.get('links') or {}).get('pia'))
        e['tickets'] = old + new
        # 日付・会場は「伸びる方向」にだけ更新する（縮める＝情報を失うので触らない）
        if b.get('date') and b['date'] > (e.get('date') or ''):
            e['date'] = b['date']
            if b.get('dateLabel'):
                e['dateLabel'] = b['dateLabel']
            if b.get('venue'):
                e['venue'] = b['venue']
            if b.get('prefecture'):
                e['prefecture'] = b['prefecture']
        e['verifiedAt'] = '2026-08-23'
    rows.append((i, e.get('name', ''), len(old), len(old) + len(new)))

log.write('\n=== 枠が増えたエントリ %d件 / 追加した枠 %d ===\n' % (touched, added_total))
for i, n, a, bn in rows:
    log.write('  id%-5d %-40s %d→%d 枠\n' % (i, n[:40], a, bn))
log.close()
shrink.close()
print('枠が増えたエントリ %d件 / 追加した枠 %d → tmp/merge_diff_0823.txt' % (touched, added_total))
print('※再導出のほうが少なかった分は消さずに tmp/merge_shrink_0823.txt に出した')

if APPLY:
    shutil.copyfile('index.html', 'index.html.bak_0823_merge3')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2)
        + m.group(3) + h[m.end():])
    print('適用した（backup: index.html.bak_0823_merge）')
else:
    print('（差分を見ただけ。適用は --apply）')
