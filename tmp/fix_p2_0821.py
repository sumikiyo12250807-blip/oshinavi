# -*- coding: utf-8 -*-
"""新着プールの二重登録・分裂を直す（2026-08-21・part2検証エージェントの指摘）。

🚨① 4851「新日本フィルハーモニー交響楽団 第九 特別演奏会2026」（bundle・5公演）は
   **既存 4778/4779/4780/4781/4782 と完全に重複**（同じ12/16・17・19・20・21）。
   既存側は冠スポンサー名まで入っていて詳しいので、**4851 を落とす**。
② 4845+4846+4847 キユーピー サントリーホール ニューイヤー2027 ＝ 同じ公演の1/1・1/2・1/3 → 1エントリへ
③ 4868+4869 ヒビキpiano ALL CLASSIC TOUR 2026（京都11/14・目黒11/22 FINAL）→ 1エントリへ
④ 4877+4878 KOTOKO LIVE TOUR 2026 "The Bible 2" ＝ 札幌9/12だけ別エントリだった → ツアー本体(4878)へ
⑤ 4890+4891 米倉利紀（福岡12/12・熊本12/13）→ 1エントリへ
⑥ 4849 郷古廉&ホセ・ガヤルド デュオ・リサイタル（紀尾井2/3）＝ 既存 2905（大阪1/29）と同じ来日ツアー → 既存へ
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}


def absorb(keep, drops, venue=None, pref=None, label=None, name=None):
    a = by[keep]
    for t in a['tickets']:
        t.setdefault('url', (a.get('links') or {}).get('pia'))
    seen = {(t.get('type'), t.get('url')) for t in a['tickets']}
    for d in drops:
        b = by[d]
        for t in b['tickets']:
            t = dict(t)
            t.setdefault('url', (b.get('links') or {}).get('pia'))
            if (t.get('type'), t.get('url')) in seen:
                continue
            seen.add((t.get('type'), t.get('url')))
            a['tickets'].append(t)
        a['date'] = max(a['date'], b['date'])
    if name:  a['name'] = a['artist'] = name
    if venue: a['venue'] = venue
    if pref:  a['prefecture'] = pref
    if label: a['dateLabel'] = label
    a['verifiedAt'] = '2026-08-21'
    print('統合 id=%d ← %s ／ 枠%d ／ date=%s ／ %s' % (keep, drops, len(a['tickets']), a['date'], a['name']))


print('① 4851 を落とす（既存4778-4782と完全重複）:', by[4851]['name'], '枠%d' % len(by[4851]['tickets']))
absorb(4845, [4846, 4847], label='2027年1月1日(金)〜2027年1月3日(日) 東京')
absorb(4868, [4869], 'ヒビキpiano ALL CLASSIC TOUR 2026',
       None, None)
by[4868]['name'] = by[4868]['artist'] = 'ヒビキpiano ALL CLASSIC TOUR 2026'
by[4868]['venue'] = '全国ツアー（ロームシアター京都 サウスホール／めぐろパーシモンホール 小ホール）'
by[4868]['prefecture'] = '京都・東京'
by[4868]['dateLabel'] = '2026年11月14日(土)〜2026年11月22日(日) 京都・東京'
absorb(4878, [4877], name='KOTOKO LIVE TOUR 2026 "The Bible 2"')
by[4878]['venue'] = 'ペニーレーン24ほか全国ツアー'
absorb(4890, [4891], '全国ツアー（ROOMS／熊本B.9 V1）', '福岡・熊本',
       '2026年12月12日(土)〜2026年12月13日(日) 福岡・熊本')
absorb(2905, [4849], '全国ツアー（ザ・シンフォニーホール／日本製鉄紀尾井ホール）', '大阪・東京',
       '2027年1月29日(金)〜2027年2月3日(水) 大阪・東京', '郷古廉（vl）&ホセ・ガヤルド（p）')

DROP = {4851, 4846, 4847, 4869, 4877, 4891, 4849}
KEEP = [e for e in EVENTS if e['id'] not in DROP]
assert len(KEEP) == len(EVENTS) - len(DROP)
shutil.copyfile('index.html', 'index.html.bak_0821_p2fix')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 → %d件（欠番 %s） ===' % (len(EVENTS), len(KEEP), sorted(DROP)))
