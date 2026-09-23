# 公式との食い違い2件を直す（出典＝tmp/x0920/facts_main.md）
#  11172 A.B.C-Z＝明日発売2枠に公式が案内するぴあの入口／愛知の会場名を公式表記に
#  96 劇団四季『バック・トゥ・ザ・フューチャー』＝会期の始まりを公式の開幕日 2025年4月6日(日) に
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
e = by[11172]
e['venue'] = e['venue'].replace('刈谷市総合文化センター アイリス 大ホール', '刈谷市総合文化センター 大ホール')
for t in e['tickets']:
    if t.get('startDate') == '2026-09-20' and not t.get('url'):
        t['url'] = 'https://w.pia.jp/a/abcz26ip-oa/'
e = by[96]
e['dateLabel'] = e['dateLabel'].replace('2026年1月3日(土)', '2025年4月6日(日)')
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print(by[11172]['venue'], '|', by[96]['dateLabel'])
