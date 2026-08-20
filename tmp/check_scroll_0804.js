// index.html の inline <script> を実物のまま切り出して構文チェックし、
// 追加した scrollToResults の配線（input/keydown/サジェスト）が入っているか実物で確認する。
const fs = require('fs');
const vm = require('vm');
const h = fs.readFileSync('index.html', 'utf8');

const blocks = [...h.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let ok = 0;
blocks.forEach((b, i) => {
  try {
    new vm.Script(b);   // 構文エラーならここで落ちる
    ok++;
  } catch (e) {
    console.log(`SCRIPT#${i} 構文エラー: ${e.message}`);
  }
});
console.log(`inline script ${ok}/${blocks.length} 構文OK`);

const need = [
  ['ヘルパー定義', /function scrollToResults\(delay\)/],
  ['result-meta を目標にしている', /querySelector\("\.result-meta"\)/],
  ['入力時に呼ぶ(デバウンス350ms)', /if \(searchQuery\) scrollToResults\(350\); else clearTimeout\(scrollTimer\);/],
  ['Enterで即スクロール', /e\.key === "Enter"[\s\S]{0,120}scrollToResults\(0\)/],
  ['サジェスト選択で即スクロール', /suggest\.classList\.remove\("open"\);\s*[\r\n]+\s*scrollToResults\(0\);/],
];
for (const [name, re] of need) console.log(`${re.test(h) ? 'OK  ' : 'NG  '}${name}`);

// スクロール先の要素が本当に存在するか（HTML側）
console.log(`${/<div class="result-meta">/.test(h) ? 'OK  ' : 'NG  '}.result-meta がHTMLに在る`);
