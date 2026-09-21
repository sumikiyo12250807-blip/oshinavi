# -*- coding: utf-8 -*-
"""ZAIKOの作り直しで枠がどう変わったかを、投入直前のバックアップと今の現物で見比べる。
帰ってから画面で見るときの「どこが直ったか」の手引きにする。
"""
import io, json, re, sys, collections

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
BAK = 'index.html.bak_0921_prezaikorebuild'


def events(path):
    h = io.open(path, encoding='utf-8', newline='').read()
    return {e['id']: e for e in json.loads(
        re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}


old = events(BAK)
new = events('index.html')
ids = sorted(i for i, e in new.items() if (e.get('links') or {}).get('zaiko'))

out = io.open('tmp/x0921/zaiko_beforeafter.txt', 'w', encoding='utf-8')
cnt = collections.Counter()
for i in ids:
    o, n = old.get(i), new[i]
    if not o:
        cnt['新しく入った'] += 1
        continue
    ot = [t.get('type') or '' for t in (o.get('tickets') or [])]
    nt = [t.get('type') or '' for t in (n.get('tickets') or [])]
    if ot == nt:
        cnt['変わらない'] += 1
        continue
    cnt['直った'] += 1
    # 数字でも押さえる
    cnt['枠が増えた'] += 1 if len(nt) > len(ot) else 0
    cnt['枠が減った'] += 1 if len(nt) < len(ot) else 0

# 「販売中（締切不明）」がどれだけ減ったか／券種名が「チケット」だけの枠がどれだけ減ったか
def measure(src, label):
    ev = [e for e in src.values() if (e.get('links') or {}).get('zaiko')]
    unk = sum(1 for e in ev for t in (e.get('tickets') or []) if t.get('saleEndUnknown'))
    plain = sum(1 for e in ev for t in (e.get('tickets') or [])
                if re.match(r'^(チケット|抽選チケット)(（\d+）)?（', t.get('type') or ''))
        # 「チケット（…」「抽選チケット（2）（…」＝名前が無い枠
    sold = sum(1 for e in ev for t in (e.get('tickets') or []) if t.get('soldout'))
    sended = sum(1 for e in ev for t in (e.get('tickets') or []) if t.get('saleEnded'))
    pre = sum(1 for e in ev for t in (e.get('tickets') or []) if t.get('startDate'))
    z = sum(1 for e in ev for t in (e.get('tickets') or []) if '00:00公演' in (t.get('type') or ''))
    park = sum(1 for e in ev for t in (e.get('tickets') or []) if '駐車' in (t.get('type') or ''))
    tot = sum(len(e.get('tickets') or []) for e in ev)
    out.write('%s（%dエントリ / %d枠）\n' % (label, len(ev), tot))
    out.write('  締切不明「販売中」    %5d枠\n' % unk)
    out.write('  券種名が無い枠        %5d枠\n' % plain)
    out.write('  予定枚数終了          %5d枠\n' % sold)
    out.write('  販売終了(saleEnded)   %5d枠\n' % sended)
    out.write('  発売前(startDate)     %5d枠\n' % pre)
    out.write('  「00:00公演」         %5d枠\n' % z)
    out.write('  駐車券                %5d枠\n\n' % park)


out.write('=== ZAIKOの作り直し 前後の数字 ===\n\n')
measure(old, '◆前（投入時）')
measure(new, '◆後（作り直し）')
out.write('エントリ単位: %s\n\n' % dict(cnt))

out.write('=== 直った見本（先頭8件）===\n')
shown = 0
for i in ids:
    o, n = old.get(i), new[i]
    if not o:
        continue
    ot = [t.get('type') or '' for t in (o.get('tickets') or [])]
    nt = [t.get('type') or '' for t in (n.get('tickets') or [])]
    if ot == nt:
        continue
    out.write('--- id%s %s @ %s\n' % (i, (n.get('name') or '')[:40], (n.get('venue') or '')[:20]))
    for x in ot[:4]:
        out.write('    前: %s\n' % x[:72])
    for x in nt[:4]:
        out.write('    後: %s\n' % x[:72])
    shown += 1
    if shown >= 8:
        break
out.close()
print('wrote tmp/x0921/zaiko_beforeafter.txt  %s' % dict(cnt))
