# -*- coding: utf-8 -*-
# 7.5 ぴあ発売前一覧との突き合わせで抜けていた分 → build_pia_entries の入力（足し込み5件＝既存のぴあURL／新規16件）
import io, json, re
root = 'C:/Users/user/oshinavi/'
s = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
E, _ = json.JSONDecoder().raw_decode(s, m.start(1))
by = {e['id']: e for e in E}
MERGE = {3320: 'https://t.pia.jp/pia/event/event.do?eventCd=2634573', 4071: None, 6136: 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670827', 7336: None, 9215: None}
NEW = [('OLUYO10周年記念フェス FESTIVAL-YO! 2026', '2638728'), ('廣津留すみれ', '2634095'),
       ('第48回マーチングバンド関西大会', '2627013'), ('五十嵐紅トリオ', '2638990'), ('五十嵐紅トリオ', '2639168'),
       ('五十嵐紅トリオ', '2639167'), ('五十嵐紅', '2638974'), ('五十嵐紅', '2639173'), ('五十嵐紅', '2638978'),
       ('倉冨亮太×五十嵐紅', '2638930'), ('WOMEN’S RALLY in 恵那 2026', '2638860'), ('柔道 グランドスラム東京 2026', 'b2671420'),
       ('ギラヴァンツ北九州対AC長野パルセイロ', '2636949'), ('超かぐや姫！ 超復活応援上映会', '2638299'),
       ('SHERBETS', '2633461')]
out = []
for i, u in MERGE.items():
    e = by[i]
    url = u or (e.get('links') or {}).get('pia')
    out.append({'newid': i, 'artist': e.get('artist') or e.get('name'), 'urls': [url]})
nid = 90001
for a, cd in NEW:
    if cd in s:
        print('登録済み', a, cd); continue
    key = 'eventBundleCd' if cd.startswith('b') else 'eventCd'
    out.append({'newid': nid, 'artist': a, 'urls': ['https://t.pia.jp/pia/event/event.do?%s=%s' % (key, cd)]})
    nid += 1
json.dump(out, io.open(root + 'tmp/x1001/x/add/build_in.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
