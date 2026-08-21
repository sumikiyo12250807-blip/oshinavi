# -*- coding: utf-8 -*-
"""X投稿の主役にする3組のデータを直す（2026-08-21）。

① 4334 ONE OK ROCK ＝ **会場欄が古かった**。明日8/22 10:00に一般発売が出るのは
   **ZOZOマリンスタジアム（千葉）9/5・9/6**なのに、venue は「マリンメッセ福岡／宮城セキスイハイム」
   （＝8/18・8/19・8/25・8/26の終わった公演）のままだった。実ページで取り直して置換する。
     https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669955
② 3126 PEDRO / 3475 キュウソネコカミ ＝ 同じ文言の枠が二重になっていた
   （今朝のツアー統合で足した分と元からあった分がぶつかった）。**同じ type かつ同じ url** のものを1つに畳む。
   🚨飛び先が違うものは残す（[[feedback_dedup_badges_keeps_urls]]）。
   取り直した結果は date が縮むので**置換しない**（渡したURLに含まれない公演があるため）。
"""
import io, re, json, sys, shutil, collections
sys.stdout.reconfigure(encoding='utf-8')

built = {e['id']: e for e in json.load(io.open('tmp/xfix_built.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    if e['id'] == 4334:
        b = built[4334]
        print('① id=4334 %s' % e.get('name'))
        print('   venue %s → %s' % (e.get('venue'), b['venue']))
        print('   date  %s → %s' % (e.get('date'), b['date']))
        e['venue'] = b['venue']; e['prefecture'] = b['prefecture']
        e['date'] = b['date']; e['dateLabel'] = b.get('dateLabel')
        for t in b['tickets']:
            t.setdefault('url', (e.get('links') or {}).get('pia'))
        e['tickets'] = b['tickets']
        e['verifiedAt'] = '2026-08-21'
    elif e['id'] in (3126, 3475):
        ts = e['tickets']
        for t in ts:
            t.setdefault('url', (e.get('links') or {}).get('pia'))
        seen, keep = set(), []
        for t in ts:
            k = (t.get('type'), t.get('url'))
            if k in seen:
                print('② id=%d 重複を落とす: %s' % (e['id'], t['type']))
                continue
            seen.add(k); keep.append(t)
        print('② id=%d %s 枠 %d → %d' % (e['id'], e.get('name'), len(ts), len(keep)))
        e['tickets'] = keep
        e['verifiedAt'] = '2026-08-21'

shutil.copyfile('index.html', 'index.html.bak_0821_xfix')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
