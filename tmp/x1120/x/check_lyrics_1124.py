# -*- coding: utf-8 -*-
# 11/24 発売のまとめ歌詞2本の行を、index.html の登録（11/24 に発売の受付の括弧の県・時刻・先行かどうか）と1行ずつ突き合わせる
import io, re, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = {e['id']: e for e in C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())}
D = '2026-11-24'
PRE = re.compile(r'先行|プレリザーブ|プレオーダー|リザーブ|プリセール|プレセール|会員')
# (歌詞の行, id, 時刻, 県（受付の括弧）, 先行か)
L = [
    ('しもの たつや と たかはし ひでき とうきょう', 53841, '10:00', '東京', False),
    ('みやた だい と つじもと れいの ちぇろ とうきょう', 54945, '10:00', '東京', False),
    ('かびら じえい いはら つよし あやの かなみ やまぐち', 49265, '10:00', '山口', False),
    ('たさん しま おおさか', 55875, '10:00', '大阪', False),
    ('じゅこう ちゃかい なら せんこう', 55879, '10:00', '奈良', True),
    ('のむら まんさい たち とうきょう せんこう', 55686, '11:00', '東京', True),
    ('しんこくりつ げきじょう おぺら とうきょう せんこう', 54075, '19:00', '東京', True),
    ('きみょう れいたろう ばんど と ざいにち ふぁんく とうきょう', 45930, '10:00', '東京', False),
    ('そるむ あいち せんこう', 45845, '10:00', '愛知', True),
    ('でぃーん ほっかいどう せんこう', 55672, '11:00', '北海道', True),
    ('あくのゆめ と ひまつぶし とうきょう', 36182, '18:00', '東京', False),
    ('とうきょう あいどる げきじょう とうきょう', 53227, '21:00', '東京', False),
    ('きゅーくる', 54678, '21:00', '', False),
    ('きっど ばん たち とうきょう', 48836, '22:00', '東京', False),
    ('かくめい どーぷねす たち とうきょう', 55948, '22:15', '東京', False),
]
out = io.open('C:/Users/user/oshinavi/tmp/x1120/x/check_lyrics_1124.txt', 'w', encoding='utf-8')
bad = 0
for ly, i, tm, pf, sen in L:
    e = E.get(i)
    ts = [t for t in (e or {}).get('tickets') or [] if t.get('startDate') == D and not t.get('soldout')]
    ok_t = [t for t in ts if re.search(r'(?<!\d)%s発売' % tm.lstrip('0'), t.get('type') or '')]
    prefs = {m for t in ok_t for m in re.findall(r'（([^（）\s]+?) [^（）]*公演', t.get('type') or '')}
    pre = any(PRE.search(t.get('type') or '') for t in ok_t)
    good = bool(e) and e.get('genre') != 'new' and ok_t and (not pf or any(pf in p for p in prefs)) and (pre == sen)
    bad += not good
    out.write('%s %s ｜ id%s %s ｜ 受付 %s ｜ 県 %s ｜ 先行 %s\n' % ('✅' if good else '🚨', ly, i, (e or {}).get('name', '')[:30],
              [t.get('type')[:50] for t in ok_t] or [t.get('type')[:50] for t in ts], prefs, pre))
out.write('\n🚨 %d 行\n' % bad)
