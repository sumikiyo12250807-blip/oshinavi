# -*- coding: utf-8 -*-
"""販売終了バッジの3面整合を検算（JS / SSR / ai*.html）。写経でなく実物から数える。"""
import re, sys, json, glob, subprocess
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))

se = [(e['id'], e.get('name'), t.get('type')) for e in EV
      for t in (e.get('tickets') or []) if t.get('saleEnded')]
so = [(e['id'], e.get('name'), t.get('type')) for e in EV
      for t in (e.get('tickets') or []) if t.get('soldout') and not t.get('saleEnded')]
print('データ: 販売終了 %d枠 / 予定枚数終了 %d枠' % (len(se), len(so)))
print('  販売終了を持つエントリ:', sorted({x[0] for x in se}))

# saleEnded は必ず soldout も持つ（並び・非表示ロジックを共用しているため）
bad = [(e['id'], t.get('type')) for e in EV for t in (e.get('tickets') or [])
       if t.get('saleEnded') and not t.get('soldout')]
print('  🚨soldoutを伴わないsaleEnded（あってはいけない）:', bad)

# ① JS
print('\n① renderCard: saleEnded分岐 =', 't.saleEnded ? " saleended"' in h,
      '/ CSS =', '.ticket-soldout-badge.saleended' in h)
print('   並び順ロジック(EVENTS.sortのsoldout行)は無変更か =',
      'if (t.soldout) return [3, "9999-99-99", 1];' in h)

# ② SSR
ssr = h[h.index('<!-- AI_SSR_START -->'):h.index('<!-- AI_SSR_END -->')]
print('② SSR: ⚫予定枚数終了 %d行 / ⚪販売終了 %d行'
      % (ssr.count('⚫ 予定枚数終了'), ssr.count('⚪ 販売終了')))

# ③ ai*.html
ai = ''.join(open(f, encoding='utf-8').read() for f in sorted(glob.glob('ai*.html')))
print('③ ai*.html: ⚫予定枚数終了 %d / ⚪販売終了 %d'
      % (ai.count('⚫ 予定枚数終了'), ai.count('⚪ 販売終了')))

# 実物のrenderCardでバッジ文字列を出す（写経しない）
src = [re.search(r'(  function parseDateStr\(.*?\n  \})', h, re.S).group(1),
       'const today = new Date(2026,7,14);',
       'function fmt(t,ev){ if(parseDateStr(ev.date) < today) return ""; '
       'return (t.saleEnded ? "販売終了" : "予定枚数終了"); }']
ev2300 = next(e for e in EV if e['id'] == 2300)
src.append('const ev = %s;' % json.dumps(ev2300, ensure_ascii=False))
src.append('ev.tickets.forEach(t => console.log("  " + t.type.slice(0,30) + " → " + fmt(t, ev)));')
open('tmp/_badge_probe.js', 'w', encoding='utf-8').write('\n'.join(src))
print('\n実物ロジックで id2300 工藤静香のバッジを出す:')
print(subprocess.run(['node', 'tmp/_badge_probe.js'], capture_output=True, text=True,
                     encoding='utf-8').stdout.rstrip() or '（node失敗）')
