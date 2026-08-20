# -*- coding: utf-8 -*-
"""tmp/eplus_check_urls.txt のURLを1本ずつ間隔をあけて叩き、公演ごと・枠ごとの窓を出す。
兄弟券種ページ（…P0210NN の NN を増分）も一緒に叩いて「同一公演の別券種が生きていないか」を見る
（feedback_eplus_delete_blindspot の券種穴）。
"""
import re, sys, time, importlib.util
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

spec = importlib.util.spec_from_file_location('epd', 'tools/eplus_detail.py')
epd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(epd)

urls = [u.strip() for u in open('tmp/eplus_check_urls.txt', encoding='utf-8') if u.strip()]


def probe(u):
    try:
        page = epd.fetch(u)
    except Exception as ex:
        return None, str(ex)
    try:
        return epd.parse(page), None
    except Exception as ex:
        return None, 'parse:%s' % ex


for u in urls:
    print('=' * 78)
    print(u)
    shows, err = probe(u)
    if err:
        print('  [取得失敗]', err)
        # 兄弟券種を探す（P021001 -> P021002..004）
        m = re.search(r'(P021)(\d{3})$', u)
        if m:
            for n in range(1, 5):
                alt = u[:m.start(2)] + '%03d' % n
                if alt == u:
                    continue
                time.sleep(2)
                s2, e2 = probe(alt)
                if not e2 and s2:
                    print('  ▶兄弟券種 %s' % alt)
                    for sh in s2:
                        alive = [t for t in sh['tickets'] if t['status'] != '受付終了']
                        print('     %s %s 受付終了でない枠 %d' % (sh['date'], sh['venue'], len(alive)))
                        for t in alive:
                            print('       [%s] %s | %s' % (t['status'], t['name'], t['period']))
    else:
        for sh in shows:
            print('  ▼%s %s（%s）' % (sh['date'], sh['venue'], sh['pref']))
            for t in sh['tickets']:
                print('     [%s] %s | %s' % (t['status'], t['name'], t['period']))
    time.sleep(3)
