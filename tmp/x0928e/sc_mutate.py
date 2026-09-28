import sys, json, copy, subprocess, re, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT = 'C:/Users/user/oshinavi/'
R = ROOT + 'tmp/x0928e/'
sel = json.load(open(R + 'sc_sel.json', encoding='utf-8'))
E = {s['entry']['links']['livepocket'].split('/e/')[1]: s['entry'] for s in sel}
def g(slug): return copy.deepcopy(E[slug])
def tk(e, pred): return [t for t in e['tickets'] if pred(t)]
M = []
def add(name, e): M.append((name, e))
# baseline (correct entries only) - should be clean
e = g('z96to'); e['tickets'][0]['date'] = '2026-10-02'; add('M01 締切を1日ずらす(date)', e)
e = g('z96to'); e['tickets'][0]['type'] = e['tickets'][0]['type'].replace('〜10/3 19:00', '〜10/2 19:00'); add('M02 表記の締切だけずらす(type)', e)
e = g('cbico'); e['tickets'][0].pop('soldout'); e['tickets'][0].pop('soldoutSince', None); add('M03 soldoutを消す', e)
e = g('waltick02'); t = e['tickets'][0]; t.pop('saleEnded'); t.pop('saleEndedSince', None); add('M04 saleEndedを消す', e)
e = g('s4389'); e['tickets'] = e['tickets'][:1]; add('M05 受付の枠を1つ消す', e)
e = g('2newsong'); e['tickets'].append(copy.deepcopy(e['tickets'][1])); add('M06 枠を1つ増やす(複製)', e)
e = g('261104'); e['prefecture'] = '神奈川'; add('M07 県を変える', e)
e = g('diabell_1027_1'); e['venue'] = 'holiday nagoya'; add('M08 会場を変える', e)
e = g('k1oba'); e['tickets'][0].pop('startDate'); add('M09 販売前のstartDateを消す', e)
e = g('261104'); e['tickets'][0]['startDate'] = '2026-09-28'; add('M10 販売中にstartDateを足す', e)
e = g('diabell_1027_1'); e['date'] = '2026-09-20'; e['dateLabel'] = '2026年9月20日(日) 15:15開演'; add('M11 公演日を過去に', e)
e = g('z96to'); t = copy.deepcopy(e['tickets'][0]); t['type'] = '出店者エントリー受付（東京 10/3 19:00公演）〜10/3 19:00'; e['tickets'].append(t); add('M12 出す側の受付名の枠を足す', e)
e = g('qw5jm'); e['tickets'] = [t for t in e['tickets'] if '7_0z2' not in t['url']]; add('M13 畳んだエントリから1ページ分の枠を消す', e)
e = g('csd1127_1'); e['tickets'][0]['startDate'] = '2026-10-08'; add('M14 startDateを1日ずらす', e)
e = g('0jiob'); e['dateLabel'] = '2026年11月4日(水)〜11月15日(日)'; add('M15 dateLabelの初日をずらす', e)
e = g('k1oba'); e['tickets'][0]['soldout'] = True; add('M16 販売前の枠にsoldout', e)
e = g('261104'); e['tickets'][0]['soldout'] = True; add('M17 販売中の枠にsoldout', e)
e = g('qw5jm'); t = e['tickets'][0]; t.pop('soldout'); t.pop('soldoutSince', None); add('M18 畳んだエントリの売切枠からsoldoutを消す', e)
e = g('qw5jm'); a, b = e['tickets'][1], e['tickets'][2]; a['url'], b['url'] = b['url'], a['url']; add('M19 畳んだエントリで枠のURLを入れ替える', e)
e = g('bmo202609'); e['date'] = '2026-09-29'; add('M20 会期の最終日(date)を1日早める', e)
e = g('shogo261124'); e['tickets'][1]['date'] = '2026-11-24'; add('M21 販売前の締切を公演日側へずらす', e)
e = g('i0t7o'); e['tickets'][0]['date'] = '2026-09-30'; add('M22 販売前の締切を発売日で作る(date=startDate)', e)
e = g('s5kfm'); e['tickets'] = e['tickets'][1:]; add('M23 FC先行の枠を消す', e)
e = g('mei-chan2026'); e['tickets'] = e['tickets'][:3]; add('M24 販売終了の枠を消す', e)
BASE = [('B00 無変更の正しい件（誤検知の確認）', [copy.deepcopy(E[k]) for k in ['z96to','s4389','cbico','k1oba','csd1127_1','2newsong','waltick02','wqttx','261104','diabell_1027_1','0jiob','hanamibukifes20261105','bxlfm','qhli7','6hpik','mei-chan2026','i0t7o','shogo261124','s5kfm','oiy_g','m5twd','bmo202609','20261214','mkxcx','meltiq26-10-07']])]
os.makedirs(R + 'sc_mut', exist_ok=True)
res = []
for name, ents in BASE + [(n, [e]) for n, e in M]:
    tag = name.split()[0]
    fj = R + f'sc_mut/{tag}.json'; fr = R + f'sc_mut/{tag}_report.txt'
    json.dump({'entries': ents}, open(fj, 'w', encoding='utf-8'), ensure_ascii=False)
    p = subprocess.run([sys.executable, ROOT + 'tools/gate_livepocket_indep.py', '--built', fj, '--sleep', '3', '--html-dir', R + 'sc_gate_html', '--report', fr], cwd=ROOT, capture_output=True)
    rep = open(fr, encoding='utf-8').read() if os.path.exists(fr) else ''
    items = re.findall(r'項目: (.+)', rep)
    res.append((name, p.returncode, items))
    print(f'{name}\texit={p.returncode}\t{len(items)}\t' + ' | '.join(items[:4]))
