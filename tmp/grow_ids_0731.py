# -*- coding: utf-8 -*-
"""指定エントリに、指定のぴあURLを足して作り直す（取りこぼし育成の汎用版）。
tools/grow_from_audit.py と同じ流儀:
  上書き = tickets(ぴあ由来) / date(千秋楽) / dateLabel / venue / prefecture
  守る   = artist / name / links / genre / verified と 非ぴあ枠
  安全弁 = 既存のぴあ枠が消える育成は --allow-drop が無い限り適用しない

  python tmp/grow_ids_0731.py --id 3507 --urls b2451557
  python tmp/grow_ids_0731.py --id 3507 --urls b2451557 --apply
（--urls は eventCd / eventBundleCd をカンマ区切り。b で始まればbundle扱い）
"""
import os, re, sys, json, datetime, importlib.util

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)
_OUT = sys.__stdout__
ARGS = sys.argv[1:]


def opt(name):
    if name in ARGS:
        i = ARGS.index(name)
        if i + 1 < len(ARGS) and not ARGS[i + 1].startswith('--'):
            return ARGS[i + 1]
    return None


def say(m):
    _OUT.write(m + '\n'); _OUT.flush()


APPLY = '--apply' in ARGS
ALLOW_DROP = '--allow-drop' in ARGS
EID = int(opt('--id'))
CDS = [c.strip() for c in (opt('--urls') or '').split(',') if c.strip()]
if not CDS:
    say('!! --urls が空'); sys.exit(1)


def cd_url(cd):
    key = 'eventBundleCd' if cd.startswith('b') else 'eventCd'
    return 'https://t.pia.jp/pia/event/event.do?%s=%s' % (key, cd)


def is_pia_ticket(t):
    u = t.get('url') or ''
    return (not u) or ('pia.jp' in u)


def perf_key(type_):
    m = re.search(r'[（(]([^（）()]*公演[^（）()]*)[）)]', type_ or '')
    return m.group(1).strip() if m else (type_ or '').strip()


s = importlib.util.spec_from_file_location('bpe', os.path.join(TOOLS, 'build_pia_entries.py'))
bpe = importlib.util.module_from_spec(s); s.loader.exec_module(bpe)

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
nnew = 0
for cd in CDS:
    u = cd_url(cd)
    if u not in urls:
        urls.append(u); nnew += 1

say('id=%d  ぴあURL %d本（既存%d + 新規%d）' % (EID, len(urls), len(urls) - nnew, nnew))
ne = bpe.build({'newid': EID, 'artist': ev.get('artist', ''), 'urls': urls})
if ne is None:
    say('🚨 買える枠ゼロで返ってきた＝置換しない'); sys.exit(1)

kept = [t for t in cur if not is_pia_ticket(t)]
newt = list(ne['tickets']) + kept
nd = max([d for d in (ne.get('date'), ev.get('date')) if d])

L = []
L.append('枠 %d → %d（非ぴあ据置 %d）' % (len(cur), len(newt), len(kept)))
L.append('千秋楽 %s → %s' % (ev.get('date'), nd))
L.append('会場 %s' % (ev.get('venue') or ''))
L.append('  →  %s' % (ne.get('venue') or ''))
L.append('県   %s → %s' % (ev.get('prefecture'), ne.get('prefecture')))
L.append('日付 %s' % (ev.get('dateLabel') or ''))
L.append('  →  %s' % (ne.get('dateLabel') or ''))
L.append('--- 今の枠 ---')
for t in cur:
    L.append('  %s | date=%s start=%s' % (t.get('type'), t.get('date'), t.get('startDate')))
L.append('--- 作り直した枠 ---')
for t in ne['tickets']:
    L.append('  %s | date=%s start=%s' % (t.get('type'), t.get('date'), t.get('startDate')))

newk = {perf_key(t.get('type')) for t in ne['tickets']}
lost = [t for t in cur if is_pia_ticket(t) and perf_key(t.get('type')) not in newk]
if lost:
    L.append('🚨 消えるぴあ枠 %d件:' % len(lost))
    for t in lost:
        L.append('   × %s | date=%s' % (t.get('type'), t.get('date')))

outp = 'tmp/grow_%d_0731.txt' % EID
open(outp, 'w', encoding='utf-8').write('\n'.join(L))
say('差分は %s' % outp)

if lost and not ALLOW_DROP:
    say('→ 枠が消えるので自動適用しない（見てから --allow-drop）'); sys.exit(0)
if not APPLY:
    say('(ドライラン。適用は --apply)'); sys.exit(0)

ev['tickets'] = newt
ev['date'] = nd
for k, v in (('dateLabel', ne.get('dateLabel')), ('venue', ne.get('venue')), ('prefecture', ne.get('prefecture'))):
    if v:
        ev[k] = v
ev['verifiedAt'] = datetime.date.today().isoformat()

bak = os.path.join(ROOT, 'index.html.bak_%s_grow%d' % (datetime.date.today().strftime('%m%d'), EID))
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open(idx, 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
raw = open(idx, 'rb').read()
say('=== 適用 (backup: %s) / 孤立LF=%d ===' % (os.path.basename(bak), raw.count(b'\n') - raw.count(b'\r\n')))
