---
title: ECC 深度了解
date: 2026-05-04
tags:
  - ecc
  - claude-code
  - tool
  - tech
  - learning
aliases:
  - Everything Claude Code
---

# Everything Claude Code (ECC) 深度了解

> 日期：2026-05-04
> 来源：与 Claude Code 的实际对话探索

---

## 1. ECC 的安装机制

ECC **不是**把 skill 文件放到 `.claude/skills/` 目录，而是作为 **Claude Code 插件 (Plugin)** 安装。

### 安装位置
```
~/.claude/plugins/cache/everything-claude-code/everything-claude-code/2.0.0-rc.1/
├── skills/      ← 182 个 skills（插件内部）
├── commands/    ← 68  个命令
├── agents/      ← 48  个 agents
├── hooks/       ← 钩子脚本 + hooks.json
├── rules/       ← 规则文件（按语言分类）
└── .claude-plugin/plugin.json
```

### 配置入口
`~/.claude/settings.json` 中：
```json
"extraKnownMarketplaces": {
  "everything-claude-code": {
    "source": { "source": "github", "repo": "affaan-m/everything-claude-code" }
  }
},
"enabledPlugins": {
  "everything-claude-code@everything-claude-code": true
}
```

### 对比：插件系统 vs Skills 目录

| 机制 | `.claude/skills/` | 插件系统 |
|------|-------------------|----------|
| 安装方式 | 手动放入 skill 文件 | Claude Code 从 GitHub 拉取 |
| 能装什么 | 单个 skill | skills + commands + agents + hooks + rules + MCP |
| ECC 在哪 | ❌ 不在 | ✅ 在 plugins/cache/ |

---

## 2. ECC 的钩子系统

ECC 有 26 个钩子，分 7 种类型，全部自动运行。

### 核心钩子

| 钩子 | 时机 | 作用 |
|------|------|------|
| GateGuard | PreToolUse (Bash/Edit/Write) | 首次操作前要求陈述事实 |
| Config Protection | PreToolUse (Write/Edit) | 阻止修改 linter/formatter 配置 |
| Quality Gate | PostToolUse | 编辑后自动检查代码质量 |
| Suggest Compact | PreToolUse (Edit/Write) | 定期提醒手动压缩上下文 |
| Cost Tracker | Stop | 会话结束追踪成本 |

### GateGuard 具体行为
- **首次 Bash**：要求陈述「当前任务 + 该命令做什么」
- **首次 Edit/Write 某文件**：要求列出 importers、受影响 API、数据结构
- **危险命令** (rm -rf, git reset --hard)：要求列出影响范围 + 回滚方案

### 禁用方法
```bash
export ECC_GATEGUARD=off          # 本次会话
# 或在 settings.json: "env": { "ECC_GATEGUARD": "off" }
```

---

## 3. /plan 的区别

| | Claude Code 自带 | ECC 的 /plan |
|---|---|---|
| 机制 | `EnterPlanMode` 工具（独立模式） | 内联执行 |
| 流程 | 探索→设计→ExitPlanMode 提交 | 分析→出步骤→等确认 |
| 适合 | 复杂架构决策 | 快速规划 |

ECC 还有更重的 `/prp-plan`：生成 PRD + 架构设计 + 技术文档。

---

## 4. ECC 的记忆系统

ECC 内置 `memory` MCP 服务器（知识图谱），**不会自动记录**，需要手动写入。

### 记忆类型
| 类型 | 内容 | 示例 |
|------|------|------|
| user | 用户角色、偏好、知识背景 | 你是后端工程师，熟悉 Go |
| feedback | 用户给出的行为指导 | 不要用 mock 数据库 |
| project | 项目背景、目标、约束 | 这个重构是合规要求 |
| reference | 外部系统链接 | Bug 在 Linear 项目 "INGEST" |

### 会话持久化
- `/save-session` — 手动保存会话摘要
- `/resume-session` — 恢复之前的会话
- 对话转录自动保存在 `~/.claude/projects/<project>/` 下（JSONL）

---

## 5. ECC 完整功能清单

### 会话管理
`/save-session` `/resume-session` `/sessions` `/checkpoint`

### 学习系统（从对话中提炼知识）
`/learn` — 从对话提取模式 → skill 文件
`/skill-create` — 从 Git 历史生成 skill
`/evolve` — 聚类 instinct → skill/agent

### 代码质量
`/code-review` `/security-review` `/build-fix` `/refactor-clean` `/quality-gate`

### 开发流程
`/plan` `/prp-plan` `/prp-implement` `/tdd-workflow` `/feature-dev`

### 自动化
`/hookify` — 从对话创建钩子规则
`/loop-start` — 定时重复执行任务

### 10 条自动加载的规则
`coding-style.md` `security.md` `testing.md` `code-review.md` `development-workflow.md` `agents.md` `performance.md` `git-workflow.md` `patterns.md` `hooks.md`

---

## 6. 关键心得

1. ECC 的价值不在界面，而在规则/钩子/agents 改变了助手的行为方式
2. 记忆需要主动建立，不会自动记录对话
3. GateGuard 可以关闭，不是必须忍受
4. `/learn` 适合无 git 项目，`/skill-create` 需要 git 仓库
5. 插件系统 ≠ skills 目录，插件可以包含 skills 但 skills 只是插件功能之一

## 相关笔记

- [[ClaudeCode与Obsidian日记工作流|Claude Code + Obsidian 日记工作流]] — 如何用 Claude Code 管理 Obsidian 知识库
- [[ClaudeCode任务完成提示音Hook|任务完成提示音 Hook]] — Stop hook 实战用例
- [[工具|工具与平台]] — 回到工具 MOC
