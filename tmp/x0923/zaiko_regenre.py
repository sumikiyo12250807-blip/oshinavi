# -*- coding: utf-8 -*-
"""新着プールに残るZAIKOエントリのジャンルを、直したハーベスタで取り直す（2026-09-23 夜）。

背景＝`zaiko_harvest.py` がイベント側ジャンル（`{"data":[...]}`）を1件も読めておらず、
売り場が Idol と言っている17件が musicetc（その他）に落ちていた。
ハーベスタと `genres_of` の順番を直したので、実ページから引き直して `_genre` を入れ替える。

🚨ジャンルだけを触る。枠（tickets）・日付・URLには指1本触れない。
使い方: python tmp/x0923/zaiko_regenre.py [--apply]
"""
import collections
import importlib.util
import io
import json
import re
import sys
import time

APPLY = '--apply' in sys.argv


# 🚨読み込む道具が中で sys.stdout を差し替える。古いラッパーがGCされると下のbufferまで
#    閉じてしまうので、**握っておく**（reference_tiget_harvest の罠8と同じ）。
_KEEP = []


def _load(path, name):
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


ZH = _load('tools/zaiko_harvest.py', 'zh')
BZ = _load('tools/build_zaiko_entries.py', 'bz')

text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)

targets = [e for e in events if e.get('genre') == 'new' and (e.get('links') or {}).get('zaiko')]
unknown = collections.Counter()
log, changed, same, err = [], 0, 0, 0
for e in targets:
    url = e['links']['zaiko']
    html = ZH.fetch(url)
    if not html:
        err += 1
        log.append('%s\tFETCH_ERR\t\t\t%s' % (e['id'], url))
        continue
    det = ZH.parse_event(html, url)
    if not det:
        err += 1
        log.append('%s\tPARSE_ERR\t\t\t%s' % (e['id'], url))
        continue
    # 🚨一覧のカテゴリ（performances-shows など）はエントリに残っていない＝ここでは渡せない。
    #    ジャンル欄が空の件は**触らない**（投入時にカテゴリで決めた値をそのまま残す）。
    #    触ると 20940 OSK日本歌劇団のような engeki が その他 に退化する。
    gs = BZ.genres_of(det, unknown, None)
    old = e.get('_genre')
    if not gs:
        same += 1
        log.append('%s\t(据え置き)\t%s\t%s\t%s' % (e['id'], old, '|'.join(det.get('genres') or []),
                                                 (e.get('name') or e.get('artist') or '')))
        time.sleep(0.6)
        continue
    e['_genre'] = gs[0]
    e['_srcgenre'] = 'zaiko:%s' % (','.join(det.get('genres') or []) or '?')
    if len(gs) > 1:
        e['_extraGenres'] = gs[1:]
    if gs[0] != old:
        changed += 1
    else:
        same += 1
    log.append('%s\t%s\t%s\t%s\t%s' % (e['id'], gs[0], old,
                                       '|'.join(det.get('genres') or []),
                                       (e.get('name') or e.get('artist') or '')))
    time.sleep(0.6)

rep = io.open('tmp/x0923/zaiko_regenre.txt', 'w', encoding='utf-8')
rep.write('ZAIKO 取り直し %d件（変わった %d / 同じ %d / 読めず %d）\n' % (len(targets), changed, same, err))
if unknown:
    rep.write('\n== 対応表に無いジャンル（写さず数えた）==\n')
    for k, c in unknown.most_common():
        rep.write('  %-24s %4d\n' % (k, c))
rep.write('\n== 明細（id / 新 / 旧 / 売り場のイベント側ジャンル / 公演名）==\n')
rep.write('\n'.join(log) + '\n')
rep.close()

sys.stdout.write('targets=%d changed=%d same=%d err=%d unknown=%d\n'
                 % (len(targets), changed, same, err, len(unknown)))
sys.stdout.write('report: tmp/x0923/zaiko_regenre.txt\n')

if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)

body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
data = (text[:start] + body + text[end:]).encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open('index.html', 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
