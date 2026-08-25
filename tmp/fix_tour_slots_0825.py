# -*- coding: utf-8 -*-
"""昼のヒール後に reconcile が出した取りこぼし／期限切れを当てる。

実ページ確認（2026-08-25 13:0x・tools/pia_tickets.py）:
 id4054 jo0ji
   受付終了 = 北海道11/22プレリザーブ／愛知12/5／大阪11/8／広島11/15 → 4枠を落とす
   🚨未登録 = 「jo0ji」プレリザーブ Zepp Fukuoka(福岡 11/28公演) 受付中 〜2026/9/6 23:59
              （bundle b2670553 にだけ出ていた＝[[feedback_pia_bundle_hides_shows]]の型）→ 足す
 id4103 矢野顕子
   受付終了 = 矢野顕子〔大阪〕(大阪 11/18公演) → 1枠を落とす
"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

DROP = {
    4054: ['プレリザーブ（北海道 11/22公演）〜8/20 11:00',
           'プレリザーブ（愛知 12/5公演）〜8/23 23:59',
           'プレリザーブ（大阪 11/8公演）〜8/25 11:00',
           'プレリザーブ（広島 11/15公演）〜8/25 11:00'],
    4103: ['先行（大阪 11/18公演）〜8/25 11:00'],
}
ADD = {
    4054: [{'type': 'プレリザーブ（福岡 11/28公演）〜9/6 23:59',
            'date': '2026-09-06',
            'url': 'https://t.pia.jp/pia/ticketInformation.do?lotRlsCd=31863'}],
}

path = 'index.html'
s = io.open(path, encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', s, re.S).group(1))
cur = {e['id']: e for e in EV}

built = []
for eid in (4054, 4103):
    ts = [t for t in cur[eid]['tickets'] if t.get('type') not in DROP.get(eid, [])]
    n_drop = len(cur[eid]['tickets']) - len(ts)
    assert n_drop == len(DROP.get(eid, [])), 'id%d 落とせた枠 %d / 指定 %d' % (
        eid, n_drop, len(DROP.get(eid, [])))
    ts += ADD.get(eid, [])
    ts.sort(key=lambda t: t.get('date') or '')
    built.append({'id': eid, 'tickets': ts})
    print('id%d %d枠 → %d枠（落とし%d・足し%d）' % (
        eid, len(cur[eid]['tickets']), len(ts), n_drop, len(ADD.get(eid, []))))

json.dump(built, open('tmp/built_tourfix_0825.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('written tmp/built_tourfix_0825.json（適用は tmp/apply_tickets_0825.py）')
