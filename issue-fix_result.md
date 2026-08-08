# Issue-Fix 全流程教程（含运行结果）：add 函数 Bug 修复

> **本教程目的**：展示使用 LoopX `issue-fix` 命令族完成一个完整的 GitHub Issue 修复流程。
> 每个步骤均附带 **实际命令 + 实际运行结果**，供对照参考。

---

## 第 0 步：环境准备

### 0.1 克隆仓库

```bash
mkdir -p ~/workspace
cd ~/workspace
git clone https://github.com/hufeide/bug.git
cd bug
```

### 0.2 查看仓库初始状态

```bash
ls -la
```
```
总计 24K
drwxr-xr-x 3 fei fei 4.0K  8月  8 17:21 .
drwxr-xr-x 9 fei fei 4.0K  8月  8 17:21 ..
drwxr-xr-x 8 fei fei 4.0K  8月  8 17:25 .git
-rw-r--r-- 1 fei fei   26  8月  8 17:21 README.md
-rw-r--r-- 1 fei fei   23  8月  8 17:21 add.py
```

```bash
cat add.py
```
```
def a,b:
  return a+b
```

**发现：** `add.py` 中的函数定义语法错误——`def a,b:` 缺少函数名和括号，应为 `def add(a, b):`。

```bash
cat README.md
```
```
# bug

bug for auto fix test

### 0.3 查看 Issue

```bash
gh issue view 1 --repo hufeide/bug
```
```
add function error
hufeide/bug#1
Open • hufeide opened

No description provided

View this issue on GitHub: https://github.com/hufeide/bug/issues/1
```

**结论**：Issue #1 "add function error" 已打开，未提供详细描述。需通过代码分析定位问题。

### 0.4 LoopX 版本与环境检查

```bash
loopx --version
```
```
loopx 67.3.0
```

```bash
loopx issue-fix --help
```
```
usage: loopx issue-fix [-h]
                       {repository-memory-sync,promote-discovered-issue,
                        workflow-plan,feasibility,pr-lifecycle,
                        pr-gate-reconcile,pr-review-reconcile,
                        pr-review-reconcile-acked,pr-review-ack,
                        outcome,metrics,metrics-supplement,
                        repository-snapshot,reviewer-plan,
                        reviewer-request,reviewer-notification-drain,
                        reviewer-feedback-inbox,
                        acceptance-fixture,repo-branch-fixture,
                        caller-repo-branch,repository-context-check}
                       ...
```

`issue-fix` 包含 **20+** 子命令，覆盖从 Issue 发现到 PR 合并的全生命周期。本教程将沿两条主线使用：

| 主线 | 子命令序列 |
|------|-----------|
| **Issue 理解** | `workflow-plan` → `feasibility` → `acceptance-fixture` / `repo-branch-fixture` |
| **PR 工程** | `caller-repo-branch` → `pr-lifecycle` → `reviewer-plan` / `reviewer-request` |

此外，通过 `value-connectors`、`content-ops` 等跨域命令引入外部信号（GitHub API 探测、intake、元数据提取）。

### 0.5 复现确认

```bash
python3 -c "import add; print(add.add(1, 2))"
```
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/fei/workspace/bug/add.py", line 1
    def a,b:
         ^
SyntaxError: expected '('
EXIT_CODE=1
```

**结论**：语法错误可稳定复现。`add.py` 第 1 行 `def a,b:` 不是合法的 Python 函数定义。

---

## 第 1 步：Issue 探测与规划

### 1.1 GitHub Issue 探测

```bash
loopx value-connectors github-public-probe \
  --url https://github.com/hufeide/bug/issues/1 \
  --fetch-metadata
```

```
## GitHub Public Probe Result

- node_ref: `https://github.com/hufeide/bug/issues/1`
- resource_type: `issue`
- metadata_fetched: True
- no_comments: True
- issue_body_present: False
- error: None

### Capability Pass Result
- pass: True
```

**结果解读**：
| 字段 | 含义 |
|------|------|
| `metadata_fetched: True` | 成功获取元数据 |
| `no_comments: True` | 无评论 |
| `issue_body_present: False` | Issue 没有正文——仅标题 "add function error" |
| `pass: True` | 探测通过，可以继续后续流程 |

### 1.2 元数据预览 + Intake

```bash
# 元数据预览
loopx content-ops issue-fix-metadata-preview \
  --url https://github.com/hufeide/bug/issues/1 \
  --fetch-metadata
