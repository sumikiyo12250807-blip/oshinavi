# -*- coding: utf-8 -*-
"""feedback_x_paste_powershell_only に「タブが背面だと貼れない」を書き足す。

2026-09-10に3回失敗した。原因は**拡張が操作するタブがタブグループの中にあって、
Chromeのアクティブタブと別だった**こと。Ctrl+Vはアクティブなところにしか届かない。
"""
import io

p = ('C:/Users/user/.claude/projects/C--Users-user-oshinavi/memory/'
     'feedback_x_paste_powershell_only.md')
s = io.open(p, encoding='utf-8').read()

anchor = '# やること（先に書く）'

add = '''# 🚨🚨【2026-09-10・**refクリックを挟むと貼れない。`n` で開いてすぐ貼る**】

3回続けて「Ctrl+Vを送ったのに本文欄が空（字数1）」になった。

## 真因＝**拡張のタブが「タブグループ」の中にあって、Chromeのアクティブタブと別だった**

- `tabs_context_mcp` が返すのは **tabGroupId の中のタブだけ**。
  ユーザーが見ている OSHINAVI のタブは**その一覧に出てこない**
- `Get-Process chrome | MainWindowTitle` は**アクティブタブの題**を返す＝OSHINAVIだった
- **Ctrl+V はアクティブなタブにしか届かない**ので、拡張が見ている X のタブは空のまま
- `javascript_tool` で `document.visibilityState` を見ると **`hidden`**。これが目印

## ✅ 通った手順（キーボードだけで完結させる）

```
1. Get-Content -Raw -Encoding UTF8 tmp/xp<日付>/NN.txt | Set-Clipboard
2. tmp/x_focus_and_paste.ps1 -Match "Home / X" -NoPaste
     … Chromeを前面に出し、Ctrl+Tab を回してタイトルが合うタブで止める
       🚨composeはモーダルなのでタイトルは "compose" でなく **"Home / X"**
3. tmp/x_compose_paste.ps1
     … Esc → **n**（Xの新規投稿ショートカット）→ Ctrl+V
       **`n` が本文欄にカーソルを置いてくれる**ので、refクリックが要らない
4. javascript_tool で `div[data-testid="tweetTextarea_0"]` の innerText.length を読む
```

🚨**本文欄を `ref` でクリックしてからPowerShellを呼ぶと、その間にフォーカスが飛ぶ**。
　 2026-09-03のmemoryにある「refでクリック→貼る」は**タブが前面のときだけ通る**。

## 予約画面は `form_input` より **JSのnative setter** が速い

```js
function setSel(sel, val) {
  const setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
  setter.call(sel, val);
  sel.dispatchEvent(new Event('change', { bubbles: true }));
}
const s = [...document.querySelectorAll('select')];
setSel(s[3], '20');   // Hour   （s[0]=Month s[1]=Day s[2]=Year s[3]=Hour s[4]=Minute）
setSel(s[4], '16');   // Minute
```
そのあと `document.body.innerText.match(/Will send on[^\\n]*/)` で**時刻を機械で確かめる**。
Confirm と Schedule も `innerText === 'Confirm'` / `=== 'Schedule'` で拾って click() する
＝**押す前に文字を確かめている**ことになる（[[feedback_x_browser_operation]] の取り違え防止）。

📊 この形で **5本を約20分**（1本4分→1本約4分のまま。失敗の3回を除けば速い）。

---

'''

assert anchor in s and '2026-09-10' not in s
io.open(p, 'w', encoding='utf-8').write(s.replace(anchor, add + anchor, 1))
print('feedback_x_paste_powershell_only.md に2026-09-10の手順を追記')
