# -*- coding: utf-8 -*-
"""今朝のビルド結果を「新着に投入」と「既存に足す（統合）」に分ける（2026-09-11）。

・既存ツアーに足す（部分一致チェックで見つけた分）:
    7856【当日引換券】氷川きよし→762 ／ 7860【当日引換券】山崎育三郎→802 ／
    7895 ウィーン・J.シュトラウス管 ニューイヤー2027→1776 ／ 7918 siruko ファンミ→4258 ／
    7841 あつこ&タニケン ハッピードレミハウス（ツアー）→7508 ／ 7903 トリオ・カルディア→2016
・統合行きで相手が決まらなかった分（仮id 9001〜）:
    9001・9002 川崎鷹也（福岡3/28・長崎4/4）→4227 ／ 9005 島津亜矢→710 ／ 9006 西村由紀江→727 ／
    9009 山内惠介（札幌のディナーショー）→177
    9003 OZアカデミー（宮古島1/24）・9004 新日本プロレス（福島11/24）＝別の興行なので新規
    ⏸ 9007 ズーカラデル（10/24福岡）・9008 TSUKEMEN（12/15渋谷）＝既存ツアーの会期の外で決め切れない＝保留
・ミラクルドリームサーカス両毛足利公演の月別4件（7923〜7926）は長期公演なので1エントリに畳む（[[feedback_longrun_event]]）
🚨足す枠には、その枠のページのURLを先に焼き込む（merge_with_urls は同じ相手に2件来るとURLを取り違える）
出力: tmp/inject_0911.json ／ tmp/built_mergeX_0911.json ／ tmp/cand_mergeX_0911.json
"""
import datetime, io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
WD = '月火水木金土日'


def jp(s):
    y, m, d = map(int, s.split('-'))
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


fresh = json.load(io.open('tmp/built_0911_fresh.json', encoding='utf-8-sig'))
held = json.load(io.open('tmp/built_held_0911.json', encoding='utf-8-sig'))
MERGE = {7856: 762, 7860: 802, 7895: 1776, 7918: 4258, 7841: 7508, 7903: 2016,
         9001: 4227, 9002: 4227, 9005: 710, 9006: 727, 9009: 177}
NEW_FROM_HELD = [9003, 9004]
CIRCUS = [7925, 7924, 7926, 7923]  # 10月・11月・12月・1月

by = {e['id']: e for e in fresh + held}
mergeb, mergec = [], []
for src, dst in MERGE.items():
    e = json.loads(json.dumps(by[src]))
    url = (e.get('links') or {}).get('pia')
    for t in e.get('tickets') or []:
        t['url'] = t.get('url') or url
    e['id'] = dst
    mergeb.append(e)
    mergec.append({'newid': dst, 'artist': e.get('artist'), 'urls': [url]})

# サーカスを1エントリに
base = json.loads(json.dumps(by[CIRCUS[0]]))
base['name'] = base['artist'] = 'ミラクルドリームサーカス両毛足利公演'
tix = []
for cid in CIRCUS:
    c = by[cid]
    u = (c.get('links') or {}).get('pia')
    for t in c.get('tickets') or []:
        t = dict(t)
        t['url'] = t.get('url') or u
        tix.append(t)
base['tickets'] = tix
d0 = '2026-10-09'
d1 = max(by[c]['date'] for c in CIRCUS)
base['date'] = d1
base['dateLabel'] = '%s〜%s 栃木 足利赤十字病院 東側 大テント特設会場' % (jp(d0), jp(d1))

inject = []
skip = set(MERGE) | set(CIRCUS)
for e in fresh:
    if e['id'] in skip:
        continue
    inject.append(e)
inject.append(base)
nid = max(e['id'] for e in fresh) + 1
for hid in NEW_FROM_HELD:
    e = json.loads(json.dumps(by[hid]))
    e['id'] = nid
    nid += 1
    inject.append(e)
inject.sort(key=lambda e: e['id'])

json.dump(inject, io.open('tmp/inject_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mergeb, io.open('tmp/built_mergeX_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mergec, io.open('tmp/cand_mergeX_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('投入 %d件（id %d〜%d）／ 既存に足す %d件 ／ サーカス4件→id%d に畳んだ（%s〜%s・%d枠）'
      % (len(inject), inject[0]['id'], inject[-1]['id'], len(mergeb), base['id'], d0, d1, len(tix)))
