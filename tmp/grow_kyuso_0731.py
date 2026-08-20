# -*- coding: utf-8 -*-
"""キュウソネコカミ(id3475)の取りこぼし育成。
ユーザー指摘＋tools/pia_kw_search.py の総ざらいで、登録が北海道公演1本だけなのに対し
ぴあにはキュウソネコカミ名義の単独公演が7本あることが判明。既存URL＋未登録6本で作り直す。

やり方は tools/grow_from_audit.py と同じ流儀:
  上書き = tickets(ぴあ由来) / date(千秋楽) / dateLabel / venue / prefecture
  守る   = artist / name / links / genre / verified と 非ぴあ枠
  安全弁 = 既存のぴあ枠が消える育成は --allow-drop が無い限り適用しない

  python tmp/grow_kyuso_0731.py            # ドライラン（差分を出す）
  python tmp/grow_kyuso_0731.py --apply
"""
import os, re, sys, json, datetime, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)
_REAL_OUT = sys.__stdout__

ARGS = sys.argv[1:]
APPLY = '--apply' in ARGS
ALLOW_DROP = '--allow-drop' in ARGS
EID = 3475

BASE = 'https://t.pia.jp/pia/event/event.do?eventCd='
NEW_CDS = [
    ('2612708', '岩手10/23・宮城10/25・秋田10/30'),
    ('2627362', '新潟11/18'),
    ('2627363', '石川11/20'),
    ('2626502', '京都9/23 磔磔'),
    ('2628908', '静岡 R9年1/16'),
    ('2627249', '高知 R9年1/30'),
]


def say(m):
    _REAL_OUT.write(m + '\n'); _REAL_OUT.flush()


def _load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, fname))
    mod = importlib.util.module_from_spec(s)
    s.loader.exec_module(mod)
    return mod


def is_pia_ticket(t):
    u = t.get('url') or ''
    return (not u) or ('pia.jp' in u)


def perf_key(type_):
    m = re.search(r'[（(]([^（）()]*公演[^（）()]*)[）)]', type_ or '')
    return m.group(1).strip() if m else (type_ or '').strip()


bpe = _load('bpe', 'build_pia_entries.py')

idx = os.path.join(ROOT, 'index.html')
h = open(idx, encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
ev = next(e for e in EVENTS if e['id'] == EID)

cur = ev.get('tickets') or []
urls = []
p = (ev.get('links') or {}).get('pia')
if p:
    urls.append(p)
for t in cur:
    if t.get('url') and 'pia' in t['url'] and t['url'] not in urls:
        urls.append(t['url'])
for cd, _ in NEW_CDS:
    u = BASE + cd
    if u not in urls:
        urls.append(u)

say('ぴあURL %d本（既存%d + 新規%d）' % (len(urls), len(urls) - len(NEW_CDS), len(NEW_CDS)))
ne = bpe.build({'newid': EID, 'artist': ev.get('artist', ''), 'urls': urls})
if ne is None:
    say('🚨 買える枠ゼロで返ってきた＝置換しない'); sys.exit(1)

kept = [t for t in cur if not is_pia_ticket(t)]
newt = list(ne['tickets']) + kept
nd = max([d for d in (ne.get('date'), ev.get('date')) if d])

lines = []
lines.append('枠 %d → %d（非ぴあ据置 %d）' % (len(cur), len(newt), len(kept)))
lines.append('千秋楽 %s → %s' % (ev.get('date'), nd))
lines.append('会場 %s' % (ev.get('venue') or ''))
lines.append('  →  %s' % (ne.get('venue') or ''))
lines.append('県   %s → %s' % (ev.get('prefecture'), ne.get('prefecture')))
lines.append('日付 %s' % (ev.get('dateLabel') or ''))
lines.append('  →  %s' % (ne.get('dateLabel') or ''))
lines.append('--- 今の枠 ---')
for t in cur:
    lines.append('  %s | date=%s start=%s' % (t.get('type'), t.get('date'), t.get('startDate')))
lines.append('--- 作り直した枠 ---')
for t in ne['tickets']:
    lines.append('  %s | date=%s start=%s' % (t.get('type'), t.get('date'), t.get('startDate')))

newk = {perf_key(t.get('type')) for t in ne['tickets']}
lost = [t for t in cur if is_pia_ticket(t) and perf_key(t.get('type')) not in newk]
if lost:
    lines.append('🚨 消えるぴあ枠 %d件:' % len(lost))
    for t in lost:
        lines.append('   × %s | date=%s' % (t.get('type'), t.get('date')))

open('tmp/grow_kyuso_0731.txt', 'w', encoding='utf-8').write('\n'.join(lines))
say('差分は tmp/grow_kyuso_0731.txt')

if lost and not ALLOW_DROP:
    say('→ 枠が消えるので自動適用しない（見てから --allow-drop）'); sys.exit(0)
if not APPLY:
    say('(ドライラン。適用は --apply)'); sys.exit(0)

ev['tickets'] = newt
ev['date'] = nd
if ne.get('dateLabel'):
    ev['dateLabel'] = ne['dateLabel']
if ne.get('venue'):
    ev['venue'] = ne['venue']
if ne.get('prefecture'):
    ev['prefecture'] = ne['prefecture']
ev['verifiedAt'] = datetime.date.today().isoformat()

bak = os.path.join(ROOT, 'index.html.bak_%s_grow_kyuso' % datetime.date.today().strftime('%m%d'))
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open(idx, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
raw = open(idx, 'rb').read()
say('=== 適用 (backup: %s) / 孤立LF=%d ===' % (os.path.basename(bak), raw.count(b'\n') - raw.count(b'\r\n')))
