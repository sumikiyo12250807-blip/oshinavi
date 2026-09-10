# -*- coding: utf-8 -*-
"""id7731 海宝直人 に、reconcile_pia が見つけた発売前の枠を足す。

reconcile_pia --new の出力＝
  🚨MISSING ぴあに [発売前] 9/12 11:00発売 (2026-09-16) があるが登録に無い | 「海宝直人」プレリザーブ

会場は単独（市川市文化会館 大ホール／千葉・2027-01-29）なので、どの公演の枠かは迷わない。
発売前の枠は startDate === date === 発売日で書く（[[feedback_entry_template_standard]]）。
2027年公演なので県名のあとは R9年 表記（[[feedback_r9_year_notation]]）。

⏭ もう1件の MISSING（id7753「僕らの時代じゃない」／一般発売 9/13 10:00発売）は
   **京都・愛知の2会場のツアーで、どちらの公演の枠か確定できない**。
   ぴあが混雑ページを返して券種を読めなかったので、次の便で取り直す。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

SLOT = {
    "type": "プレリザーブ（千葉 R9年 1/29公演）9/12 11:00発売",
    "startDate": "2026-09-12",
    "date": "2026-09-12",
    "url": "https://t.pia.jp/pia/event/event.do?eventCd=2635479",
}

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

target = None
for e in events:
    if e['id'] == 7731:
        target = e
        break
if target is None:
    print('!! id7731 が無い')
    sys.exit(1)

print('id7731 %s / 公演%s' % (target.get('name'), target.get('date')))
for t in target.get('tickets') or []:
    print('  いま: %-50s date=%s' % ((t.get('type') or '')[:50], t.get('date')))

if any((t.get('type') or '').startswith('プレリザーブ') for t in target.get('tickets') or []):
    print('  → プレリザーブ枠が既にある。何もしない')
    sys.exit(0)

target.setdefault('tickets', []).append(SLOT)
print('  足した: %s' % SLOT['type'])

out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('書き込み完了')
