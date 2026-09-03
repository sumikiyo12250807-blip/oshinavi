# -*- coding: utf-8 -*-
"""今夜の取りこぼし監査で見つけた14件を、既存エントリに**足すだけ**で統合する。

🚨「追加と補完だけ・置換で枠を殺さない」
   （feedback_build_pia_multiurl_loses_ticket_url／feedback_heal_flattens_ticket_types の教訓）
   既存の tickets は1つも消さない。新側の枠のうち、既存に無いものだけを足す。
   重複判定の鍵＝(日付を落とした券種名, 飛び先URL)＝別の売り場なら別枠として残す。

千秋楽(date)は「既存と新側の遅いほう」に伸ばす。県(prefecture)は増えた分だけ足す。
venue は触らない（全国ツアーの表記を壊さないため）。

  python tmp/apply_leftover_merge_0903.py [--apply]
"""
import re, json, sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

# 新id → 統合先の既存id（別エージェントの独立判定）
PAIRS = [(6469, 3775), (6470, 3406), (6471, 4276), (6472, 2471), (6473, 1868),
         (6474, 3818), (6479, 2254), (6483, 892), (6485, 6303), (6488, 5100),
         (6489, 3956), (6490, 1008), (6491, 1008), (6492, 6136)]

built = {e['id']: e for e in json.load(open('tmp/leftover_built_0903.json', encoding='utf-8'))}
src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EV = json.loads(m.group(2))
by = {e['id']: e for e in EV}


def base_type(ty):
    ty = re.sub(r'〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$', '', ty or '')
    ty = re.sub(r'\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$', '', ty)
    return ty.strip()


def key(t):
    return (base_type(t.get('type')), (t.get('url') or '').strip())


added_total = 0
for newid, keepid in PAIRS:
    nb = built.get(newid)
    ke = by.get(keepid)
    if not nb or not ke:
        print('!! id%d または id%d が見つからない' % (newid, keepid))
        continue
    have = {key(t) for t in (ke.get('tickets') or [])}
    add = [t for t in nb.get('tickets', []) if key(t) not in have]
    print('=== id%d「%s」← 新id%d' % (keepid, (ke.get('name') or '')[:30], newid))
    print('    既存 %d枠 / 新側 %d枠 → 足すのは %d枠'
          % (len(ke.get('tickets') or []), len(nb.get('tickets') or []), len(add)))
    for t in add:
        print('      + %s' % t.get('type'))
    if add:
        ke['tickets'] = list(ke.get('tickets') or []) + add
        added_total += len(add)
    # 千秋楽は遅いほうへ
    if nb.get('date') and (nb['date'] > (ke.get('date') or '')):
        print('      date: %s → %s' % (ke.get('date'), nb['date']))
        ke['date'] = nb['date']
    # 県は増えた分だけ足す。
    # 🚨ただし既存が「全国」なら触らない（「全国・東京」は意味が壊れる）。
    #   県が4つを超えるものも「全国」のままにする＝バッジは ticket.type 側に県が入る。
    cur = [p for p in re.split(r'[・/／]', ke.get('prefecture') or '') if p]
    if '全国' in cur:
        pass
    else:
        for p in re.split(r'[・/／]', nb.get('prefecture') or ''):
            if p and p not in cur:
                cur.append(p)
        newpref = '全国' if len(cur) > 4 else '・'.join(cur)
        if newpref != (ke.get('prefecture') or ''):
            print('      prefecture: %r → %r' % (ke.get('prefecture'), newpref))
            ke['prefecture'] = newpref

print('\n=== 足した枠 合計 %d ===' % added_total)
if not APPLY:
    print('（--apply を付けると書き込む）')
    sys.exit(0)

nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
open('index.html.bak_0903_leftovermerge', 'w', encoding='utf-8', newline='').write(src)
open('index.html', 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('index.html を更新（backup: index.html.bak_0903_leftovermerge）')
