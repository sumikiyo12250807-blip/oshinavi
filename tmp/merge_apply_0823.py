# -*- coding: utf-8 -*-
"""8/23朝：新着候補のうち既存と同じ興行だった9件を既存エントリへ統合する。
方針（feedback_tour_consolidate / feedback_dedup_badges_keeps_urls / feedback_tour_per_ticket_url）:
  ・**足すだけ**（既存の枠は消さない）
  ・追加する枠には必ず ticket.url（その売り場のぴあURL）を付ける＝導線を消さない
  ・同じ文言のバッジを作らない（東京ホラー特区は券種名を type に入れて見分けをつける）
"""
import re, json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

NEW = {e['id']: e for e in json.load(io.open('tmp/mergeinto_0823.json', encoding='utf-8'))}

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
BY = {e['id']: e for e in EVENTS}

log = []


def pia(nid):
    return (NEW[nid].get('links') or {}).get('pia')


def add_tickets(target_id, nid, retype=None):
    """新エントリ nid の枠を target_id へ足す。url は新エントリのぴあURLを刻む。"""
    tgt = BY[target_id]
    url = pia(nid)
    have = {(t.get('type'), t.get('date')) for t in tgt['tickets']}
    added = 0
    for t in NEW[nid]['tickets']:
        nt = dict(t)
        if retype:
            nt['type'] = retype
        if (nt['type'], nt.get('date')) in have:
            continue
        nt['url'] = url
        tgt['tickets'].append(nt)
        have.add((nt['type'], nt.get('date')))
        added += 1
    log.append('id%-5s ← id%-5s 枠+%d (%s)' % (target_id, nid, added, url))
    return added


# ── 1) 新日本フィル「第九」特別演奏会2026 ── 既存4782(12/17の1公演)は新5060(5公演のbundle)の部分集合
t = BY[4782]
n = NEW[5060]
before = len(t['tickets'])
old_pairs = {(x.get('type'), x.get('date')) for x in t['tickets']}
new_pairs = {(x.get('type'), x.get('date')) for x in n['tickets']}
assert old_pairs <= new_pairs, '4782の既存枠が新bundleに含まれていない＝置換不可'
t['name'] = n['name']
t['artist'] = n['artist']
t['dateLabel'] = n['dateLabel']
t['venue'] = n['venue']
t['prefecture'] = n['prefecture']
t['date'] = n['date']
t['links']['pia'] = pia(5060)
t['tickets'] = [dict(x) for x in n['tickets']]
log.append('id4782  ← id5060  枠%d→%d（既存枠は新bundleの部分集合と機械確認）' % (before, len(t['tickets'])))

# ── 2) 音楽の絵本～ブラスサンタ with サキソフォックス～（埼玉12/13 ＋ 東京12/12）
t = BY[3557]
t['name'] = '音楽の絵本～ブラスサンタ with サキソフォックス～'
t['artist'] = '音楽の絵本'
t['venue'] = '全国ツアー（深谷市民文化会館 大ホール／銀座ブロッサム（中央会館））'
t['prefecture'] = '埼玉・東京'
t['dateLabel'] = '2026年12月12日(土)・13日(日) 東京・埼玉'
add_tickets(3557, 5067)

# ── 3) しまじろうコンサート（既存309の全国ツアーへ 栃木12/26・三重12/20 を追加）
add_tickets(309, 5074)
add_tickets(309, 5078)

# ── 4) ケロポンズファミリーコンサート（福岡10/12 ＋ 岡山10/31＝千秋楽）
t = BY[2384]
t['venue'] = '全国ツアー（石橋文化ホール／ロマン高原かよう総合会館 レインボーホール）'
t['prefecture'] = '福岡・岡山'
t['dateLabel'] = '2026年10月12日(月)・31日(土) 福岡・岡山'
t['date'] = '2026-10-31'
add_tickets(2384, 5090)

# ── 5) 東京ホラー特区!!2026（サイン会・撮影会の別売り場5つ／同じ文言にならないよう券種名を入れる）
HORROR = {
    5091: '一般発売【エドワード・ファーロング サイン or セルフィー会】（東京 9/11〜9/13公演）8/26 11:00発売',
    5092: '一般発売【エドワード・ファーロング 撮影会】（東京 9/11〜9/13公演）8/26 11:00発売',
    5093: '一般発売【リンダ・ハミルトン／エドワード・ファーロング 撮影会】（東京 9/11〜9/13公演）8/26 11:00発売',
    5094: '一般発売【リンダ・ハミルトン サイン or セルフィー会】（東京 9/11〜9/13公演）8/26 11:00発売',
    5095: '一般発売【リンダ・ハミルトン 撮影会】（東京 9/11〜9/13公演）8/26 11:00発売',
}
for nid, ty in HORROR.items():
    add_tickets(3798, nid, retype=ty)

# 同じ文言のバッジが出来ていないか（統合先だけ）
for tid in (4782, 3557, 309, 2384, 3798):
    types = [x.get('type') for x in BY[tid]['tickets']]
    dup = [x for x in set(types) if types.count(x) > 1]
    if dup:
        print('🚨 SAME-BADGE id%d: %s' % (tid, dup))
        sys.exit(2)

NL = '\r\n' if '\r\n' in h else '\n'
io.open('index.html.bak_0823_merge', 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('\n'.join(log))
print('OK 統合完了')
