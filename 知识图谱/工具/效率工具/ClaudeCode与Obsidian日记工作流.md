---
title: Claude Code + Obsidian 日记工作流
date: 2026-05-04
tags:
  - claude-code
  - tech
  - obsidian
  - workflow
  - diary
  - tools
---

# Claude Code + Obsidian 日记工作流

> 用 Claude Code 辅助管理 Obsidian 知识库，把 AI 嵌入日常记录流程
> 相关：[[ECC深度了解|ECC 深度了解]] — 了解 Claude Code 插件系统的完整机制 | [[工具|工具与平台]]

## 为什么这样搭配

| 工具 | 角色 |
|------|------|
| Obsidian | 存储、浏览、可视化笔记 |
| Claude Code | 整理、归纳、生成、关联笔记 |

Claude Code 能直接读写文件，所以它就是你知识库的 AI 助手——你告诉它做什么，它直接操作 `.md` 文件。

## 日记流程

### 每日模板

在 Obsidian 中配置日记模板（`模板/日记模板.md`），每天自动生成：

```markdown
---
title: "{{date}}"
tags: [daily]
---

# {{date}}

## 今日重点

## 笔记

## 回顾
```

### 借助 Claude Code 整理

每天或每周结束时，在终端进入知识库目录，让 Claude Code 帮你：

```bash
cd /home/wjg/knowledge-base
claude
```

然后下指令，例如：

| 你想做什么 | 对 Claude 说的话 |
|-----------|-----------------|
| 整理收集箱 | "帮我把收集箱里的笔记归类到知识图谱对应分类" |
| 提取日记要点 | "阅读本周日记，提炼关键收获写到一篇周报" |
| 关联已有笔记 | "检查这篇新笔记，帮我加上到相关笔记的双向链接" |
| 生成 MOC | "帮我把关于 Docker 的所有笔记汇总成一个 MOC" |
| 补全模板属性 | "给这篇笔记加上 YAML frontmatter" |

### 实际工作流

1. **白天** → Obsidian 快速记录（`Ctrl+N` 进收集箱，或日记页随手记）
2. **晚上/weekend** → 打开终端，让 Claude Code 整理当天内容
3. **定期** → Claude Code 帮你建立索引 MOC、补全标签、去重

## 注意事项

- Claude Code 可以直接读写你的 vault 文件，所以保持同步（Sync 插件或 git）
- 重要内容建议先备份或 commit，再让 AI 批量操作
- AI 整理的笔记最好人工再过一眼，确认关联是否合理

## 相关

- [[ECC深度了解|ECC 深度了解]]
- [[ClaudeCode任务完成提示音Hook|任务完成提示音 Hook]]
