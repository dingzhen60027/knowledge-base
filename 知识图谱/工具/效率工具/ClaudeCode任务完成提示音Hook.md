---
title: Claude Code 任务完成提示音 Hook
date: 2026-05-05
tags:
  - claude-code
  - hook
  - workflow
---

# Claude Code 任务完成提示音 Hook

## 痛点

让 Claude Code 完成任务后**没有明显提醒**，如果切出去看手机或干别的事，经常任务跑完了还不知道。

## 解决方案：Stop Hook

新增了一个 Stop 类型的 hook：当任务完成时自动播放提示音。

```
Hook 类型: Stop
触发时机: 任务完成时
动作: 播放系统提示音
```

## 什么是 Hook

Hook 是 Claude Code 在特定时机自动执行的脚本。7 种类型：

| 类型 | 触发时机 |
|------|---------|
| PreToolUse | 工具调用**前** |
| PostToolUse | 工具调用**后** |
| Stop | 任务**结束**时 |
| Notification | 消息通知时 |
| PreCompact | 上下文压缩前 |
| SessionStart | 会话开始时 |
| Resume | 从暂停恢复时 |

> [!info] 更多细节
> 参考 [[ECC深度了解#2. ECC 的钩子系统|ECC 钩子系统]]

## 相关笔记

- [[ECC深度了解|ECC 深度了解]] — ECC 26 个钩子的完整说明
- [[ClaudeCode与Obsidian日记工作流|Claude Code + Obsidian 工作流]] — AI 辅助知识库管理