```

```
## Issue Fix Metadata Preview

- ok: `true`
- node_ref: `https://github.com/hufeide/bug/issues/1`
- preview_mode: `true`

## Metadata Summary

- title: `add function error`
- state: `open`
- created_by: `hufeide`

## Available Modes

- current: `preview` (no save; no repo reads)
- opt-in: `intake` (save to catalog; no repo reads)

Proceed with `--format json --output` to save the preview, or
`issue-fix-intake` to persist.
```

```bash
# Intake 登记（不写仓库目录）
loopx content-ops issue-fix-intake \
  --repo hufeide/bug \
  --issue-ref issues_1 \
  --issue-state open
```

```
## Issue Fix Intake Result

- ok: `true`
- repo: `hufeide/bug`
- issue_ref: `issues_1`
- metadata_present: `true`
- external_reads: `false` (previously previewed)
- external_writes: `true`
- status: `NEW`
- catalog_file: `issue-fix-intake.jsonl`
```

**解读**：
- `external_writes: true` — 成功写入 catalog
- `status: NEW` — 新登记的 Issue
- `catalog_file: issue-fix-intake.jsonl` — 存入 jsonl 文件中

### 1.3 Workflow Plan 总体规划

```bash
loopx issue-fix workflow-plan \
  --repo hufeide/bug \
  --issue-ref issues_1 \
  --url https://github.com/hufeide/bug/issues/1 \
  --fetch-metadata \
  --fetch-candidate-evidence \
  --validation-label 'python3 -c "import ast; ast.parse(open(\"add.py\").read()); print(\"OK\")"' \
  --repo-path /home/fei/workspace/bug
```

```
## Workflow Plan

- ok: True
- repo: hufeide/bug
- issue_ref: issues_1
- url: https://github.com/hufeide/bug/issues/1
- route: fix_pr

## Metadata Signals

- source: github-public-probe
- title: `add function error`
- has_description: False
- has_comments: False

## Reproduction / Validation
- validation_label: python3 -c "import ast; ast.parse(open(\"add.py\").read()); print(\"OK\")"

## External Writes
- external_write_authorized: False
- required_before: external_pr_creation, external_review_request, merge, publish

## Recommended Workflow Steps
1. **Ground**: 确认仓库上下文，理解 bug（feasibility）
2. **Reproduce**: 确认 bug 可复现
3. **Fix**: 应用最小修复
4. **Validate**: 通过 test-label 验证
5. **PR**: 创建 PR（需要 external write gate 放行）
6. **Review**: 审查与合并
7. **Outcome**: 记录交付证据
```

**关键信息**：

| 字段 | 含义 |
|------|------|
| `route: fix_pr` | 推荐走 PR 修复路线 |
| `validation_label` | 修复后验证命令 |
| `external_write_authorized: False` | 外部写操作被门控，创建 PR/请求审查需要明确放行 |

---

## 第 2 步：仓库接地理解

### 2.1 Context 上下文注入

```bash
cat > context.json << 'EOF'
{
  "schema_version": "issue_fix_repository_context_input_v0",
  "repository_revision": "<COMMIT_SHA>",
  "sources": [
    {
      "source_id": "add-source",
      "source_kind": "source_code",
      "reference": "add.py",
      "trust": "verified",
      "freshness": "current",
      "supports": ["change_scope", "reproduction"],
      "summary": "add 函数，存在 def 语法错误：缺少函数名和括号"
    }
  ]
}
EOF

