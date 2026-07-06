---
title: Reasonix AI编码助手
tags:
  - inbox
  - tool/ai
  - reasonix
created: 2026-06-07
---

# Reasonix：一个 DeepSeek 原生的终端编码助手

## 它是什么

Reasonix 是一个**开源的、配置驱动的 AI 编码助手**，跑在终端里，默认用 DeepSeek 的模型。

它不是 Claude Code 的替代品，而是走的另一条路——一条更便宜、更开放的路。它和 Claude Code 共享同一套 Agent Skills 标准，所以你在 Claude Code 里写的 playbook（/baoyan-daily-update 这类 skill），Reasonix 可以直接用。

> 项目地址：[github.com/esengine/DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)（MIT 协议）
> 安装：`npm i -g reasonix`

## 为什么会有 Reasonix

DeepSeek 的 API 有**缓存命中**和**未命中**两档价格。缓存命中的价格只有未命中的 **1/40**（以 v4-flash 为例：¥0.02 vs ¥1.0 per 1M tokens）。

Reasonix 的核心思路就是围绕这个定价模型设计的——**保持会话前缀稳定，最大化缓存命中率，让长时间对话的成本大幅降低**。每一次工具调用、每一条消息都追加在会话末尾，不修改前缀，这样 DeepSeek 的自动缓存可以反复命中。

相比之下，Claude Code 用的是 Anthropic 的模型，走订阅制，没有缓存差价可以利用。

## 核心设计理念

### 1. 配置驱动，一切皆配置

Reasonix 的核心代码几乎不知道任何具体模型或工具——所有 provider、tool、plugin 都是在 `reasonix.toml` 中声明，运行时通过注册表查找。

```
模型没有硬编码的 switch-case
工具没有写死的实现
新模型 = 一行配置，不需要改代码
```

### 2. 缓存优先（Cache-First）

这是 Reasonix 最独特的设计。常规的上下文压缩（compaction）会破坏缓存前缀，所以 Reasonix 尽量不压缩，只在接近上下文窗口上限时才压缩一次：

- `soft_compact_ratio = 0.5` — 达到 50% 时给提示
- `compact_ratio = 0.8` — 达到 80% 时压缩一次
- 压缩后自动归档旧历史到 `archive/`，但大部分时候缓存前缀是稳定的

### 3. 支持双模型协作

可以配一个"执行模型"和一个"规划模型"：

```toml
[agent]
planner_model = "deepseek-pro"
```

规划模型（低频）在一个独立 session 里运行，只读分析+出计划；然后执行模型在自己的 session 里落地。两个 session 互不干扰，各自保持缓存稳定。

### 4. 兼容 Claude Code 的生态

Reasonix 的 `ConventionDirs` 包含 `.reasonix`、`.agents`、`.agent`、`.claude` 四个目录。也就是说，它默认会扫描 `~/.claude/skills/`、`<project>/.claude/skills/` 等路径——你在 Claude Code 里装的 skill，Reasonix 直接拿来用，不需要迁移。

## 安装和配置

```bash
npm i -g reasonix          # 全局安装
reasonix setup              # 交互式配置向导 → 生成 reasonix.toml
export DEEPSEEK_API_KEY=sk-...
reasonix chat               # 启动交互式对话
```

配置优先级：**命令行 flag > `./reasonix.toml` > `~/.config/reasonix/config.toml` > 内置默认值**

## 数据存储

| 内容 | 位置 |
|------|------|
| 配置文件（用户） | `~/.config/reasonix/config.toml` |
| 配置文件（项目） | `./reasonix.toml` |
| 历史对话 | `~/.config/reasonix/sessions/`（`.jsonl` 格式，每行一条消息） |
| 压缩归档 | `~/.config/reasonix/archive/` |
| 凭据 | `~/.config/reasonix/credentials` |
| 自定义命令 | `~/.config/reasonix/commands/*.md` 或 `.reasonix/commands/*.md` |
| 自定义 skill | `~/.reasonix/skills/` / `<project>/.reasonix/skills/` |

## 架构分层

Reasonix 有三层扩展机制：

1. **编译期内置** — provider（`openai`）和 tool（`read_file`、`bash`、`grep` 等）通过 `init()` 自注册
2. **运行时 MCP 插件** — 通过 `[[plugins]]` 配置的 MCP 服务器（stdio 或 Streamable HTTP）
3. **Skills / Commands** — Markdown 格式的 playbook 和自定义斜杠命令

### MCP 支持

Reasonix 是一个 MCP 客户端，支持 stdio 和 Streamable HTTP 两种传输协议：

```toml
[[plugins]]
name    = "example"
command = "reasonix-plugin-example"

[[plugins]]
name    = "stripe"
type    = "http"
url     = "https://mcp.stripe.com"
headers = { Authorization = "Bearer ${STRIPE_KEY}" }
```

也兼容 `.mcp.json`（Claude Code 的 MCP 配置格式），直接放项目根目录就行。

## 内置工具

Reasonix 自带的工具和 Claude Code 基本对标：

