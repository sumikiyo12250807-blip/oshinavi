# -*- coding: utf-8 -*-
"""heal_union_stale.py — ヒールの安全弁で止まった件に、取り直しを「足し算」で当てる（もと tmp/heal_blocked_union_1805.py・2026-09-14 夜）。
🆕2026-10-22 すちこ「足し算の道具、直していいわよ」＝置き換えない場合を2つ足した：
  ・ぴあ以外の売り場の枠（FANY・e+ など）は、ぴあの取り直しで置き換えない（10/21 ロザン 19973・20221＝FANY の一般をぴあで上書き）
  ・発売前の元の枠（発売日が今日より後）を、発売日が過去の取り直しでは置き換えない（10/21・10/22 ふみ 25264＝11/7 発売の一般をぴあに残る「10/3発売」の表示で置き換え）
使い方: python tools/heal_union_stale.py [--apply] [--ids-src]   （対象 id は tmp/heal_blocked_hold_1805.txt）
当てたら tmp/heal_head_compare_1805.py で「枠が消えたエントリ 0」を確かめる。
"""
"""止まった26件に取り直しを「足し算」で当てる（2026-09-14 夜）。
安全弁が止めたのは、取り直し（tmp/heal_ids.json）に元の生きた枠が入っていなかったから。
ぴあで見ると多くは「取り直しが拾い損ねただけ」（まとめページ版の飛び先・飛び先が空の枠・券種名の書き替え）。
だから差し替えでなく足し算にする:
  ・取り直しの枠は全部入れる（飛び先が空なら、置き換える元の枠の飛び先を引き継ぐ）
  ・元の枠は「取り直しのどれかに置き換えられた」ものだけ外す。置き換え＝
      ① 券種の基底名が同じで、売り場の番号が同じ／どちらかの飛び先が空／元が「M/D発売」の古い形
      ② 売り場の番号と公演（perf_key）が同じ（【仙台大会】のような券種名の書き替え）
  ・それ以外の元の枠は全部そのまま残す＝画面から消える枠は出ない
  ・売り切れの印付きの元の枠は、置き換えがあっても残す（取り直しは売り切れを拾わない）
売り切れ・販売終了の印付けは別（heal_blocked_slotstatus_1805.md を見てから）。
使い方: python tmp/heal_blocked_union_1805.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
ids = [int(x) for x in io.open('tmp/heal_blocked_hold_1805.txt', encoding='utf-8').read().split(',') if x.strip()]
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
SRC = 'tmp/heal_ids.json' if '--ids-src' in sys.argv else 'tmp/heal_stale.json'   # 10/22：--ids で取り直した分は heal_ids.json
built = {o['id']: o for o in json.load(io.open(SRC, encoding='utf-8')) if o.get('status') == 'convert'}
OLD_FORM = re.compile(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}\s*発売\s*$')


def replaces(n, o):
    # 10/22：ぴあ以外の売り場の枠（FANY・e+ など）は、ぴあの取り直しで置き換えない（10/21 ロザン＝FANY の一般をぴあで上書き／分かれたボタンの e+ 側を守る）
    if o.get('url') and 'pia.jp' not in o['url']:
        return False
    # 10/22：発売前の元の枠を、発売日が過去の取り直し（ぴあに残る古い発売日の表示）では置き換えない（ふみ）
    if (o.get('startDate') or '') > TODAY and n.get('startDate') and n['startDate'] < TODAY:
        return False
    bn, bo = H.base_type(n.get('type')), H.base_type(o.get('type'))
    un, uo = H._url_id(n.get('url')), H._url_id(o.get('url'))
    if bn == bo and (un == uo or not n.get('url') or not o.get('url') or OLD_FORM.search(o.get('type') or '')):
        return True
    # ② は「元に無かった【…】の札が付いただけ」の書き替えに限る（【仙台大会】）。
    #    同じ売り場の番号でも【電子チケット】↔【紙チケット】、4次プリセール↔一般発売、poco先行↔一般発売は別の枠。
    strip = lambda s: re.sub(r'【[^】]*】', '', s)
    return bool(n.get('url') and o.get('url') and un == uo and '【' not in bo
                and strip(bn) == bo and H.perf_key(n.get('type')) == H.perf_key(o.get('type')))


def vis(ts):
    return sum(1 for t in ts if H.visible_slot(t, TODAY))


total = 0
for i in ids:
    e, o = by.get(i), built.get(i)
    if not e or not o:
        print('id%-5s 取り直し無し＝触らない' % i)
        continue
    old = e.get('tickets') or []
    new = [dict(t) for t in o['tickets']]
    # 10/22（ふみ）：発売前の元の枠と同じ券種で、発売日が過去の取り直しの枠は、ぴあに残った古い表示＝足さずに捨てる（二重に出さない）
    stale = [n for n in new if n.get('startDate') and n['startDate'] < TODAY and any(
        H.base_type(n.get('type')) == H.base_type(t.get('type')) and (t.get('startDate') or '') > TODAY
        and 'pia.jp' in (t.get('url') or 'pia.jp') for t in old)]
    if stale:
        print('id%-5s 古い発売日の取り直しを捨てる %d枠：%s' % (i, len(stale), ' ／ '.join(n.get('type') for n in stale)))
        new = [n for n in new if n not in stale]
    gone, kept = [], []
    for t in old:
        rep = [n for n in new if replaces(n, t)]
        if rep and not t.get('soldout'):
            for n in rep:
                if not n.get('url') and t.get('url'):
                    n['url'] = t['url']
                if not n.get('startDate') and t.get('startDate'):
                    n['startDate'] = t['startDate']
            gone.append(t)
        else:
            kept.append(t)
    merged = new + kept
    ko = {H.slot_key(t) for t in merged if H.visible_slot(t, TODAY)}
    lost = [t for t in old if H.visible_slot(t, TODAY) and H.slot_key(t) not in ko
            and not any(replaces(n, t) for n in new)]
    e['tickets'] = merged
    total += 1
    print('id%-5s %s ｜出る枠 %d→%d（取り直し%d・置き換え%d・残す%d）%s' % (
        i, (e.get('name') or '')[:24], vis(old), vis(merged), len(new), len(gone), len(kept),
        '  🚨消える枠 %d' % len(lost) if lost else ''))
    for t in gone:
        if H.visible_slot(t, TODAY):
            n = [x for x in new if replaces(x, t)][0]
            print('     置換 %s → %s ｜%s' % (t.get('type'), n.get('type'), H._url_id(n.get('url'))))
print('\n%d件' % total)
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
