# -*- coding: utf-8 -*-
"""新着の読み直しで見つかった取りこぼし・売り切れを3件に当てる（2026-09-16 朝）。
根拠＝別エージェントがぴあの実ページからゼロで読んだ結果（scratchpad/recheck_*_result.json）。
  8544 カズキのタネ＝東京 11/7 TOKYO FMホール（2626223 rlsCd=004）が予定枚数終了で抜けていた → 印付きで足す・会期 11/7 まで・県に東京
  8573 ガクテンソク＝大阪 10/18 なんばグランド花月（別ページ 2615687）が予定枚数終了で抜けていた → 印付きで足す・会期 10/18 まで・5県＝全国
  9946 CUTIE STREET＝当日引換券（神奈川 9/23・横浜アリーナ）が予定枚数終了 → その枠に売り切れの印
売り切れは消さない決まり（DELETE_GATE 1.）。
使い方: python tmp/fix_new3_0916.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
TODAY = '2026-09-16'
U = 'https://t.pia.jp/pia/event/event.do?eventCd=%s'


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
ev = events(text)
by = {e['id']: e for e in ev}
new = {}

e = json.loads(json.dumps(by[8544], ensure_ascii=False))
assert e['date'] == '2026-10-12' and len(e['tickets']) == 2
e['tickets'].append({'type': '一般発売（東京 11/7公演）', 'date': '2026-11-07', 'url': U % '2626223',
                     'soldout': True, 'soldoutSince': TODAY})
e['date'] = '2026-11-07'
e['dateLabel'] = '2026年10月2日(金)〜2026年11月7日(土) 神奈川・東京'
e['venue'] = '全国ツアー（茅ヶ崎市民文化会館 小ホール／茅ヶ崎市総合体育館 第2体育室／TOKYO FMホール）'
e['prefecture'] = '神奈川・東京'
new[8544] = e

e = json.loads(json.dumps(by[8573], ensure_ascii=False))
assert e['date'] == '2026-09-25' and len(e['tickets']) == 1
e['tickets'].append({'type': '一般発売（大阪 10/18公演）', 'date': '2026-10-18', 'url': U % '2615687',
                     'soldout': True, 'soldoutSince': TODAY})
e['date'] = '2026-10-18'
e['dateLabel'] = '2026年7月8日(水)〜2026年10月18日(日) 全国ツアー'
e['venue'] = '全国ツアー（電力ホール／有楽町よみうりホール／倉敷市芸文館ホール／レクザムホール 小ホール／なんばグランド花月）'
e['prefecture'] = '全国'
new[8573] = e

e = json.loads(json.dumps(by[9946], ensure_ascii=False))
hit = [t for t in e['tickets'] if t['type'] == '当日引換券発売（神奈川 9/23公演）〜9/22 23:59']
assert len(hit) == 1 and not hit[0].get('soldout')
hit[0]['soldout'] = True
hit[0]['soldoutSince'] = TODAY
new[9946] = e

lines = text.split('\r\n')
out, i, hits = [], 0, 0
while i < len(lines):
    m = re.fullmatch(r'    "id": (\d+),', lines[i + 1]) if lines[i] == '  {' and i + 1 < len(lines) else None
    if m and int(m.group(1)) in new:
        j = i
        while not lines[j].startswith('  }'):
            j += 1
        tail = lines[j][3:]  # 「,」があれば残す
        block = ['  ' + ln for ln in json.dumps(new[int(m.group(1))], ensure_ascii=False, indent=2).split('\n')]
        block[-1] += tail
        out += block
        hits += 1
        i = j + 1
        continue
    out.append(lines[i])
    i += 1
assert hits == 3, hits
res = '\r\n'.join(out)
ev2 = events(res)
a = {x['id']: json.dumps(x, ensure_ascii=False, sort_keys=True) for x in ev2 if x['id'] not in new}
b = {x['id']: json.dumps(x, ensure_ascii=False, sort_keys=True) for x in ev if x['id'] not in new}
assert a == b and len(ev2) == len(ev), 'ほかのエントリが変わった'
assert '\n' not in res.replace('\r\n', ''), '素のLFが混ざった'
for k in new:
    g = next(x for x in ev2 if x['id'] == k)
    print('id%d 会期 %s／県 %s／枠 %d（うち売り切れの印 %d）' % (k, g['dateLabel'], g['prefecture'], len(g['tickets']),
                                                  sum(1 for t in g['tickets'] if t.get('soldout'))))
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_fixnew3')
    with open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(res)
    print('書き込んだ（予備 index.html.bak_0916_fixnew3）')
else:
    print('（調べるだけ。--apply で書き込み）')
