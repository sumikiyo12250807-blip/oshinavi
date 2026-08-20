# -*- coding: utf-8 -*-
"""複数のぴあページを1エントリに統合した新着に、枠ごとの会場別URL(ticket.url)を付ける。
feedback_tour_per_ticket_url＝複数会場ツアーは各ticketに会場別pia URLを付ける。
各URLを個別に build して「そのページから出た枠」を特定し、登録側の同じ券種名にURLを当てる。
"""
import re, json, sys, os, time
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B

APPLY = '--apply' in sys.argv

cands = {c['newid']: c for c in json.load(open('tmp/cand_pick_0816.json', encoding='utf-8'))}
# 候補時のnewid → 投入後の実id（finalizeで振り直したので名前で対応付ける）
raw = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', raw, re.S)
EVENTS = json.loads(m.group(2))
pool = {e['id']: e for e in EVENTS if 4326 <= e['id'] <= 4375}

def base(ty):
    """券種名から日付・時刻を落とした基底名（heal_stale と同じ考え方）"""
    ty = re.sub(r'〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$', '', ty or '')
    ty = re.sub(r'\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$', '', ty)
    return ty.strip()

TARGETS = []
for c in cands.values():
    if len(c['urls']) < 2:
        continue
    name = re.sub(r'\s+', '', c['artist'])
    for e in pool.values():
        if re.sub(r'\s+', '', e.get('artist') or '')[:8] == name[:8] or \
           B.norm_fw(c['artist'])[:10] == (e.get('artist') or '')[:10]:
            TARGETS.append((e, c['urls']))
            break

print("対象 %d件" % len(TARGETS))
changed = 0
for e, urls in TARGETS:
    print("=" * 60)
    print("id%s %s （ぴあ%dページ統合）" % (e['id'], (e.get('artist') or '')[:30], len(urls)))
    owner = {}
    for u in urls:
        u2 = u.replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')
        try:
            sub = B.build({'newid': 0, 'artist': e.get('artist'), 'urls': [u2]})
        except Exception as ex:
            print("   ERROR %s %s" % (u2, ex)); continue
        time.sleep(1.2)
        if not sub:
            continue
        for t in sub.get('tickets') or []:
            owner.setdefault(base(t.get('type')), u2)
    for t in e.get('tickets') or []:
        b = base(t.get('type'))
        u = owner.get(b)
        if u and t.get('url') != u:
            print("   %s\n      → %s" % (t.get('type'), u))
            if APPLY:
                t['url'] = u
            changed += 1
        elif not u:
            print("   ⚠️ 出所不明のまま: %s" % t.get('type'))

print()
print("=== URLを当てる枠 %d ===" % changed)
if APPLY and changed:
    bak = 'index.html.bak_0816_tickurl'
    if not os.path.exists(bak):
        open(bak, 'w', encoding='utf-8', newline='').write(raw)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8', newline='').write(
        raw[:m.start()] + m.group(1) + new_arr.replace('\n', '\r\n') + m.group(3) + raw[m.end():])
    print("適用した (backup: %s)" % bak)
