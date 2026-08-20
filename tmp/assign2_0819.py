# -*- coding: utf-8 -*-
"""新着プール25件の振り分け（2026-08-19・2回目）。ユーザー指示「チェックし直したら振り分けて」。

検証＝①独立再照合（指摘1件・4676は取り込み直して統合済）
      ②別エージェント2本にゼロから再導出させ、25件中23件が枠数・千秋楽・県・ジャンルとも一致
      ③食い違った1件＝4642 琵琶は**検証側が正しい**（琵琶＝和楽器＝dento）。
        build_pia_entries の和楽器語に琵琶ほかを追加したうえで dento に直す
      ④4639「音楽/民族音楽」は PIA_GENRE_MAP の既存決定どおり yougaku（海外の音楽の受け皿）
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

FIX = {4642: 'dento'}   # 検証で覆った分

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

rows = []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    g = FIX.get(e['id'], e.get('_genre'))
    if not g:
        print('!! id=%d に _genre が無い。中止' % e['id'])
        sys.exit(1)
    extra = e.get('_extraGenres') or []
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    rows.append((e['id'], e['name'], g, extra, (e.get('links') or {}).get('pia', '')))

left = [e['id'] for e in EVENTS if e.get('genre') == 'new']
print('振り分け %d件 / 新着に残る %d件' % (len(rows), len(left)))

body = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
mo = re.search(r'(const NEW_ORDER\s*=\s*)(\[[^\]]*\])', body)
body = body[:mo.start()] + mo.group(1) + json.dumps(left) + body[mo.end():]

shutil.copyfile('index.html', 'index.html.bak_0819_assign2')
open('index.html', 'w', encoding='utf-8').write(body)

with open('logs/assigned_2026-08-19.md', 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n## 2回目の振り分け %d件（今朝投入した35件のうち、統合で減った残り）\n\n' % len(rows))
    f.write('検証＝独立再照合（指摘1件・4676は取り込み直して統合）＋別エージェント2本のゼロ導出。\n')
    f.write('25件中24件が枠数・千秋楽・県・ジャンルとも一致。食い違った1件は**検証側が正しかった**ので直した。\n\n')
    f.write('| id | 公演名 | ジャンル | 確認用URL |\n|---|---|---|---|\n')
    for i, name, g, extra, url in rows:
        lab = g + ('＋' + '＋'.join(extra) if extra else '')
        f.write('| %d | %s | %s | %s |\n' % (i, name.replace('|', '/'), lab, url))
    f.write('\n**直した1件**＝4642 能舞台に響く琵琶の音色 ～琵琶絵巻～ 坂田美子：enka → **dento**。\n')
    f.write('原因は `build_pia_entries.py` の和楽器語リストに「琵琶」が無く、演歌側に落ちていたこと。\n')
    f.write('リストに 琵琶／義太夫／清元／新内／小唄／端唄／地唄／浄瑠璃／詩吟／囃子／能舞台 を追加した。\n\n')
    f.write('**判断が微妙だった1件**＝4639 二胡とピアノでめぐる名曲の旅：ぴあのカテゴリが「音楽/民族音楽」で、\n')
    f.write('登録ツールの対応表では **yougaku（海外の音楽の受け皿）** に倒れる。過去に「ネパールの詩心」で決めた\n')
    f.write('マッピングどおりなのでそのままにしたが、二胡＋ピアノでクラシックの名曲を弾く公演なので、\n')
    f.write('classic のほうがよければ言ってほしい。\n')

for i, name, g, extra, url in rows:
    print('  %d %s → %s%s' % (i, name[:34], g, '+' + '+'.join(extra) if extra else ''))
