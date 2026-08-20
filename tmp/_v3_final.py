import re, json, sys, os, subprocess
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
def load(t): return json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', t, re.S).group(2))
def show(r): return subprocess.run(['git','show',r+':index.html'],capture_output=True).stdout.decode('utf-8')

revs = ['7219f83^','7219f83','a17e3aa','9ae6eb5','483533f','8ebfcf0','6f73da7','53f02f5','f7df8b4']
prev = None; prevname=None
for r in revs:
    e = load(show(r)); ids = set(x['id'] for x in e)
    line = "%-10s EVENTS=%d" % (r, len(e))
    if prev is not None:
        gone = sorted(prev-ids); add = sorted(ids-prev)
        line += "  削除%d 追加%d" % (len(gone), len(add))
        if gone: line += " 削除id=%s" % gone[:40]
    print(line); prev = ids
cur = load(open('index.html',encoding='utf-8',newline='').read())
ids = set(x['id'] for x in cur)
print("WORKTREE   EVENTS=%d  削除%d 追加%d" % (len(cur), len(prev-ids), len(ids-prev)))

# 今日のコミットで tickets が減ったエントリ
base = {x['id']: x for x in load(show('6f73da7'))}
now = {x['id']: x for x in cur}
print("\n■ 6f73da7→現在 で tickets が減ったエントリ")
for i, e in now.items():
    b = base.get(i)
    if b and len(b.get('tickets') or []) > len(e.get('tickets') or []):
        print("  id%s %s: %d枠→%d枠" % (i, e.get('artist'), len(b['tickets']), len(e['tickets'])))
        for t in b['tickets']:
            if t not in e['tickets']: print("     消えた枠:", json.dumps(t, ensure_ascii=False))

# renderCard シミュレーション（1149と2300）
TODAY='2026-08-14'
print("\n■ カード表示シミュレーション")
for i in (1149, 2300, 2223, 2265):
    e = now[i]
    print("  --- id%s %s (公演日=%s)" % (i, e.get('artist'), e.get('date')))
    for t in e['tickets']:
        if t.get('soldout'):
            lab = '販売終了' if t.get('saleEnded') else '予定枚数終了'
        elif t.get('startDate') and t['startDate']==TODAY and t['startDate']!=t.get('date'):
            lab = '本日発売（〜%s）' % t['date']
        elif t.get('startDate') and t['startDate']>TODAY:
            lab = '発売開始まであと%d日' % 0
        elif (t.get('date') or '') < TODAY:
            lab = '(非表示)'
        else:
            lab = '販売中（〜%s）' % t.get('date')
        print("      %-18s %s" % (lab, t.get('type')))
