# -*- coding: utf-8 -*-
"""7/12 期限切れ救済変換：check_expired⚠️のうちreconcileでMISSING/DROPだったidをぴあ再build。
tickets のみ置換。--apply で index.html に反映。"""
import re, json, sys, time, datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'tools')
from build_pia_entries import build

IDS = [1036, 1249, 1577, 1870, 771, 1355]
OUT = 'tmp/rescue_0712.json'
TODAY = datetime.date.today().isoformat()


def load_events(h):
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    return m, json.loads(m.group(2))


def pia_urls(ev):
    urls = []
    p = (ev.get('links') or {}).get('pia')
    if p and 'pia' in p:
        urls.append(p)
    for t in ev.get('tickets', []):
        u = t.get('url')
        if u and 'pia' in u and u not in urls:
            urls.append(u)
    return urls


def main():
    h = open('index.html', encoding='utf-8').read()
    m, EVENTS = load_events(h)
    byid = {e['id']: e for e in EVENTS}

    if '--apply' in sys.argv:
        built = {o['id']: o for o in json.load(open(OUT, encoding='utf-8'))}
        changed = 0
        for i, o in built.items():
            if o.get('status') == 'convert' and o.get('tickets'):
                byid[i]['tickets'] = o['tickets']
                changed += 1
        bak = f'index.html.bak_{datetime.date.today():%m%d}_rescue'
        open(bak, 'w', encoding='utf-8').write(h)
        new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
        open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
        print(f'=== {changed}件 適用 (backup: {bak}) ===')
        return

    out = []
    for n, i in enumerate(IDS, 1):
        ev = byid[i]
        urls = pia_urls(ev)
        try:
            ne = build({'newid': i, 'artist': ev.get('artist', ''), 'urls': urls})
        except Exception as ex:
            out.append({'id': i, 'status': 'ERROR', 'artist': ev.get('artist', ''), 'err': str(ex)[:120]})
            print(f'[{n}/{len(IDS)}] {i} ERROR {str(ex)[:60]}'); time.sleep(2.0); continue
        if ne is None:
            out.append({'id': i, 'status': 'delete', 'artist': ev.get('artist', ''), 'urls': urls})
            print(f'[{n}/{len(IDS)}] {i} {ev.get("artist","")[:20]} 買える枠ゼロ→削除候補')
        else:
            ts = ne['tickets']
            out.append({'id': i, 'status': 'convert', 'artist': ev.get('artist', ''), 'tickets': ts})
            desc = ' / '.join(f"{t.get('type','')}〜{t.get('date','')}" for t in ts)
            print(f'[{n}/{len(IDS)}] {i} {ev.get("artist","")[:20]} convert {len(ts)}枠: {desc}')
        time.sleep(1.2)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== 完了 → ' + OUT + ' (適用は --apply) ===')


if __name__ == '__main__':
    main()
