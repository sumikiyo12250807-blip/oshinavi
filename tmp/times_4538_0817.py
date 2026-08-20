# -*- coding: utf-8 -*-
"""Juice=Juice 4538 の各公演（9/18夜・9/19昼・9/19夜）の開演時刻をぴあ実ページから取る。
[[feedback_same_day_show_time_badge]]＝同一会場・同日で時間違いの公演はバッジに開演時刻を入れる。
昼/夜の語だけに頼らない。取れなければ「取れなかった」と言う（推測しない）。"""
import re, sys, html, http.client
sys.stdout.reconfigure(encoding='utf-8')


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


conn = http.client.HTTPSConnection('t.pia.jp', timeout=30)
conn.request('GET', '/pia/event/event.do?eventCd=2631763',
             headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
raw = conn.getresponse().read().decode('utf-8', 'replace')
txt = strip(raw)

print('=== 公演名の周辺100字（昼/夜ごと）===')
for kw in ('9/18夜公演', '9/19昼公演', '9/19夜公演'):
    for m in re.finditer(re.escape(kw), txt):
        seg = txt[max(0, m.start() - 60):m.start() + 140]
        print('  [%s] %s' % (kw, seg))
        print()
        break

print('=== 時刻らしき表記を全部（開場/開演/HH:MM）===')
for pat, lab in [(r'開場\s*(\d{1,2}:\d{2})', '開場'),
                 (r'開演\s*(\d{1,2}:\d{2})', '開演'),
                 (r'(\d{1,2}:\d{2})\s*開演', '開演(逆)'),
                 (r'(\d{4}/\d{1,2}/\d{1,2})\s*\([月火水木金土日]\)\s*(\d{1,2}:\d{2})', '日付+時刻')]:
    h = re.findall(pat, txt)
    print('  %-10s %s' % (lab, list(dict.fromkeys(map(str, h)))[:10] or '（無し）'))

print()
print('=== JSON-LD / data属性に時刻があるか ===')
for m in re.finditer(r'"startDate"\s*:\s*"([^"]+)"', raw):
    print('   startDate:', m.group(1))
for m in re.finditer(r'data-[a-z]*time[a-z]*="([^"]+)"', raw):
    print('   data time:', m.group(1))
