# -*- coding: utf-8 -*-
"""過去のセッション記録から、許可リストに入れる価値のある「読み取りだけ」の操作を数える。

🚨 入れてはいけないもの（任意のコードが動くから）＝
   python / node / bun / bash / sh / npx / PowerShell の中身 / make / gh api など。
   これらは何度出てきても除外する。
🚨 Claude Code が最初から許可しているもの（ls / cat / git status / grep など）も除外する。
"""
import json, io, os, re, collections, glob

DIR = r"C:\Users\user\.claude\projects\C--Users-user-oshinavi"
files = sorted(glob.glob(os.path.join(DIR, "*.jsonl")), key=os.path.getmtime, reverse=True)[:50]

# 最初から許可されている（=小窓が出ない）ので入れない
AUTO_OK = set("""cal uptime cat head tail wc stat strings hexdump od nl id uname free df du locale
groups nproc basename dirname realpath cut paste tr column tac rev fold expand unexpand fmt comm
cmp numfmt readlink diff true false sleep which type expr seq tsort pr echo ls cd pwd whoami alias
xargs file sed sort man help netstat ps base64 grep egrep fgrep sha256sum sha1sum md5sum tree date
hostname lsof pgrep tput ss fd fdfind aki rg jq uniq history arch ifconfig pyright find printf test
git gh docker""".split())

# 任意のコードが動くので絶対に入れない
NEVER = set("""python python3 node bun deno ruby perl php lua bash sh zsh fish eval exec ssh npx bunx
uvx uv npm yarn pnpm make just cargo go powershell pwsh cmd sudo curl wget""".split())

bash = collections.Counter()
mcp = collections.Counter()
n_calls = 0

for f in files:
    try:
        for line in io.open(f, encoding="utf-8", errors="replace"):
            if '"tool_use"' not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get("message") or {}
            for c in (msg.get("content") or []):
                if not isinstance(c, dict) or c.get("type") != "tool_use":
                    continue
                n_calls += 1
                name = c.get("name") or ""
                if name.startswith("mcp__"):
                    mcp[name] += 1
                    continue
                if name != "Bash":
                    continue
                cmd = ((c.get("input") or {}).get("command") or "").strip()
                # 先頭のコマンドを取る（環境変数の前置き・cd・パイプ・&& を剥がす）
                for part in re.split(r"\||&&|;", cmd):
                    part = part.strip()
                    part = re.sub(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)+", "", part)
                    m = re.match(r"([\w./-]+)(?:\s+([\w.:@/-]+))?", part)
                    if not m:
                        continue
                    head = os.path.basename(m.group(1))
                    if head in ("cd", "timeout", "sudo"):
                        continue
                    sub = m.group(2) or ""
                    key = head if head in ("ls", "cat") else ("%s %s" % (head, sub)).strip()
                    bash[key] += 1
                    break
    except Exception:
        pass

buf = ["セッション記録 %d本 / ツール呼び出し %d回" % (len(files), n_calls), ""]
buf.append("=== Bash（先頭コマンド別・上位40） ===")
for k, v in bash.most_common(40):
    head = k.split()[0]
    if head in NEVER:
        mark = "⛔任意コード実行"
    elif head in AUTO_OK:
        mark = "－最初から許可済み"
    else:
        mark = "✅候補"
    buf.append("  %-6d %-34s %s" % (v, k[:34], mark))

buf.append("")
buf.append("=== MCPツール（上位30） ===")
for k, v in mcp.most_common(30):
    ro = any(w in k for w in ("read", "get", "list", "search", "view", "context", "screenshot", "find", "status"))
    buf.append("  %-6d %-52s %s" % (v, k, "✅読み取り系" if ro else "－書き込み/操作系"))

io.open("tmp/perm_scan_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("BASH_KINDS=%d MCP_KINDS=%d CALLS=%d" % (len(bash), len(mcp), n_calls))
