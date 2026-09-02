# -*- coding: utf-8 -*-
"""判断が割れるものだけ、ぴあページの公演詳細テキスト（出演・曲目・主催など）を抜く。"""
import urllib.request, re, io, time, html as _html

T = [
 ('NEW6274_石川さゆり豊橋', '2627655'),
 ('OLD2338_石川さゆり極上韮崎', '2623354'),
 ('OLD4509_石川さゆり岡山', '2626203'),
 ('NEW6287_世良2027鹿児島', '2632576'),
 ('NEW6288_世良2026豊川', '2629110'),
 ('OLD5291_世良深谷', '2607858'),
 ('NEW6303_桂文珍狭山', '2630056'),
 ('OLD413b_桂文珍有楽町', '2627160'),
 ('OLD4670_桂文珍川崎', '2628387'),
 ('NEW6306_伯山石川', '2627560'),
 ('NEW6317_プリキュア石川', '2633613'),
 ('NEW6332_レオてつ和歌山', 'b2563199'),
 ('OLD4223_レオてつ常陸大宮', '2632487'),
 ('NEW6343_エリザベート長野', '2632218'),
 ('NEW6344_大阪フィル枚方', '2632255'),
 ('NEW6345_音楽の絵本板橋', '2627800'),
 ('OLD4207_音楽の絵本苫小牧', '2629881'),
 ('NEW6351_0歳藤枝', '2633965'),
 ('OLD3638_0歳横浜', '2628113'),
 ('NEW6274b_石川さゆり豊橋', '2627655'),
]

def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()

o = io.open('tmp/dup_detail_0902.txt', 'w', encoding='utf-8')
seen = set()
for tag, cd in T:
    if cd in seen:
        continue
    seen.add(cd)
    u = ('https://t.pia.jp/pia/event/event.do?eventBundleCd=' + cd) if cd.startswith('b') \
        else ('https://t.pia.jp/pia/event/event.do?eventCd=' + cd)
    o.write(u'##### %s %s\n' % (tag, u))
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            final = r.geturl(); body = r.read().decode('utf-8', 'replace')
        if 'sorry.pia' in final:
            o.write(u'  混雑ページ\n\n'); time.sleep(20); continue
        # 公演詳細（説明）ブロックを広めに取る
        blocks = []
        for pat in (r'<div[^>]*class="[^"]*eventDetail[^"]*"[^>]*>(.*?)</div>\s*</div>',
                    r'<section[^>]*class="[^"]*eventInformation[^"]*"[^>]*>(.*?)</section>',
                    r'<div[^>]*class="[^"]*p-eventInfo[^"]*"[^>]*>(.*?)</section>',
                    r'<div[^>]*id="eventDetail"[^>]*>(.*?)</div>'):
            for mm in re.finditer(pat, body, re.S):
                t = txt(mm.group(1))
                if len(t) > 20:
                    blocks.append(t)
        if not blocks:
            # フォールバック: 本文中の「■」「主催」「出演」周辺
            t = txt(body)
            i = t.find('チケット情報')
            blocks.append(t[:i] if i > 200 else t[:3000])
        got = u' ||| '.join(blocks)
        # ノイズ（スクリプト・共通文言）を落として頭を出す
        got = re.sub(r'window\.dataLayer.*', '', got)
        got = re.sub(r'!function\(f,b,e.*', '', got)
        o.write(u'  ' + got[:2500] + u'\n')
    except Exception as e:
        o.write(u'  ERR %s\n' % e)
    o.write(u'\n'); o.flush()
    print(tag, 'ok')
    time.sleep(3)
o.close()
print('DONE')
