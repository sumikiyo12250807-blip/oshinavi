# -*- coding: utf-8 -*-
"""削除の客観チェックで見つかった2件の是正（どちらも「登録の公演日が短く切れていた」型）。

939  まつもと市民芸術館『松本のオフィーリア』
     ぴあ実データ: 公演 2026-08-27〜2026-08-30 / statustext=「販売終了」
     → date を千秋楽 2026-08-30 に直し、枠に saleEnded を付けて「販売終了」バッジで残す
       （feedback_saleended_vs_soldout＝販売終了も消さずに出し続ける）

4133 Age Factory／ENTH／Paledusk
     ぴあ実データ(b2563811): 9/2 Zepp Haneda(TOKYO) の2券種が「予定枚数終了」
     → date を千秋楽 2026-09-02 に直し、その2枠を soldout で追加（予定枚数終了バッジ）
     ⚠️ 追加した2枠の `date`(販売終了日)はぴあが出していない。公演日 2026-09-02 を入れてある。

🚨 index.html は CRLF。json.dumps の LF を元の改行へ戻すこと。
"""
import io, re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
PATH = 'index.html'
src = io.open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src[:4000] else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
E = json.loads(m.group(2))
by = {e['id']: e for e in E}

# --- 939 ---
e = by[939]
assert e['date'] == '2026-08-27', e['date']
e['date'] = '2026-08-30'
n = 0
for t in (e.get('tickets') or []):
    t['soldout'] = True
    t['saleEnded'] = True
    t['saleEndedSince'] = TODAY
    n += 1
print('939 date→2026-08-30 / 販売終了マーク %d枠' % n)

# --- 4133 ---
e = by[4133]
assert e['date'] == '2026-08-27', e['date']
e['date'] = '2026-09-02'
e['venue'] = '全国ツアー（Zepp Sapporo／Zepp Nagoya／Zepp Osaka Bayside／Zepp Fukuoka／Zepp Haneda(TOKYO)）'
add = [
    {"type": "一般発売（東京 9/2公演）", "date": "2026-09-02",
     "url": "https://t.pia.jp/pia/ticketInformation.do?eventCd=2543601&rlsCd=002",
     "soldout": True, "soldoutSince": TODAY},
    {"type": "＜2F立ち見＞追加販売（東京 9/2公演）", "date": "2026-09-02",
     "url": "https://t.pia.jp/pia/ticketInformation.do?eventCd=2543601&rlsCd=003",
     "soldout": True, "soldoutSince": TODAY},
]
have = {t.get('url') for t in (e.get('tickets') or [])}
for a in add:
    if a['url'] in have:
        continue
    e.setdefault('tickets', []).append(a)
print('4133 date→2026-09-02 / 予定枚数終了2枠を追加 / 枠数 %d' % len(e['tickets']))

dumped = json.dumps(E, ensure_ascii=False, indent=2).replace('\n', nl)
io.open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
print('書き戻した (改行=%r)' % nl)
