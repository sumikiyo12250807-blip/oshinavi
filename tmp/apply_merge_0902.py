# -*- coding: utf-8 -*-
"""統合を適用する。「追加と補完だけ・置換で枠を殺さない」
（feedback_build_pia_multiurl_loses_ticket_url の二次事故の教訓）。

  6136 舞台「呪術廻戦」-渋谷事変前編- ← 6137（大阪）を畳む
  6105 劇団「ハイキュー!!」“勝者と敗者” ← 6106（大阪）を畳む

ツアーは1エントリ（feedback_tour_consolidate）。venue/dateLabel/date は
再ビルド結果（全国ツアー表記・千秋楽）に更新する。畳んだ側の id は欠番にする
（新着プールの id は振り直さない＝feedback_new_list_order_lock）。

  python tmp/apply_merge_0902.py [--apply]
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
PAIRS = [(6136, 6137), (6105, 6106)]

built = {e['id']: e for e in json.load(open('tmp/merge_built_0902.json', encoding='utf-8'))}
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


dropped = []
for keep, drop in PAIRS:
    b = built[keep]
    ke, de = by[keep], by[drop]
    before = [t for t in (ke.get('tickets') or [])] + [t for t in (de.get('tickets') or [])]
    newk = {key(t) for t in b['tickets']}
    # 既存の枠のうち、再ビルドに現れなかったものは捨てずに残す（＝追加と補完だけ）
    keepers = [t for t in before if key(t) not in newk
               and (base_type(t.get('type')), '') not in {(k[0], '') for k in newk}]
    merged = list(b['tickets']) + keepers
    print(f'=== id{keep} ← id{drop}')
    print(f'   枠: 元 {len(before)}（{len(ke.get("tickets") or [])}+{len(de.get("tickets") or [])}）'
          f' → 再ビルド {len(b["tickets"])} + 据置 {len(keepers)} = {len(merged)}')
    for t in keepers:
        print(f'   据置: {t.get("type")}')
    ke['tickets'] = merged
    ke['artist'] = b.get('artist') or ke.get('artist')
    ke['name'] = b.get('name') or ke.get('name')
    for f in ('venue', 'dateLabel', 'date', 'prefecture'):
        if b.get(f):
            print(f'   {f}: {ke.get(f)!r} → {b[f]!r}')
            ke[f] = b[f]
    dropped.append(drop)

EV2 = [e for e in EV if e['id'] not in dropped]
print(f'\nエントリ数 {len(EV)} → {len(EV2)}（欠番 {dropped}）')
if not APPLY:
    print('（--apply を付けると書き込む）')
    sys.exit(0)
# 🚨 index.html は CRLF。newline='' で読み書きすると json.dumps の \n だけが素の LF で入り、
#   EVENTS配列だけ改行が混ざる（2026-09-02 に実際にやった）。改行をそろえてから書く。
#   出典 feedback_index_html_crlf_preserve
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(EV2, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
open('index.html.bak_0902_merge', 'w', encoding='utf-8', newline='').write(src)
out = src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():]
open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('index.html を更新（backup: index.html.bak_0902_merge）')
