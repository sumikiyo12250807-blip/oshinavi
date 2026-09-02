# -*- coding: utf-8 -*-
"""e+152件の振り分けを logs/assigned_2026-09-02.md に追記する。
新着タブから消える代わりの「後から見る場所」（feedback_new_pool_ok_before_assign）。"""
import re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

hold = [int(x) for x in open('tmp/eplus_hold_ids_0902.txt').read().split(',') if x.strip()]
h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}

agent = {}
for ln in open('tmp/eplus_genre_agent_0902.md', encoding='utf-8'):
    m = re.match(r'^\|\s*(\d{3,5})\s*\|(.*?)\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|', ln)
    if m:
        agent[int(m.group(1))] = (m.group(3).strip(), m.group(4).strip())

rows = [(i, by[i]) for i in agent if i in by and by[i].get('genre') != 'new' and i not in hold]
rows.sort()
c = collections.Counter(e.get('genre') for _, e in rows)

L = ['', '---', '', '## 追記：e+の152件を振り分けた（2026-09-02 夜）', '',
     'ユーザーが新着タブで目視確認して「ざっと数字の間違いはなさそう」→ 明示のGOをもらって実行。', '',
     '**ジャンルの決め方**＝e+にはぴあのようなカテゴリが無いので「ぴあの言う通りに写す」が使えない。',
     '機械の名前fallbackは engeki に90件（＝判定できなかったものの受け皿）が落ちて使い物にならなかったので、',
     '**別エージェントに会場と名前をゼロから見せて判定させ、その結果を採用した**（必要な分は実際に検索して裏取り）。', '',
     '内訳＝' + ' / '.join(f'{k} {v}' for k, v in c.most_common()), '',
     '| id | 公演名 | ジャンル | 会場 | 判定の根拠 |', '|---|---|---|---|---|']
for i, e in rows:
    g, why = agent.get(i, ('', ''))
    L.append(f"| {i} | {e.get('artist','')[:40]} | {e.get('genre')} | "
             f"{(e.get('venue') or '')[:26]} | {why[:44]} |")

L += ['', f'計 {len(rows)}件', '',
      '### ⚠️判定できず、振り分けずプールに残した10件', '',
      '| id | 公演名 | なぜ決められなかったか |', '|---|---|---|']
for i in hold:
    e = by.get(i)
    _, why = agent.get(i, ('', ''))
    L.append(f"| {i} | {(e.get('artist') if e else '')[:40]} | {why[:60]} |")
L += ['', '大半は「大学の学園祭のゲストらしいが、出演が確定した告知を見つけられなかった」もの。',
      'あとは音楽イベントかトーク企画か決め手が無かったもの。**推測で振り分けない**。', '',
      '### 今日投入したぴあの87件は振り分けていない', '',
      '新着50件は**投入した翌日に再チェックを通してから**の決まり（PLAYBOOK）。9/3の朝の便で処理する。']
open('logs/assigned_2026-09-02.md', 'a', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print(f'追記した {len(rows)}件 / 保留 {len(hold)}件')
