# -*- coding: utf-8 -*-
"""zb35の35件をぴあキーワード検索(rlsInfo.do?kw=)で総ざらい。
「登録したeventCdは0枠だが、ぴあに別のeventCdで生き枠がある」型（feedback_pia_bundle_hides_shows）を拾う。"""
import subprocess, sys, io, time, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

KW = [
 (1554,'高嶋ちさ子'),(1601,'藍井エイル'),(2748,'熊本地震10年復興コンサート'),(3473,'AA＝'),
 (3509,'田辺花火大会'),(3696,'Stray Kids'),(4035,'紫 今'),(4036,'Little Parade'),
 (4050,'Bray me'),(4051,'K-Drama OST'),(4057,'Faulieu'),(4066,'新サクラ大戦'),
 (4080,'澤野弘之'),(4081,'梅田サイファー'),(4083,'汐れいら'),(4089,'花宮初奈'),
 (4094,'KAWAII LAB'),(4098,'高木いくの'),(4100,'Khalid'),(4106,'徹子の部屋'),
 (4114,'Yung Kai'),(4115,'THE MACKSHOW'),(4117,'RAINCOVER'),(4150,'FIVE O ONE'),
 (4156,'IRIS MONDO'),(4159,'わーすた'),(4163,'中本こまり'),(4165,'TAKERU'),
 (4167,'Ken Yokoyama'),(4172,'Bocchi'),(4175,'THE PREDATORS'),(4422,'yeti let you notice'),
 (4423,'The Performance Zero'),(4424,'シャッポ'),(4425,'スミワタルトリオ'),
]
os.makedirs('tmp/zbkw', exist_ok=True)
for eid, kw in KW:
    out = 'tmp/zbkw/%d.txt' % eid
    try:
        r = subprocess.run([sys.executable, 'tools/pia_kw_search.py', kw, '--out', out],
                           capture_output=True, timeout=240)
        print('id=%d kw=%s rc=%d' % (eid, kw, r.returncode))
        if r.returncode != 0:
            print('   stderr=%s' % r.stderr.decode('utf-8','replace')[-300:])
    except Exception as e:
        print('id=%d ERR %r' % (eid, e))
    time.sleep(4.0)
