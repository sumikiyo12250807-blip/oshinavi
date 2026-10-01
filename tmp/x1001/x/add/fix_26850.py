# -*- coding: utf-8 -*-
# 26850 ハク。＝北海道11/8に福岡12/11・熊本12/12・愛知1/16を足した＝会期・県・会場を事実に合わせる
import io, json, re
root = 'C:/Users/user/oshinavi/'
src = io.open(root + 'index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', src)
st = m.start(1)
E, end = json.JSONDecoder().raw_decode(src, st)
e = next(x for x in E if x['id'] == 26850)
print(e.get('venue'), e.get('dateLabel'), e.get('prefecture'))
e['date'] = '2027-01-16'
e['dateLabel'] = '2026年11月8日(日)〜2027年1月16日(土) 北海道・福岡・熊本・愛知'
e['prefecture'] = '北海道・福岡・熊本・愛知'
e['venue'] = '全国ツアー（SPIRITUAL LOUNGE／INSA／熊本B.9 V2／ボトムライン）'
body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
io.open(root + 'index.html', 'wb').write((src[:st] + body.replace('\n', '\r\n') + src[end:]).encode('utf-8'))
print('直した')