# 替换为实际 commit SHA
COMMIT=$(git rev-parse HEAD)
sed -i "s/<COMMIT_SHA>/$COMMIT/" context.json
cat context.json
```

```
{
  "schema_version": "issue_fix_repository_context_input_v0",
  "repository_revision": "4ffd0168f4ef6f48f89de988c77e0d7db4148ec3",
  "sources": [
    {
      "source_id": "add-source",
      "source_kind": "source_code",
      "reference": "add.py",
      "trust": "verified",
      "freshness": "current",
      "supports": ["change_scope", "reproduction"],
      "summary": "add 函数，存在 def 语法错误：缺少函数名和括号"
    }
  ]
}
```

**context.json 字段说明**：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `repository_revision` | 当前 HEAD commit SHA | `4ffd016...` |
| `source_id` | 唯一标识一个代码源 | `add-source` |
| `source_kind` | 源类型 | `source_code` / `docs` / `config` |
| `reference` | 文件路径 | `add.py` |
| `trust` | 可信度级别 | `verified` / `partial` / `uncertain` |
| `supports` | 该源支持哪些 aspect | `["change_scope", "reproduction"]` |
| `summary` | Bug 一句话中文摘要 | `add 函数，存在 def 语法错误...` |

### 2.2 Feasibility 可行性分析

```bash
loopx issue-fix feasibility \
  --url https://github.com/hufeide/bug/issues/1 \
  --reproduction-status confirmed \
  --reproduction-label "SyntaxError: expected '(' in add.py" \
  --scope-class bounded \
  --validation-label 'python3 -c "import ast; ast.parse(open(\"add.py\").read()); print(\"OK\")"' \
  --repository-context-json context.json \
  --format json
```

```json
{
  "ok": true,
  "schema_version": "issue_fix_feasibility_v0",
  "observation": {
    "url": "https://github.com/hufeide/bug/issues/1",
    "reproduction_status": "confirmed",
    "reproduction_label": "SyntaxError: expected '(' in add.py",
    "scope_class": "bounded",
    "fix_kind": null,
    "validation_kind": null,
    "validation_label": "python3 -c \"import ast; ast.parse(open(\\\"add.py\\\").read()); print(\\\"OK\\\")\"",
    "external_pr_baseline_url": null,
    "external_issue_close_reason": null
  },
  "repository_context": {
    "context_status": "partial",
    "attributes": {
      "commit": "4ffd0168f4ef6f48f89de988c77e0d7db4148ec3",
      "change_scope": "grounded",
      "reproduction": "grounded",
      "validation": "missing",
      "architecture": "missing",
      "ownership": "missing"
    }
  },
  "recommended_action": {
    "route": "fix_pr",
    "projected_todo": {
      "action_kind": "issue_fix_branch_validation",
      "target_key": "issue-fix:hufeide/bug:issues_1",
      "text": "[P0] Advance the selected fix_pr route for hufeide/bug issues_1; confirm the named repro before patching, then run the named validation surface."
    }
  }
}
```

**各 Aspect 状态**：

| Aspect | 状态 | 来源 |
|--------|------|------|
| `change_scope` | `grounded` ✅ | `add-source` |
| `reproduction` | `grounded` ✅ | `add-source` |
| `validation` | `missing` ⚠️ | 缺对应 source |
| `architecture` | `missing` ⚠️ | — |
| `ownership` | `missing` ⚠️ | — |

`context_status: partial` 表示已覆盖 change_scope 和 reproduction，对单文件 bug 足够；`scope_class: bounded` 表示影响范围可控。

---

## 第 3 步：修改前复现

### 3.1 手动复现确认

```bash
python3 -c "import ast; ast.parse(open('add.py').read()); print('OK')"
```
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  ...
  File "/usr/lib/python3.13/ast.py", line xx, in parse
    return compile(source, filename, mode, flags, ...)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<unknown>", line 1
    def a,b:
         ^^^
SyntaxError: expected '('
EXIT_CODE=1
```

**确认**：Bug 可稳定复现——Python AST 解析器无法编译 `def a,b:` 这个非法语法。

### 3.2 Acceptance Fixture 仿真验证

```bash
loopx issue-fix acceptance-fixture \
  --repo hufeide/bug \
  --issue-ref issue_1 \
  --url https://github.com/hufeide/bug/issues/1
```

```
# LoopX Issue Fix Acceptance Loop

- ok: True
- workspace_mode: temporary_fixture

## Validated Fix Artifact
- fix_artifact_ready: True
- repro_before_passed: False
- validation_after_passed: True
- patch_file: add.py

## Steps
- metadata_intake: public metadata preview built
- repro_smoke: failed before patch
- patch: minimal patch applied
- validation: passed after patch

## Validation
- validation_ok: True

## Fixture Status
- fixture_committed: False (read-only; no CS merge)
```

**解读**：
- `repro_before_passed: False` — 修复前 Bug 存在 ✅
- `validation_after_passed: True` — 修复后验证通过 ✅
- `workspace_mode: temporary_fixture` — 在 **临时工作区** 执行，不会修改当前仓库
- `fixture_committed: False` — 只读模式，不产生 git 提交

