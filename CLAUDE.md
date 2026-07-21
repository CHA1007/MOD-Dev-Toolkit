# CLAUDE.md

## Agent skills

### Issue tracker

Issues are tracked as local markdown files under `.scratch/<feature>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Five canonical labels, used as-is (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## 代码规范

### 注释规则

- 注释一律使用中文；英文名词（API、Gradle、WPF-UI、JSON 等）可保留原文
- 只在关键代码处注释：非显而易见的逻辑、重要决策、坑点；显而易见的代码不加注释
- 注释一行说明「作用」或「实现」即可，禁止冗长解释
- 运行 `python scripts/clean_comments.py` 审计注释违规，`--fix` 应用清理
