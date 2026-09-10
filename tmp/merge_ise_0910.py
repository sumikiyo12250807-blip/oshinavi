# -*- coding: utf-8 -*-
"""伊勢正三の2エントリを1つにまとめる（ユーザー指示 2026-09-10「伊勢正三 ひとつにまとめて」）。

■ いまの状態＝**同じ公演が二重登録**（[[feedback_tour_individual_url_dup]]）
  id2317 伊勢正三（全国ツアー 8/29〜11/7）
     - 一般発売（福島・長野 10/10〜10/12公演）〜10/9 23:59   url=eventCd=2624009
     - 一般発売（東京 11/7公演）〜11/6 23:59                url=eventCd=2627801
  id4503 伊勢正三（東京 11/7 かつしかシンフォニーヒルズ 単独）
     - 一般発売（東京 11/7公演）〜11/6 23:59                url=なし（links.pia=b2670023）

■ 実測（2026-09-10・ぴあの実ページ）
  eventCd=2627801        … [受付中] 2026-11-07 東京都 かつしかシンフォニーヒルズ 一般発売 〜11/6 23:59
  eventBundleCd=b2670023 … [受付中] **まったく同じ枠**（bundleは個別ページのまとめ）
  ＝どちらも生きていて、指しているものが同じ。だから畳んでよい
  （[[feedback_dedup_badges_keeps_urls]]＝飛び先が違っても**中身が同じ**なら二重に出す意味がない）。

■ やること
  ① id2317 の東京枠はそのまま（url=eventCd=2627801＝個別ページのほうが正確）
  ② id4503 を削除。消えるURL（b2670023）は logs に残す
  ③ id2317 の venue から「福岡サンパレス ホテル&ホール」は**外さない**
     ＝ぴあに枠が無いだけで、公演が無かったとは言えない（[[feedback_show_true_dates_not_sellable_range]]）
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DROP = 4503
KEEP = 2317

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

keep = next((e for e in events if e['id'] == KEEP), None)
drop = next((e for e in events if e['id'] == DROP), None)
if keep is None or drop is None:
    print('!! 対象が見つからない（keep=%s drop=%s）' % (bool(keep), bool(drop)))
    sys.exit(1)

print('残す  id%-5d %s' % (KEEP, keep.get('dateLabel')))
for t in keep.get('tickets') or []:
    print('   - %-50s url=%s' % ((t.get('type') or '')[:50], (t.get('url') or '')[:60]))
print('消す  id%-5d %s' % (DROP, drop.get('dateLabel')))
for t in drop.get('tickets') or []:
    print('   - %-50s url=%s' % ((t.get('type') or '')[:50], (t.get('url') or '(なし)')[:60]))

# 消すほうにしか無い枠が無いかを機械で確かめる（券種名でなく「県・公演日・締切」で見る）
def key(t):
    ty = t.get('type') or ''
    pref = (re.search(r'（([^）0-9]+?)\s*(?:R\d+年\s*)?\d{1,2}/\d{1,2}', ty) or [None, ''])[1]
    show = (re.search(r'((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜\d{1,2}/\d{1,2})?)公演', ty) or [None, ''])[1]
    return (pref.strip(), show.strip(), t.get('date'))

kk = {key(t) for t in keep.get('tickets') or []}
lost = [t for t in drop.get('tickets') or [] if key(t) not in kk]
print('')
if lost:
    print('🚨 消すほうにしか無い枠が %d件ある＝畳む前に足す' % len(lost))
    for t in lost:
        print('   - %s' % t.get('type'))
        keep.setdefault('tickets', []).append(t)
else:
    print('✅ 消すほうの枠は全部 残すほうにある（県・公演日・締切で照合）')

events = [e for e in events if e['id'] != DROP]
print('EVENTS %d → %d' % (len(events) + 1, len(events)))

out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

# NEW_ORDER にいたら外す
mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', out, re.S)
arr = json.loads(mo.group(2))
if DROP in arr:
    arr2 = [i for i in arr if i != DROP]
    print('NEW_ORDER %d → %d' % (len(arr), len(arr2)))
    out = out[:mo.start()] + mo.group(1) + json.dumps(arr2) + mo.group(3) + out[mo.end():]
else:
    print('NEW_ORDER には入っていない（genre=%s）' % drop.get('genre'))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

io.open('index.html', 'w', encoding='utf-8').write(out)

# 消したものを logs に残す（[[feedback_user_confirms_expired]]）
today = datetime.date.today().isoformat()
log = 'logs/removed_%s.md' % today
line = ('\n## 伊勢正三 id4503（統合のため削除・2026-09-10）\n\n'
        '- 公演＝2026年11月7日(土) かつしかシンフォニーヒルズ モーツァルトホール（東京）\n'
        '- **id2317（全国ツアー）に同じ公演の枠があるので畳んだ**（ユーザー指示「伊勢正三 ひとつにまとめて」）\n'
        '- 消えたURL＝https://ticket.pia.jp/pia/event.do?eventBundleCd=b2670023\n'
        '  （id2317 側は https://t.pia.jp/pia/event/event.do?eventCd=2627801 ＝'
        'どちらもぴあの実ページで同じ枠を指しているのを確認済み）\n')
try:
    old = io.open(log, encoding='utf-8').read()
except FileNotFoundError:
    old = '# %s に消したもの\n' % today
io.open(log, 'w', encoding='utf-8').write(old.rstrip('\n') + '\n' + line)
print('書き込み完了 / %s に記録' % log)
