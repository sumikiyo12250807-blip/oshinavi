import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
P = r'C:\Users\user\.claude\projects\C--Users-user-oshinavi\memory\MEMORY.md'
lines = open(P, encoding='utf-8').read().split('\n')
NEW = {
64: '- 🚨🚨 [**締切の縛りは外した・朝のスイープに受付中(0101)も回す**](feedback_harvest_source_order_and_far_deadline.md)（2026-09-07）／[「4日以上」は順番であって捨てる話ではない](feedback_harvest_countdown_first.md)',
68: '- 🚨🚨 [ぴあ以外も機械ゲートを通したら**新着タブに投入**・確認用の表は作らない](feedback_nonpia_user_eyes_until_gate.md)／🚨🚨[確認はOSHINAVIの実物で＝ぴあ以外の振り分けだけユーザー確認後](feedback_check_on_oshinavi_not_tables.md)',
76: '- 🚨🚨 [ぴあの「当日券発売中」は販売期間を書かない＝買える枠が消える](feedback_pia_toujitsuken_when_empty.md)（受け皿は`parse_when_row`の1か所／`[貸切公演]`は静かに落とす）',
}
before = len('\n'.join(lines))
for n, s in NEW.items():
    key = s.split('](')[1].split(')')[0]
    assert key in lines[n - 1], (n, key)
    lines[n - 1] = s
txt = '\n'.join(lines)
open(P, 'w', encoding='utf-8', newline='').write(txt)
print('文字数', before, '→', len(txt))
