# -*- coding: utf-8 -*-
"""3475 キュウソネコカミの取りこぼしを回収する（ユーザー指摘 2026-08-21「全部で21か所でやるみたい」）。

ツアー正式名＝「DMCC REAL ONEMAN TOUR 2026-2027 〜どっかん マインドフルネス! Chill? no Chill!〜」
**全21公演**（音楽ナタリー／Skream! で確認）。うちは8公演ぶんしか持っていなかった。
ぴあをアーティスト名で掃き直して未登録の eventCd を見つけ、全部まとめて再構築した。
  2612708 秋田10/23 ／ 2612586 大阪11/2 ／ 2628908 静岡2027/1/16 が未登録だった
  （さらに build の過程で岩手10/25・宮城10/30 も拾えた）

🚨**置換はしない**＝build 結果には鹿児島2/13が含まれず、置換すると千秋楽が縮んで公演が消えるため。
   既存に無い枠だけ足す（[[feedback_pia_bundle_hides_shows]]）。
🚨券種名の頭に「秋田公演 」等が残る崩れを直す。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/kyuso_built.json', encoding='utf-8'))[0]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] != 3475:
        continue
    for t in e['tickets']:
        t.setdefault('url', (e.get('links') or {}).get('pia'))
    # 既存にある「公演の組み合わせ」を（県+日付）で持つ
    def sig(ty):
        mm = re.search(r'（(.+?)\s([\d/〜~]+(?:公演)?)', ty)
        return mm.group(0) if mm else ty
    have = {sig(t['type']) for t in e['tickets']}
    print('before 枠%d / date=%s' % (len(e['tickets']), e.get('date')))
    for t in built['tickets']:
        t = dict(t)
        t['type'] = re.sub(r'^\S+公演\s+(?=一般発売)', '', t['type'])
        if sig(t['type']) in have:
            continue
        t.setdefault('url', (built.get('links') or {}).get('pia'))
        e['tickets'].append(t)
        print('    + %s | %s' % (t['type'], t.get('date')))
    e['venue'] = '全国ツアー（' + '／'.join([
        'LIVE VANQUISH', 'RISING HALL', 'Club SWINDLE', 'club change WAVE', '仙台 darwin',
        'なんばHatch', 'GOLDEN PIGS RED STAGE', '金沢EIGHT HALL', 'CASINO DRIVE', 'ペニーレーン24',
        'HEAVEN’S ROCK 宇都宮 VJ-2', 'CLUB CITTA’', 'Live House 浜松 窓枠', 'DIAMOND HALL',
        'YEBISU YA PRO', 'MUSIC ZOO KOBE 太陽と虎', '高知X-pt.', '高松DIME', 'DRUM Logos',
        '鹿児島SR HALL', 'Zepp DiverCity（TOKYO）']) + '）'
    e['prefecture'] = '全国'
    e['verifiedAt'] = '2026-08-21'
    print('after  枠%d / date=%s（据え置き）' % (len(e['tickets']), e['date']))
    n += 1
assert n == 1
shutil.copyfile('index.html', 'index.html.bak_0821_kyuso')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
