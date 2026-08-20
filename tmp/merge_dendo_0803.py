# -*- coding: utf-8 -*-
"""中田カウス 漫才のDENDO 全国ツアーを1エントリに統合する（ユーザー指示 2026-08-03）。
 ・残す＝既存id1098（レビュー済み） / 消す＝新着id3640（同じツアーの三重公演）
 ・ぴあ4公演（富山10/4・三重10/3・山形8/22・大阪8/23）を build_pia_entries で作り直して差し替え
 ・名前は「in 富山」を外してツアー名にする（4会場になるので会場名入りの名前は嘘になる）
memory: feedback_tour_consolidate / feedback_harvest_dedup_check(既存を残し新着を消す)
        feedback_index_html_crlf_preserve(CRLF維持) / feedback_new_order_array
使い方: python tmp/merge_dendo_0803.py [--apply]
"""
import re, io, json, sys, subprocess, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

APPLY = '--apply' in sys.argv
KEEP, DROP = 1098, 3640
NEW_NAME = '中田カウス 漫才のDENDO 全国ツアー 2026'
URLS = [
    'https://t.pia.jp/pia/event/event.do?eventCd=2620946',   # 富山 10/4
    'https://t.pia.jp/pia/event/event.do?eventCd=2621795',   # 三重 10/3
    'https://t.pia.jp/pia/event/event.do?eventCd=2614357',   # 山形(米沢) 8/22
    'https://t.pia.jp/pia/event/event.do?eventCd=2613761',   # 大阪(富田林) 8/23
]

json.dump([{'newid': KEEP, 'artist': NEW_NAME, 'urls': URLS}],
          io.open('tmp/cand_dendo.json', 'w', encoding='utf-8'), ensure_ascii=False)
r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', 'tmp/cand_dendo.json'],
                   capture_output=True)
built = json.loads(r.stdout.decode('utf-8'))
assert len(built) == 1, '構築失敗 %s' % r.stderr.decode('utf-8', 'replace')[:300]
b = built[0]

# 🚨富山10/4はぴあが受付終了だが e+ で受付中（〜10/3 18:00・実ページ確認済み）。
# 「ぴあで0枠＝消す」をやると買える枠を殺す（memory: feedback_delete_nonpia_blindspot）。
# build()はぴあ枠しか作らないので、e+枠は手で足して守る。
EPLUS_URL = 'https://eplus.jp/sf/detail/0981850002-P0030038P021001'
EPLUS_T = {'type': '一般発売（富山 10/4公演）〜10/3 18:00', 'date': '2026-10-03', 'url': EPLUS_URL}
b['tickets'] = sorted(b['tickets'] + [EPLUS_T], key=lambda t: t['date'])
b['date'] = '2026-10-04'                      # 千秋楽=富山(まだ買える)。古いままだとカードが早く消える
b['venue'] = b['venue'].rstrip('）') + '／富山県民会館 ホール）'
b['prefecture'] = b['prefecture'] + '・富山'
b['dateLabel'] = re.sub(r'〜2026年10月3日\(土\).*$', '〜2026年10月4日(日) ' + b['prefecture'], b['dateLabel'])

h = io.open('index.html', encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

keep = next(e for e in EVENTS if e['id'] == KEEP)
drop = next(e for e in EVENTS if e['id'] == DROP)
print('--- 統合前 ---')
print('  残す id%d %s / 枠%d / %s' % (keep['id'], keep['name'][:34], len(keep['tickets']), keep['prefecture']))
print('  消す id%d %s / 枠%d / %s' % (drop['id'], drop['name'][:34], len(drop['tickets']), drop['prefecture']))
print('--- 作り直した中身 ---')
print('  name      %s' % NEW_NAME)
print('  date      %s → %s' % (keep['date'], b['date']))
print('  dateLabel %s' % b['dateLabel'])
print('  venue     %s' % b['venue'])
print('  pref      %s → %s' % (keep['prefecture'], b['prefecture']))
for t in b['tickets']:
    print('   - %s | date=%s start=%s' % (t['type'], t['date'], t.get('startDate')))

if not APPLY:
    print('\n=== 表示のみ。適用は --apply ===')
    sys.exit(0)

# 人が決めた項目は守り、ぴあ由来だけ差し替える（grow_from_audit と同じ流儀）
keep['artist'] = NEW_NAME
keep['name'] = NEW_NAME
for k in ('tickets', 'date', 'dateLabel', 'venue', 'prefecture'):
    keep[k] = b[k]
keep['links']['pia'] = b['links']['pia']
keep['links']['eplus'] = EPLUS_URL
keep['verifiedAt'] = datetime.date.today().isoformat()

EVENTS = [e for e in EVENTS if e['id'] != DROP]

mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', h)
ids = [int(x) for x in re.findall(r'\d+', mo.group(2)) if int(x) != DROP]
h2 = re.sub(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]',
            lambda mm: mm.group(1) + '[' + ', '.join(str(i) for i in ids) + ']', h, count=1)
m2 = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h2, re.S)

bak = 'index.html.bak_0803_merge_dendo'
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h2[:m2.start()] + m2.group(1) + arr + m2.group(3) + h2[m2.end():])
print('\n適用: 総%d件 / NEW_ORDER %d件 / backup %s' % (len(EVENTS), len(ids), bak))
