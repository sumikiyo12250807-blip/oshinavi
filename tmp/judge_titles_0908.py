# -*- coding: utf-8 -*-
"""迷った候補について、ぴあの実ページから公演正式名（ツアー名）を取ってUTF-8ファイルに書く。"""
import re, sys, time, io
sys.path.insert(0, 'tools')
from build_pia_entries import fetch, is_error_page

TARGETS = [
    ('7207 鶴 大阪12/31', '2635136'),
    ('7327 鶴 北海道11/28-29', '2635143'),
    ('既存7117 鶴 徳島香川', '2634275'),
    ('既存1202 鶴 全国', '2623323'),
    ('7225 細坪基佳 東京1/16', '2633185'),
    ('既存834 細坪基佳 福島9/26', '2615287'),
    ('7279 新日本プロレス 両国10/12', '2635794'),
    ('7280 新日本プロレス 岐阜10/30', '2635780'),
    ('既存5755 新日本プロレス 新潟10/10', '2634773'),
    ('7193 川崎鷹也 愛媛5/16', '2625820'),
    ('既存4227 川崎鷹也 全国', '2624428'),
    ('既存4493 川崎鷹也 札幌5/21', '2625456'),
    ('7210 NELKE 岡山7/17', '2629976'),
    ('既存4499 NELKE 東京7/24', '2628708'),
    ('7203 純烈 神奈川', '2635249'),
    ('7204 純烈 兵庫1/27', '2635686'),
    ('既存2405 純烈', '2627865'),
    ('7317 東京ヴィヴァルディ 第一生命1/17', '2634699'),
    ('既存1723 東京ヴィヴァルディ 六本木11/3', '2625349'),
    ('7205 女王蜂 東京10/30', '2636032'),
    ('既存4802 女王蜂 全国', '2627688'),
]

out = io.StringIO()
for label, cd in TARGETS:
    url = 'https://t.pia.jp/pia/event/event.do?eventCd=' + cd
    try:
        h = fetch(url)
    except Exception as e:
        out.write('%s (%s)\n  取れなかった: %s\n\n' % (label, cd, e))
        time.sleep(3)
        continue
    if is_error_page(h):
        out.write('%s (%s)\n  ご確認ください（eventCd無効）\n\n' % (label, cd))
        time.sleep(3)
        continue
    t = re.search(r'<title>(.*?)</title>', h, re.S)
    title = re.sub(r'\s+', ' ', t.group(1)).strip() if t else '(title無し)'
    h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', h, re.S)
    h1s = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x)).strip() for x in h1s]
    subs = re.findall(r'class="[^"]*(?:eventTitle|event-title|subTitle|sub-title)[^"]*"[^>]*>(.*?)<',
                      h, re.S)
    subs = [re.sub(r'\s+', ' ', x).strip() for x in subs if x.strip()]
    out.write('%s (%s)\n' % (label, cd))
    out.write('  title: %s\n' % title)
    for x in h1s[:4]:
        if x:
            out.write('  h1: %s\n' % x)
    for x in subs[:6]:
        out.write('  sub: %s\n' % x)
    out.write('\n')
    time.sleep(3)

open(r'C:\Users\user\oshinavi\tmp\judge_titles_0908.txt', 'w', encoding='utf-8').write(out.getvalue())
print('OK wrote tmp/judge_titles_0908.txt')