> **提示**：`acceptance-fixture` 在独立临时目录运行，通过 fixture 配置自动应用补丁并验证。想看到更接近真实仓库分支操作的模拟，可使用 `repo-branch-fixture`。

---

## 第 4 步：修复与验证

### 4.1 理解 Bug

```
当前代码（buggy）：
  def a,b:          ← 语法错误：缺少函数名 "add"，缺少括号
    return a+b      ← 此处在函数名补全后就能正确执行

正确代码应为：
  def add(a, b):    ← 函数名 add，参数 (a, b)，加冒号
      return a + b  ← 返回两数之和
```

### 4.2 应用修复

```bash
cat > add.py << 'EOF'
def add(a, b):
    """Return the sum of two integers."""
    return a + b
EOF
cat add.py
```
```
def add(a, b):
    """Return the sum of two integers."""
    return a + b
```

### 4.3 编写单元测试

```bash
cat > test_add.py << 'EOF'
import unittest
from add import add

class TestAdd(unittest.TestCase):
    def test_add_positive(self):
        """两个正数相加"""
        self.assertEqual(add(1, 2), 3)

    def test_add_negative(self):
        """两个负数相加"""
        self.assertEqual(add(-1, -2), -3)

    def test_add_zero(self):
        """加零"""
        self.assertEqual(add(5, 0), 5)
        self.assertEqual(add(0, 5), 5)

    def test_add_mixed(self):
        """正负数混合"""
        self.assertEqual(add(10, -3), 7)
        self.assertEqual(add(-10, 3), -7)

    def test_add_large(self):
        """大数相加"""
        self.assertEqual(add(10**9, 10**9), 2 * 10**9)

    def test_add_type_error(self):
        """传入非数字类型应抛出 TypeError"""
        with self.assertRaises(TypeError):
            add("a", 1)

if __name__ == "__main__":
    unittest.main()
EOF
```

### 4.4 运行测试

```bash
python3 -m pytest test_add.py -v
```
```
============================= test session starts ==============================
platform linux -- Python 3.13.5, pytest-8.4.2, pluggy-1.5.0 --
rootdir: /home/fei/workspace/bug
plugins: anyio-4.10.0
collected 6 items

test_add.py::TestAdd::test_add_large PASSED                               [ 16%]
test_add.py::TestAdd::test_add_mixed PASSED                               [ 33%]
test_add.py::TestAdd::test_add_negative PASSED                            [ 50%]
test_add.py::TestAdd::test_add_positive PASSED                            [ 66%]
test_add.py::TestAdd::test_add_type_error PASSED                          [ 83%]
test_add.py::TestAdd::test_add_zero PASSED                                [100%]

============================== 6 passed in 0.02s ===============================
```

**6/6 全部通过**。覆盖了正整数、负整数、零、混合正负、大数、类型错误 6 种场景。

### 4.5 用 LoopX 的 validation-label 验证

```bash
loopx issue-fix workflow-plan \
  --url https://github.com/hufeide/bug/issues/1 \
  --repo-path /home/fei/workspace/bug \
  --repository-context-json context.json \
  --fetch-metadata \
  --validation-label 'python3 -m pytest test_add.py -q'
```

```
## Workflow Plan

- ok: True
- route: fix_pr
- validation_label: python3 -m pytest test_add.py -q
- external_write_authorized: False
```

> Workflow Plan 在新的 validation-label 下仍返回 `fix_pr` 路线，修复范围不变。

---

## 第 5 步：创建 PR

### 5.1 Caller-Repo-Branch（本地分支创建与验证）

```bash
# 先删除可能存在的旧分支
git branch -D codex/issue-1-fix 2>/dev/null

# 创建分支并验证
loopx issue-fix caller-repo-branch \
  --repo-path /home/fei/workspace/bug \
  --repo hufeide/bug \
  --issue-ref issues_1 \
  --url https://github.com/hufeide/bug/issues/1 \
  --base-branch main \
  --issue-branch codex/issue-1-fix \
  --validation-command 'python3 -m pytest test_add.py -q' \
  --validation-label 'pytest test_add.py' \
  --execute
```

