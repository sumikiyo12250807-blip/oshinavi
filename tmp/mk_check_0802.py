# -*- coding: utf-8 -*-
"""check_order.js の実物をそのまま使い、8/2グループの並びを出す検証スクリプトを作る。
写経はしない＝index.html の sort/classify を eval している本体は一切いじらず、
末尾に「8/2グループを列挙する」ブロックを足すだけ。"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = r"C:\Users\user\oshinavi\tools\check_order.js"
OUT = r"C:\Users\user\oshinavi\tmp\check_0802_group.js"

src = open(SRC, encoding="utf-8").read()

extra = """

// ---- 追加検証：8/2グループの並び（EVENTS はこの時点で実物の sort 済み）----
for (const TARGET of ['2026-08-01', '2026-08-02']) {
  console.log(`\\n--- ${TARGET} グループの並び（上から） ---`);
  let n = 0;
  for (const ev of EVENTS) {
    const c = classify(ev);
    if (c.key !== TARGET) continue;
    n++;
    const mark = ev.xPost ? `★X(${ev.xPost})` : '        ';
    console.log(`  ${String(n).padStart(3)} ${mark}  ${KIND[c.kind]}  ${(ev.name || '').slice(0, 40)}`);
    if (n >= 22) { console.log('  … 以下略'); break; }
  }
  if (n === 0) console.log('  （該当なし）');
}

// 8/1グループのうち「締切🟢」だけを先頭から（VISION FESTAの位置確認用）
console.log('\\n--- 2026-08-01 の「締切🟢」サブグループ 先頭6件 ---');
let m = 0;
for (const ev of EVENTS) {
  const c = classify(ev);
  if (c.key !== '2026-08-01' || c.kind !== 1) continue;
  m++;
  const mark = ev.xPost ? `★X(${ev.xPost})` : '        ';
  console.log(`  ${String(m).padStart(3)} ${mark}  ${KIND[c.kind]}  ${(ev.name || '').slice(0, 40)}`);
  if (m >= 6) break;
}
if (m === 0) console.log('  （該当なし）');
"""

ANCHOR = "if (viol || same || rankViol || missingTodayPresale) process.exit(2);"
assert ANCHOR in src, "終了処理のアンカーが見つからない"
out = src.replace(ANCHOR, extra + "\n" + ANCHOR)

open(OUT, "w", encoding="utf-8", newline="\n").write(out)
print("wrote %s（process.exit の手前に検証ブロックを挿入）" % OUT)
