# -*- coding: utf-8 -*-
import urllib.request, re, io, time, html as _html

T = [
 ('NEW6274_石川さゆり豊橋1/31', '2627655'),
 ('OLD2338_石川さゆり極上韮崎10/4', '2623354'),
 ('OLD4509_石川さゆり岡山11/28', '2626203'),
 ('NEW6287_世良KK2027鹿児島1/9', '2632576'),
 ('NEW6288_世良KK2026豊川12/6', '2629110'),
 ('OLD5291_世良深谷11/29', '2607858'),
 ('NEW6303_桂文珍JAPANTOUR狭山2/6', '2630056'),
 ('OLD413b_桂文珍有楽町11/29', '2627160'),
 ('OLD4670_桂文珍川崎1/17', '2628387'),
 ('NEW6306_伯山石川3/14', '2627560'),
 ('NEW6317_プリキュア石川12/5', '2633613'),
 ('NEW6332_レオてつ和歌山1/16', 'b2563199'),
 ('OLD4223_レオてつ常陸大宮10/12', '2632487'),
 ('NEW6343_エリザベート長野12/24', '2632218'),
 ('NEW6345_音楽の絵本板橋12/26', '2627800'),
 ('OLD4207_音楽の絵本苫小牧11/21', '2629881'),
 ('NEW6351_0歳藤枝12/13', '2633965'),
 ('OLD3638_0歳横浜11/7', '2628113'),
 ('NEW6344_大阪フィル枚方2/20', '2632255'),
 ('OLD1961_大阪フィル11/12', '2545140'),
]

def clean(body):
    b = re.sub(r'<script.*?</script>', ' ', body, flags=re.S)
    b = re.sub(r'<style.*?</style>', ' ', b, flags=re.S)
    b = re.sub(r'<!--.*?-->', ' ', b, flags=re.S)
    b = re.sub(r'<[^>]+>', ' ', b)
    return _html.unescape(re.sub(r'\s+', ' ', b)).strip()

o = io.open('tmp/dup_detail2_0902.txt', 'w', encoding='utf-8')
for tag, cd in T:
    u = ('https://t.pia.jp/pia/event/event.do?eventBundleCd=' + cd) if cd.startswith('b') \
        else ('https://t.pia.jp/pia/event/event.do?eventCd=' + cd)
    o.write(u'##### %s %s\n' % (tag, u))
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            final = r.geturl(); body = r.read().decode('utf-8', 'replace')
        if 'sorry.pia' in final:
            o.write(u'  混雑\n\n'); time.sleep(20); continue
        t = clean(body)
        # 公演詳細本文 = 「チケットぴあトップ」以降〜「チケット情報」手前 あたり
        i = t.find('公演情報')
        if i < 0: i = t.find('公演期間')
        j = t.find('チケット情報 公演エリア')
        seg = t[max(0, i):j] if (i >= 0 and j > i) else t[:4000]
        if len(seg) < 100:
            seg = t[:4000]
        o.write(u'  ' + seg[:2200] + u'\n')
        # 出演者タグ
        m = re.search(r'お気に入り登録(.{0,300}?)(?:公演期間|$)', t)
        if m: o.write(u'  @出演タグ: %s\n' % m.group(1).strip()[:300])
    except Exception as e:
        o.write(u'  ERR %s\n' % e)
    o.write(u'\n'); o.flush()
    print(tag, 'ok')
    time.sleep(3)
o.close()
print('DONE')