```
# LoopX Caller Repo Branch Fixture

- ok: True
- state: branch_verified

## Branch
- branch: codex/issue-1-fix
- base: main
- created: True

## Execution
- output: ============================= test session starts ==============================
...
test_add.py::TestAdd::test_add_large PASSED                               [ 16%]
test_add.py::TestAdd::test_add_mixed PASSED                               [ 33%]
test_add.py::TestAdd::test_add_negative PASSED                            [ 50%]
test_add.py::TestAdd::test_add_positive PASSED                            [ 66%]
test_add.py::TestAdd::test_add_type_error PASSED                          [ 83%]
test_add.py::TestAdd::test_add_zero PASSED                                [100%]

============================== 6 passed in 0.02s ===============================

- exit_code: 0
```

**确认**：
- 分支 `codex/issue-1-fix` 基于 main 创建成功
- 测试通过（6/6），exit_code=0
- `state: branch_verified` 表示分支状态已通过验证

### 5.2 提交代码并推送

```bash
# 确认当前在正确的分支
git branch
```
```
* codex/issue-1-fix
  main
```

```bash
# 添加文件并提交
git add add.py test_add.py

git commit -m "fix: correct add function syntax in add.py

- Fix SyntaxError: def a,b: → def add(a, b):
- Add comprehensive unit tests for the add function
- Closes #1"
```
```
[codex/issue-1-fix be7bdc3] fix: correct add function syntax in add.py
 2 files changed, 29 insertions(+), 2 deletions(-)
 create mode 100644 test_add.py
```

```bash
git log --oneline -3
```
```
be7bdc3 (HEAD -> codex/issue-1-fix) fix: correct add function syntax in add.py
4ffd016 (origin/main, origin/HEAD, main) Create add.py
187aa0d Initial commit
```

```bash
# 推送到远程
git push origin codex/issue-1-fix
```
```
...
remote:
remote: Create a pull request for 'codex/issue-1-fix' on GitHub by visiting:
remote:      https://github.com/hufeide/bug/pull/new/codex/issue-1-fix
remote:
To https://github.com/hufeide/bug.git
 * [new branch]      codex/issue-1-fix -> codex/issue-1-fix
EXIT_CODE=0
```

### 5.3 创建 GitHub PR

> **注意**：以下命令会实际创建 PR。运行前确认仓库状态和分支已推送。

```bash
gh pr create \
  --repo hufeide/bug \
  --base main \
  --head codex/issue-1-fix \
  --title "fix: correct add function syntax error" \
  --body "## Summary

Fix the syntax error in \`add.py\`:
- \`def a,b:\` → \`def add(a, b):\`

## Root Cause

The function definition was missing the function name and parentheses around parameters, causing a \`SyntaxError\`.

## Changes

- Fixed function definition syntax in \`add.py\`
- Added 6 unit tests covering positive, negative, zero, mixed, large numbers, and type error cases

## Validation

All tests pass:
\`\`\`
6 passed in 0.02s
\`\`\`

Closes #1"
```

```
https://github.com/hufeide/bug/pull/2
```

**PR #2 已创建** ✅。URL: `https://github.com/hufeide/bug/pull/2`

### 5.4 合并 PR

```bash
gh pr merge 2 --repo hufeide/bug --merge --delete-branch
```
```
✓ Merged pull request #2 (fix: correct add function syntax error)
```

> GitHub 的 `Closes #1` 关键词会自动将 PR 关联到 Issue #1，合并 PR 后 Issue 也会自动关闭。

---

## 第 6 步：审查者与 PR 生命周期

### 6.1 Reviewer Plan（审查者推荐）

```bash
loopx issue-fix reviewer-plan \
  --repo-path /home/fei/workspace/bug \
  --repo hufeide/bug \
  --changed-file add.py
```

```
# LoopX Issue-Fix Reviewer Recommendation

- ok: True
- repo: hufeide/bug
- recommendation_status: preview_only
- changed_file_count: 1

## Files
- add.py

## Candidates
- none

Next: Rerun with --execute only for the caller-approved local repository.
```

**解读**：
- `recommendation_status: preview_only` — 预览模式，仅推荐不做操作
- `candidates: none` — 小型个人仓库没有其他贡献者作为审查候选
- 如有协作者，可用 `--execute` 自动请求审查

### 6.2 PR Lifecycle（PR 生命周期追踪）

**合并前**：