- **文件操作**：`read_file`、`write_file`、`edit_file`、`multi_edit`、`delete_range`、`delete_symbol`
- **搜索**：`grep`、`glob`、`ls`
- **Shell**：`bash`
- **网络**：`web_fetch`
- **子任务**：`task`（生成 sub-agent）
- **Skill**：`run_skill`、`install_skill`
- **计划**：`todo_write`、`complete_step`
- **代码图**：`codegraph` 相关工具（可选内置 MCP 服务器）

## 内置 Skills

和 Claude Code 不同，Reasonix 有 6 个内置 skill，不需要额外安装：

| Skill | 模式 | 用途 |
|-------|------|------|
| `init` | inline | 初始化项目的 AGENTS.md（类似 CLAUDE.md） |
| `explore` | subagent | 只读探索代码库，返回浓缩报告 |
| `research` | subagent | 结合 web_fetch + 代码阅读做研究 |
| `review` | subagent | 审查当前分支的 diff |
| `security-review` | subagent | 安全专项审查 |
| `test` | inline | 运行测试并修复失败 |

subagent 模式的 skill 在隔离的子循环中运行，它的工具调用和推理过程不会进入主对话上下文，只有最终答案会返回。

## 权限和安全

Reasonix 有一套三层防护：

1. **权限策略**（Policy）— 每个工具调用进入 `deny > ask > allow > fallback` 规则判断
2. **沙箱**（Sandbox）— 文件写入被限制在项目目录内（macOS 上 Bash 也被 Seatbelt 限制）
3. **计划模式**（Plan Mode）— 拒绝所有写入操作，直到用户审批

```toml
[permissions]
mode  = "ask"
deny  = ["bash(rm -rf*)", "bash(git push*)"]
allow = ["bash(go test*)"]

[sandbox]
bash    = "enforce"   # macOS 上用 Seatbelt 限制 shell
network = true
```

## 自定义斜杠命令

在 `.reasonix/commands/` 或 `~/.config/reasonix/commands/` 下放 Markdown 文件，文件名决定命令名：

```markdown
---
description: Review the staged diff
argument-hint: [focus-area]
---
Review the staged diff. Focus on $ARGUMENTS, list bugs with file:line.
```

`review.md` → `/review`，`git/commit.md` → `/git:commit`。MCP 的 prompts 也注册为 `/mcp__<server>__<prompt>`。

## 与 Claude Code 的对比

| 维度 | Reasonix | Claude Code |
|------|----------|-------------|
| 后端模型 | DeepSeek 系列 | Claude 系列（Opus/Sonnet/Haiku） |
| 成本模型 | 按量付费，缓存价格极低 | 订阅制（Pro $20/月，Max $100-$200/月） |
| 长会话成本 | 低（缓存友好） | 高（长会话消耗大量 token） |
| 开源 | ✅ MIT | ❌ 闭源 |
| 安装方式 | `npm i -g reasonix` | 原生安装包 / Homebrew |
| Skill 格式 | 兼容 Agent Skills 标准，读 `.claude/skills/` | 原生支持 Agent Skills 标准 |
| 双模型协作 | ✅ 支持 | ❌ 只支持单一模型 |
| IDE 集成 | 仅终端 + Wails 桌面端 | VS Code / JetBrains / 桌面端 / 网页 / 终端 |
| MCP 支持 | ✅ stdio + Streamable HTTP | ✅ 更全面的 MCP 生态 |
| 沙箱 | macOS Seatbelt / 文件写入限制 | 内置沙箱 |
| 社区 | 较小，但活跃的 Discord 社区 | 非常庞大 |
| 代码审查 | 内置 `review` skill | 依赖自定义 skill 或工具 |

## 适用场景

Reasonix 特别适合的场景：

- **长时间编码会话** — 缓存命中率优势在高频提问中非常显著
- **预算敏感的项目** — 不想为每个对话付订阅费
- **DeepSeek 生态用户** — 本身就在用 DeepSeek API
- **需要两个模型协作** — 规划+执行分离的工作流
- **开源偏好** — 想要完全可控的编码助手

不太适合的场景：

- **需要顶级模型能力的复杂推演问题** — Claude Opus 在这类问题上仍然更强
- **多 IDE 深度集成** — Reasonix 目前以终端和桌面为主
- **需要闭源合规的场景** — 数据会经过 DeepSeek API

## 总结

Reasonix 是一个聪明的设计——它不是去和 Claude Code 正面竞争能力，而是选择了一个差异化的赛道：**利用 DeepSeek 的缓存定价模型，把长会话成本降到最低**。

对于一个每天和 AI 对话数小时的开发者来说，这个差异是实质性的：同样的一次编码会话，Reasonix 的成本可能是 Claude Code 的几分之一到十分之一。

同时它保持了生态兼容性——skills、MCP、`.mcp.json` 都和 Claude Code 共用，切换成本很低。

> 关键成本数据（DeepSeek v4-flash）：缓存命中 ¥0.02/1M tokens，未命中 ¥1.0/1M tokens。差值 50 倍。
