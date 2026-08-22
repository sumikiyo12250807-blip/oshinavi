# -*- coding: utf-8 -*-
"""同じ文言のバッジが並ぶ組**だけ**を、見分け札つきの枠に入れ替える（2026-08-22）。

丸ごと差し替えにしなかった理由＝キュウソネコカミ(3475)は昨日 8→14公演へ手で直したばかりで、
ぴあのまとめページには出てこない枠を持っている。再導出は9枠しか返さないので、
丸ごと置き換えると**昨日の修正が消える**（[[feedback_dedup_badges_keeps_urls]]）。

やること＝重複している (バッジ文言, 締切) の組を見つけ、再導出側に
「【…】を外すと同じ文言・同じ締切」の枠が**同じ枚数だけ**あるときに限って入れ替える。
枚数が合わない組は触らず報告する。
"""
import io
import json
import re
import shutil
import sys
import collections

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

built = {e['id']: e['tickets'] for e in json.load(open('tmp/dup2_built_0822.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

LBL = re.compile(r'【[^】]*】')
log = io.open('tmp/dup2_apply_0822.txt', 'w', encoding='utf-8')
swapped = 0
for e in EVENTS:
    bt = built.get(e['id'])
    if not bt:
        continue
    ts = e.get('tickets') or []
    cnt = collections.Counter((t.get('type'), t.get('date')) for t in ts)
    dups = {k for k, v in cnt.items() if v > 1}
    if not dups:
        continue
    log.write('== id%-5d %s\n' % (e['id'], e.get('name', '')))
    out, done = [], set()
    for t in ts:
        k = (t.get('type'), t.get('date'))
        if k not in dups:
            out.append(t)
            continue
        if k in done:
            continue
        done.add(k)
        # 再導出側から「札を外すと同じ文言・同じ締切」の枠を集める
        cands = [x for x in bt if (LBL.sub('', x['type']), x.get('date')) == (LBL.sub('', k[0]), k[1])]
        if len(cands) == cnt[k]:
            log.write('   %d枚を入れ替え: %s\n' % (cnt[k], k[0]))
            for x in cands:
                log.write('      → %s\n' % x['type'])
            out.extend(cands)
            swapped += len(cands)
        elif len(cands) == 1:
            # ぴあには1枠しか無いのに登録が2枚以上＝**うちの二重登録**。1枚に寄せる。
            # （飛び先URLが違えば別の売り場なので畳まない＝[[feedback_dedup_badges_keeps_urls]]）
            urls = {t.get('url') for t in ts if (t.get('type'), t.get('date')) == k}
            if len(urls) == 1:
                log.write('   二重登録を1枚に寄せる（登録%d枚 / ぴあ1枠・飛び先も同じ）: %s\n' % (cnt[k], k[0]))
                out.append(cands[0])
                swapped += 1
            else:
                log.write('   ⚠️飛び先URLが%d通りあるので畳まない: %s\n' % (len(urls), k[0]))
                out.extend([t] * cnt[k])
        else:
            log.write('   ⚠️枚数が合わないので触らない（登録%d枚 / 再導出%d枚）: %s\n'
                      % (cnt[k], len(cands), k[0]))
            out.extend([t] * cnt[k])
    if APPLY:
        e['tickets'] = out
        e['verifiedAt'] = '2026-08-22'
log.write('\n=== 入れ替えた枠 %d ===\n' % swapped)
log.close()
print('入れ替えた枠 %d → tmp/dup2_apply_0822.txt' % swapped)

if APPLY:
    shutil.copyfile('index.html', 'index.html.bak_0822_dup2')
    open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2)
        + m.group(3) + h[m.end():])
    print('適用した')
else:
    print('（判定のみ。適用は --apply）')