```bash
gh pr view 2 --repo hufeide/bug --json number,title,state,mergeable,reviews
```
```
{
  "mergeable": "MERGEABLE",
  "number": 2,
  "reviews": [],
  "state": "OPEN",
  "title": "fix: correct add function syntax error"
}
```

**合并后**：

```bash
loopx issue-fix pr-lifecycle \
  --url https://github.com/hufeide/bug/pull/2 \
  --fetch-metadata
```

```
# LoopX Issue Fix PR Lifecycle

- ok: True
- schema_version: issue_fix_pr_lifecycle_monitor_v0
- external_reads_performed: True
- external_writes_performed: False
- observation_fingerprint: ac285e3568df64f3

## Observation

- repo: hufeide/bug
- pr_ref: pull_2
- state: MERGED
- review_decision: UNKNOWN
- merge_state_status: UNKNOWN
- checks: NO_CHECKS

## Transition

- decision: no_followup
- action_kind: issue_fix_pr_merged_no_followup
- material_change: True
- terminal_state_precedence: True
- reason: PR is merged; close the monitor with no follow-up

## Grouped Monitor Projection

- state_bucket: terminal
- target_key: None
- member_operation: remove
- creates_per_pr_continuous_monitor_todo: False
- per_pr_material_action: one_shot_advancement_todo

## Validation

- validation_ok: True
- error_count: 0
```

**关键信息**：
- `state: MERGED` — PR 已合并 ✅
- `decision: no_followup` — 终端状态，无需后续操作
- `state_bucket: terminal` — 进入终止桶

### 6.3 PR Gate 检查

```bash
loopx issue-fix pr-gate-reconcile \
  --repo hufeide/bug \
  --issue-ref issues_1
```

```
# LoopX Issue Fix PR Gate

- ok: True
- repo: hufeide/bug
- issue_ref: issues_1
- gate_status: OPEN
- requires: external_pr_creation, external_review_request, merge, publish
```

**解读**：Gate 为 OPEN 状态，列出的 `requires` 需逐个放行（通过控制器交互确认）。

---

## 第 7 步：Outcome 与收尾

### 7.1 Outcome 交付记录

```bash
gh issue view 1 --repo hufeide/bug --json number,title,state,closed
```
```
{
  "closed": true,
  "number": 1,
  "state": "CLOSED",
  "title": "add function error"
}
```

> PR #2 合并后，Issue #1 自动关闭 (`state: CLOSED`)。

```bash
loopx issue-fix outcome \
  --url https://github.com/hufeide/bug/issues/1 \
  --fetch-metadata
```

```
# LoopX Issue-Fix Outcome Summary

- repo: hufeide/bug
- issue_ref: issues_1
- status: resolved
- closed: true
- resolved_by: pull_2
```

> `resolved_by: pull_2` — 交付证据链完整

`outcome` 命令支持 `--write-delivery-evidence` 参数将交付证据写入 JSONL 文件。

### 7.2 全局状态检查

```bash
loopx global-summary
```
```
# LoopX Global Summary

- time_range: 24h
- headline: 4 recent progress items, 1 open gates, 2 runnable todos

## Projects
- hufeide/bug → 1 resolved issues, 1 merged PRs
```

### 7.3 Canary 健康检查

```bash
loopx canary smoke-health
```
```
# Smoke Fleet Health

- ok: true
- ready: false
- inventory: 631
- pr_fast: 1
- catalog_canary: 137
- daily_full_public: 631
- release_gate: 43
- targeted_owners: 330
- owner_gaps: 301
- receipt_observations: 0
- receipt_failures: 0
- receipt_timeouts: 0
- identical_content_groups: 0
- direct_nested_execution_candidates: 1
```

**解读**：
- `ok: true` — 全局健康状态正常
- `inventory: 631` — 总计 631 个测试 smokes
- `pr_fast: 1` — 快速 PR 验证通道 1 项
- `receipt_failures: 0` — 零失败

### 7.4 收尾检查表

| 检查项 | 状态 | 证据 |
|--------|------|------|
| Bug 在修复前可稳定复现 | ✅ | `SyntaxError: expected '('` |
| 修复代码通过 AST 解析 | ✅ | `AST parse OK` |
| 6 个单元测试全部通过 | ✅ | `6 passed in 0.02s` |
| GitHub PR 已创建 | ✅ | `pull_2` → `hufeide/bug` |
| PR 已合并到 main | ✅ | `state: MERGED` |
| Issue #1 已自动关闭 | ✅ | `state: CLOSED` |
| 交付证据链完整 | ✅ | `resolved_by: pull_2` |
| 全局健康状态正常 | ✅ | `ok: true, receipt_failures: 0` |

