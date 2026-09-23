# -*- coding: utf-8 -*-
"""9/20 朝：check_expired が出した「公演終了済」の削除候補を仕分ける（読むだけ）。

区分:
  keep_stream … 配信など、公演は終わったが買える枠が生きている（📺）＝消さない
  keep_manual … ユーザーが「残す」と決めたもの（id3683 ムビチケ）
  del_ok      … 公演日が過去で、生きている枠も無い＝削除候補
出力: tmp/x0920/del_ids.txt（カンマ区切り）／tmp/x0920/del_list.md
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
KEEP_MANUAL = {3683}

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '9999') < TODAY)


del_ok, keep_stream, keep_manual, keep_future = [], [], [], []
for e in events:
    d = e.get('date') or ''
    if not d or d >= TODAY:
        continue
    if e.get('genre') == 'new':
        continue          # 新着プールは触らない
    alive = [t for t in (e.get('tickets') or []) if visible(t) and not t.get('soldout')
             and not t.get('saleEnded') and (t.get('date') or '') >= TODAY]
    row = (e['id'], (e.get('artist') or e.get('name') or '')[:60], d,
           (e.get('links') or {}).get('pia') or (e.get('links') or {}).get('eplus')
           or (e.get('links') or {}).get('rakuten') or '')
    if e['id'] in KEEP_MANUAL:
        keep_manual.append(row)
    elif alive:
        keep_stream.append(row + (len(alive),))
    else:
        del_ok.append(row)

io.open('tmp/x0920/del_ids.txt', 'w', encoding='utf-8').write(
    ','.join(str(r[0]) for r in del_ok))
with io.open('tmp/x0920/del_list.md', 'w', encoding='utf-8') as f:
    f.write('# %s 公演が終わった削除候補 %d件\n\n' % (TODAY, len(del_ok)))
    for i, n, d, u in sorted(del_ok):
        f.write('- id=%s %s（公演 %s）\n' % (i, n, d))
        if u:
            f.write('  - %s\n' % u)
    f.write('\n## 消さない：公演は終わったが買える枠が生きている %d件\n\n' % len(keep_stream))
    for i, n, d, u, c in sorted(keep_stream):
        f.write('- id=%s %s（公演 %s・生き枠%d）%s\n' % (i, n, d, c, u))
    f.write('\n## 消さない：ユーザーが残すと決めたもの %d件\n\n' % len(keep_manual))
    for i, n, d, u in sorted(keep_manual):
        f.write('- id=%s %s（公演 %s）%s\n' % (i, n, d, u))
print('del_ok=%d keep_stream=%d keep_manual=%d' % (len(del_ok), len(keep_stream), len(keep_manual)))
