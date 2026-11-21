# -*- coding: utf-8 -*-
# 11/26 発売のまとめ歌詞2本の行を、index.html の登録（11/26 に発売の受付の括弧の県・時刻・先行かどうか）と1行ずつ突き合わせる（check_lyrics_1125 の形）
import io, re, sys, json
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = {e['id']: e for e in C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())}
D = '2026-11-26'
PRE = re.compile(r'先行|プレリザーブ|プレオーダー|リザーブ|プリセール|プレセール|会員')
# [歌詞の行, id, 時刻, 県, 先行]
L = [
    ['かわなか みゆき あいち', 37575, '10:00', '愛知', False],
    ['やまもと じょうじ たち とうきょう', 42996, '10:00', '東京', False],
    ['たつみ ゆうと たち とうきょう', 51217, '10:00', '東京', False],
    ['ぜんしんざ はつはる とくべつ こうえん きょうと', 5461, '10:00', '京都', False],
    ['うめぼう あいち せんこう', 6300, '10:00', '愛知', True],
    ['たつみ ゆうと ちば せんこう', 55973, '12:00', '千葉', True],
    ['めい じぇい おおさか', 45838, '10:00', '大阪', False],
    ['めい じぇい おおさか（ジャズの棚の同じ公演）', 56959, '10:00', '大阪', False],
    ['でふすぱいらる とうきょう', 41752, '10:00', '東京', False],
    ['さかぐち あみ ほっかいどう せんこう', 48624, '11:00', '北海道', True],
    ['はやしべ さとし いばらき せんこう', 52884, '12:00', '茨城', True],
    ['らむね しょうてんがい かながわ', 51165, '21:00', '神奈川', False],
    ['だずりんぐ ばっど とうきょう', 21404, '21:00', '東京', False],
]
json.dump(L, io.open('C:/Users/user/oshinavi/tmp/x1122/x/lyrics_lines_1126.json', 'w', encoding='utf-8'), ensure_ascii=False)
out = io.open('C:/Users/user/oshinavi/tmp/x1122/x/check_lyrics_1126.txt', 'w', encoding='utf-8')
bad = 0
for ly, i, tm, pf, sen in L:
    e = E.get(i)
    ts = [t for t in (e or {}).get('tickets') or [] if t.get('startDate') == D and not t.get('soldout')]
    ok_t = [t for t in ts if re.search(r'(?<!\d)%s発売' % tm.lstrip('0'), t.get('type') or '')]
    prefs = {m for t in ok_t for m in re.findall(r'（([^（）\s]+?) [^（）]*公演', t.get('type') or '')}
    pre = any(PRE.search(t.get('type') or '') for t in ok_t)
    good = bool(e) and e.get('genre') != 'new' and ok_t and (not pf or any(pf in p for p in prefs)) and (pre == sen)
    bad += not good
    out.write('%s %s ｜ id%s %s / %s genre=%s ｜ 受付 %s ｜ 県 %s ｜ 先行 %s\n' % ('✅' if good else '🚨', ly, i, (e or {}).get('artist', '')[:30], (e or {}).get('name', '')[:30], (e or {}).get('genre'),
              [t.get('type')[:60] for t in ok_t] or [t.get('type')[:60] for t in ts], prefs, pre))
out.write('\n🚨 %d 行\n' % bad)