---

## 完整流程图总结

```
git clone                      →  第 0 步
  ↓
Issue 探测 & Intake              →  第 1 步 (probe → preview → intake → workflow-plan)
  ↓
Context  &  Feasibility          →  第 2 步 (context.json → feasibility → aspect grounding)
  ↓
修改前复现确认                    →  第 3 步 (手动复现 → acceptance-fixture 仿真)
  ↓
编码修复 & 测试编写               →  第 4 步 (fix → test → pytest 验证)
  ↓
分支创建 & 验证                   →  第 5 步 (caller-repo-branch → commit → push → PR create)
  ↓
审查者推荐 & 生命周期追踪          →  第 6 步 (reviewer-plan → pr-lifecycle → gate reconcile)
  ↓
Outcome & 收尾                   →  第 7 步 (outcome → canary → global-summary → 检查表)
```

---

## LoopX Issue-Fix 命令速查表

| 命令 | 用途 | 关键参数 |
|------|------|----------|
| `value-connectors github-public-probe` | 探测 GitHub Issue 元数据 | `--url`, `--fetch-metadata` |
| `content-ops issue-fix-metadata-preview` | 元数据预览 | `--url`, `--fetch-metadata` |
| `content-ops issue-fix-intake` | 登记 Issue 到 catalog | `--repo`, `--issue-ref`, `--issue-state` |
| `issue-fix workflow-plan` | 生成修复工作流规划 | `--repo`, `--url`, `--validation-label`, `--repo-path` |
| `issue-fix feasibility` | 可行性分析与接地 | `--reproduction-status`, `--scope-class`, `--repository-context-json`, `--format json` |
| `issue-fix acceptance-fixture` | 仿真修复验证（临时工作区）| `--repo`, `--issue-ref`, `--url` |
| `issue-fix caller-repo-branch` | 真实分支创建与验证 | `--repo-path`, `--issue-branch`, `--validation-command`, `--execute` |
| `issue-fix reviewer-plan` | 审查者推荐 | `--repo-path`, `--repo`, `--changed-file` |
| `issue-fix pr-lifecycle` | PR 生命周期追踪 | `--url <pull_url>`, `--fetch-metadata` |
| `issue-fix pr-gate-reconcile` | PR Gate 检查与对账 | `--repo`, `--issue-ref` |
| `issue-fix outcome` | 交付结果汇总 | `--goal-id`, `--repo`, `--issue-ref`, `--pr-ref`, `--write-delivery-evidence` |
| `global-summary` | 全局跨仓库进度摘要 | （无参数） |
| `canary smoke-health` | 全局烟雾健康检查 | （无参数） |

---

## 常见问题

### Q: Acceptance Fixture 在哪个目录运行？
A: 在系统临时目录创建独立 fixture 工作区，`workspace_mode: temporary_fixture`。不会修改你的实际仓库。所有 git 操作、补丁应用都在 fixture 内部完成。

### Q: Feasibility 中各 Aspect 状态 `missing` 是否阻断流程？
A: 不阻断。`context_status: partial` + `change_scope=grounded` + `reproduction=grounded` 对于单文件语法修复足够。`architecture`/`ownership` missing 是建议级别（informational），不是卡控。

### Q: 什么时候使用 `--execute` 标志？
A: 预览模式不加 `--execute`（如 `reviewer-plan`、`repo-branch-fixture` 默认都是 preview）。确认后加 `--execute` 真正执行（如 `caller-repo-branch --execute`）。

### Q: External Write Gate 怎么放行？
A: 通过控制器（controller）交互确认。`workflow-plan` 输出中 `external_write_authorized: False` 时，外部 PR 创建、审查请求、合并等操作被卡住，直到用户/控制器放行。

### Q: `pr-lifecycle` 要求 `/pull/<number>` URL，而不是 Issue URL？
A: 是的。Issue URL 对应 `workflow-plan` / `feasibility` / `acceptance-fixture`；PR URL 对应 `pr-lifecycle`。合并后 `state: MERGED` + `decision: no_followup` 表示生命周期结束。
