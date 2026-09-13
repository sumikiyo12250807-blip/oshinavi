# -*- coding: utf-8 -*-
"""昼のpush前検証S（2026-09-14）で見つかった3件を直す。改行は CRLF を保つ。
  3710 北海道コンサドーレ札幌対大分トリニータ
       今朝の足し込みで、まとめページ（eventBundleCd=b2670736）経由の2枠が重なった。
       まとめページの3枠の飛び先は eventCd=2626908（一般）/2626913（車いす等）/2629184（駐車券）＝登録済みの3枠と同じ売り場。
       → まとめページURLの2枠だけ外す（行ける先は1つも減らない）。1つは「■■■車いす…」の化けた名前だった。
  4928 アイスリボン
       「一般発売（東京 11/29公演）9/21 10:00発売」の飛び先が eventCd=2636539（12/13公演のページ）になっていた。
       11/29公演はぴあに別ページ eventCd=2636511（大田区産業プラザPiO 小展示ホール・9/21発売）で実在＝枠は正しい、飛び先だけ違う。
       → url を 2636511 に直す（消さない）。
  5193 劇団☆新感線『髑髏城の七人 LAST STAND』
       券種名が「2026年劇団☆新感線…『髑髏城の七人...』★3次受付」＝公演名まるごと（9/2から）。
       ぴあの原題「…『髑髏城の七人…』★3次受付／長野・石川」を組み立て道具が読み違えていた（道具は直した）。
       → 券種名を「3次受付」にする（締切 9/17 11:00 はぴあと一致）。
使い方: python tmp/fix_s_findings_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
log = []

# 3710
e = by[3710]
drop = [t for t in e['tickets'] if 'b2670736' in (t.get('url') or '')]
assert len(drop) == 2, [t['type'] for t in drop]
keep_urls = {t.get('url') for t in e['tickets'] if t not in drop}
for need in ('2626908', '2626913', '2629184'):
    assert any(need in (u or '') for u in keep_urls), '3710 に eventCd=%s の枠が残らない' % need
e['tickets'] = [t for t in e['tickets'] if t not in drop]
for t in drop:
    print('3710 外す  %s ｜%s' % (t['type'], t['url']))
    log.append((3710, e['name'], t['type'], '同じ売り場の二重の入口（まとめページ経由）＝公演ページの枠が残る', t['url']))

# 4928
e = by[4928]
hit = [t for t in e['tickets'] if t['type'].startswith('一般発売（東京 11/29公演）')]
assert len(hit) == 1, hit
old = hit[0].get('url')
assert '2636539' in (old or ''), old
hit[0]['url'] = 'https://t.pia.jp/pia/event/event.do?eventCd=2636511'
print('4928 飛び先 %s → %s ｜%s' % (old, hit[0]['url'], hit[0]['type']))

# 5193
e = by[5193]
hit = [t for t in e['tickets'] if t['type'].startswith('2026年劇団☆新感線')]
assert len(hit) == 1, hit
old = hit[0]['type']
new = re.sub(r'^.*?★3次受付', '3次受付', old)
assert new.startswith('3次受付（石川・長野 R9年 1/21〜2/14公演）〜9/17 11:00'), new
hit[0]['type'] = new
print('5193 券種名 %s → %s' % (old, new))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
with io.open('logs/removed_%s.md' % datetime.date.today().isoformat(), 'a', encoding='utf-8') as f:
    f.write('\n## 昼のpush前検証Sで外した重なり（今朝の足し込み・まだ公開していない分）\n\n')
    f.write('| id | 公演名 | 外した枠 | 理由 | 確認用URL |\n|---|---|---|---|---|\n')
    for i, n, ty, why, u in log:
        f.write('| %s | %s | %s | %s | %s |\n' % (i, n, ty, why, u))
    f.write('\n（消さずに直した＝4928 アイスリボン 11/29 の飛び先を eventCd=2636511 へ／5193 髑髏城の七人の券種名を「3次受付」へ）\n')
print('書き込み完了')
