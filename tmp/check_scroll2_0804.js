// 「Enterと候補クリックの時だけスクロール」になっているかを実物で確認する。
const fs = require('fs');
const vm = require('vm');
const h = fs.readFileSync('index.html', 'utf8');

const blocks = [...h.matchAll(/<script(?![^>]*\bsrc=)(?![^>]*ld\+json)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let ok = 0;
blocks.forEach((b, i) => {
  try { new vm.Script(b); ok++; } catch (e) { console.log(`SCRIPT#${i} 構文エラー: ${e.message}`); }
});
console.log(`JS(ld+json除く) ${ok}/${blocks.length} 構文OK`);

const checks = [
  ['入力中のスクロールは無い', !/scrollToResults\(350\)/.test(h)],
  ['Enterで動く', /e\.key === "Enter"[\s\S]{0,140}scrollToResults\(0\)/.test(h)],
  ['候補クリックで動く', /suggest\.classList\.remove\("open"\);\s*[\r\n]+\s*scrollToResults\(0\);/.test(h)],
  ['ヘルパーは残っている', /function scrollToResults\(delay\)/.test(h)],
  ['scrollToResultsの呼び出しは2回だけ', (h.match(/scrollToResults\(/g) || []).length === 3],  // 定義1+呼出2
];
for (const [name, pass] of checks) console.log(`${pass ? 'OK  ' : 'NG  '}${name}`);
