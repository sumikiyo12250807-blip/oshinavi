# -*- coding: utf-8 -*-
"""id4538 Juice=Juice の販売枠を実態に合わせて7枠に直す（ユーザー指摘の取りこぼし）。

何が起きていたか＝ぴあは6本の抽選先行（lotRlsCd が全部別）を出しているのに、
build_pia_entries が券種名と昼/夜を落として全部「先行（神奈川 9/18公演）」「（9/19公演）」に
潰した。その結果 dedup_badges が重複と見なして畳み、3枠しか残らなかった。

公演時刻は会場公式で裏取り（[[feedback_same_day_show_time_badge]]＝同一会場・同日で時間違いの
複数公演はバッジに開演時刻を入れる。昼/夜の語だけに頼らない）:
  厚木市文化会館 公式 https://atsugi-bunka.jp/events/shusaijigyo/2026/09_18_1674.php
  「9/18(金) 19：00 ・9/19(土) ①13：45 ②17:15 / 大ホール」
  音楽ナタリー/ハロプロ公式の記載とも一致。

⚠️ticket.url は付けない（event ページのまま）。ticketInformation.do?rlsCd= 形を url に入れると
   reconcile が「0枠」と誤読する罠がある（[[feedback_reconcile_rlscd_false_zero]]）。
   バッジは links.pia のイベントページに飛び、そこに6枠とも並んでいる。

🚨CRLF保持（[[feedback_index_html_crlf_preserve]]）。

  python tmp/fix_4538_slots_0817.py [--apply]
"""
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
EID = 4538

TICKETS = [
    ('先行（神奈川 9/18 19:00公演）〜8/20 23:59', '2026-08-20', None),
    ('ODYSSEY WEB会員先行（神奈川 9/18 19:00公演）〜8/20 23:59', '2026-08-20', None),
    ('先行（神奈川 9/19 13:45公演）〜8/20 23:59', '2026-08-20', None),
    ('ODYSSEY WEB会員先行（神奈川 9/19 13:45公演）〜8/20 23:59', '2026-08-20', None),
    ('先行（神奈川 9/19 17:15公演）〜8/20 23:59', '2026-08-20', None),
    ('ODYSSEY WEB会員先行（神奈川 9/19 17:15公演）〜8/20 23:59', '2026-08-20', None),
    ('一般発売（神奈川 9/18〜9/19公演）8/29 10:00発売', '2026-08-29', '2026-08-29'),
]

src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
BLOCK = re.compile(r'  \{\r\n    "id": (\d+),.*?\r\n  \},?', re.S)
m = {int(x.group(1)): x for x in BLOCK.finditer(src)}[EID]
e = json.loads(m.group(0).rstrip(',').strip())

print('=== 直す前 %d枠 ===' % len(e.get('tickets') or []))
for t in e.get('tickets') or []:
    print('   %s' % t.get('type'))

new = []
for ty, dt, sd in TICKETS:
    o = {'type': ty, 'date': dt}
    if sd:
        o['startDate'] = sd
    new.append(o)
e['tickets'] = new


def dump_entry(obj):
    body = json.dumps(obj, ensure_ascii=False, indent=2)
    body = '\n'.join(('  ' + ln) if ln else ln for ln in body.split('\n'))
    return body.replace('\n', '\r\n')


src = src[:m.start()] + dump_entry(e) + (',' if m.group(0).endswith(',') else '') + src[m.end():]

print()
print('=== 直した後 %d枠 ===' % len(new))
for t in new:
    print('   %s' % t['type'])

EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S).group(2))
chk = [x for x in EV if x['id'] == EID][0]
print()
print('総件数 %d / id%d の枠 %d本 / バッジ文言のユニーク %d'
      % (len(EV), EID, len(chk['tickets']), len({t['type'] for t in chk['tickets']})))
print('CRLF %d → %d ／ LF単独 %d' % (before_crlf, src.count('\r\n'), src.count('\n') - src.count('\r\n')))

if APPLY:
    io.open('index.html.bak_0817_fix4538', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました（backup: index.html.bak_0817_fix4538）')
else:
    print('（判定のみ。適用するなら --apply）')
