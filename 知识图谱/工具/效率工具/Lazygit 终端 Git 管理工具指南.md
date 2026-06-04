---
title: Lazygit 终端 Git 管理工具指南
aliases:
  - lazygit
  - git tui
tags:
  - git
  - lazygit
  - tool
  - terminal
created: 2026-06-04
---

# Lazygit 终端 Git 管理工具指南

> 终端里的 Git 可视化面板 —— 不离开键盘，也能看清每次操作的结果。

---

## 一、背景：Git 命令行的痛点

Git 本身功能很强大。但日常开发中，那些最频繁的操作——暂存文件、写提交信息、切换分支、看历史、解决冲突——每次都要敲一长串命令，而且很多操作需要额外的命令来"确认结果"。

一个典型的例子。假设你改了三个文件，只想暂存其中两个：

```bash
git add file1.cpp file2.cpp
git status                  # 确认暂存状态
git commit -m "feat: ..."
git push                    # 推送到远程
```

这还不算复杂的情况。如果遇到冲突、需要交互式变基、或者只是忘了某条命令的精确参数，就要停下来查文档。更麻烦的是，`git log` 的输出虽然信息量大，但不够直观——谁改了什么、分支从哪里分出来的、commit 之间的关系，靠文字很难一眼看清。

问题是：**Git 的日常操作频率很高，但纯命令行的心智负担也不小。** 尤其在以下几种场景下特别明显：

- 开新分支之后频繁切换、合并
- 暂存时想看清楚改了哪些行再决定
- 交互式变基（squash / reword / drop）
- 解决冲突时比对两边的改动
- 刚学 Git 的人，对 `reset`、`revert`、`rebase` 的畏难情绪

这些问题会打断你的工作流——你正在写代码，然后停下来敲一串 git 命令，再切回编辑器。

有没有一种方式，既能保持命令行的效率（不离开终端），又能获得图形化的直观反馈？

---

## 二、Lazygit 是什么

Lazygit 是一个**终端用户界面（TUI）**，它架在 Git 之上，把 Git 的常用操作变成了可视化的面板和快捷键。你不需要切换到浏览器打开 GitHub Desktop，也不需要开 VS Code 的 Git 面板——直接在终端里按几个键就能完成所有操作。

它和 GUI 工具（如 GitKraken、Sourcetree）的区别：

| | GUI 工具 | Lazygit |
| --- | ------- | ------- |
| 运行位置 | 独立窗口 | 终端内 |
| 鼠标依赖 | 依赖 | 纯键盘 |
| 启动速度 | 秒级 | 毫秒级 |
| 学习成本 | 低（但切换窗口频繁） | 中（但融入终端工作流） |
| 远程仓库管理 | 强 | 够用 |

和原始 `git` 命令的区别：

| | git CLI | Lazygit |
| --- | ------- | ------- |
| 操作方式 | 手动输入命令+参数 | 快捷键选择 |
| 反馈速度 | 需输命令看结果 | 实时刷新面板 |
| 学习曲线 | 陡 | 平 |
| 复杂操作 | 需记参数 | 交互式选择 |
| 脚本化/自动化 | 强 | 弱 |

> [!tip] Lazygit 不是替代 `git` 命令，而是**降低日常操作的认知负担**。复杂脚本、CI/CD 配置、自动化操作仍然用命令行。

---

## 三、安装

### 3.1 通过包管理器（推荐）

**Ubuntu / Debian**（需要 sudo）：

```bash
sudo apt install lazygit
```

**macOS：**

```bash
brew install lazygit
```

**Arch Linux：**

```bash
sudo pacman -S lazygit
```

### 3.2 下载二进制文件

如果包管理器没有或版本过旧，直接从 GitHub release 下载：

```bash
LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/download/v${LAZYGIT_VERSION}/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
tar xf lazygit.tar.gz lazygit
sudo mv lazygit /usr/local/bin/
lazygit --version
```

> [!note] 如果下载慢，终端配置代理：`export https_proxy=http://127.0.0.1:7897`（替换为你的代理端口）。

### 3.3 验证安装

```bash
lazygit --version
```

进入已有 Git 仓库的目录，直接输入 `lazygit` 启动：

```bash
cd /path/to/your/repo
lazygit
```

---

## 四、界面布局：五个面板

启动 lazygit 后，你会看到一个分屏界面。按功能分成五个主要面板，通过数字键 `1`-`5` 或方向键切换：

```
┌─────────────┬──────────────────────────────┐
│   1: Status  │                              │
│   (状态)     │    右侧主面板                 │
│             │    (文件差异 / commit 详情)    │
│  2: Files    │                              │
│   (文件)     │                              │
│             │                              │
│  3: Commits  │                              │
│   (提交)     │                              │
│             │                              │
│  4: Branch   │                              │
│   (分支)     │                              │
│             │                              │
│  5: Stash    │                              │
│   (暂存)     │                              │
└─────────────┴──────────────────────────────┘
```

### 面板说明

| 面板 | 用途 | 对应 git 命令 |
| --- | ---- | ------------ |
| Status | 当前分支、仓库状态概览 | `git status` |
| Files | 列出修改的文件，可逐行暂存 | `git status` + `git diff` |
| Commits | 当前分支的提交历史 | `git log` |
| Branch | 本地和远程分支管理 | `git branch` + `git remote` |
| Stash | 暂存栈管理 | `git stash` |

每个面板选中条目后，右侧主区域会展示详细信息（文件 diff、commit 内容、分支拓扑等）。

---

## 五、核心操作

### 5.1 查看变更与暂存（Files 面板）

这是最常用的面板。你改了文件后按 `2` 进入 Files 面板：

1. 上下键选择文件
2. 按 `空格` 暂存/取消暂存整个文件
3. 按 `Enter` 查看文件 diff（右侧显示改动的行）
4. 在 diff 视图中，按 `空格` 可以**逐行暂存**——只暂存某几行修改
5. 文件颜色含义：

| 颜色 | 含义 |
| ---- | ---- |
| 红色 | 未暂存的修改 |
| 绿色 | 已暂存 |
| 黄色 | 部分暂存（部分行已暂存、部分未暂存） |

### 5.2 提交（Files 面板 → Commit）

暂存完文件后：

1. 按 `c` 弹出提交信息输入框
2. 输入提交信息，`Enter` 确认提交
3. 如果想修改上一次提交（amend），按 `a`

> [!tip] 提交信息的编辑支持多行，按 `Ctrl+O` 提交或使用默认编辑器。

### 5.3 分支操作（Branch 面板）

按 `4` 进入 Branch 面板：

| 操作 | 按键 | 说明 |
| ---- | ---- | ---- |
| 切换分支 | `Enter` | 选中分支后按回车 |
| 创建分支 | `n` | 基于当前分支创建新分支 |
| 删除分支 | `d` | 删除选中的本地分支 |
| 合并分支 | `M` | 将选中分支合并到当前分支 |
| 变基 | `r` | 将当前分支变基到选中分支 |
| 查看远程分支 | `R` | 显示/隐藏远程跟踪分支 |

### 5.4 提交历史管理（Commits 面板）

按 `3` 进入 Commits 面板：

| 操作 | 按键 | 说明 |
| ---- | ---- | ---- |
| 查看详情 | `Enter` | 查看该次提交的改动 |
| 复制哈希 | `y` | 复制 commit hash |
| 检出 | `S` | 检出到该 commit（detached HEAD） |
| 打标签 | `t` | 给该 commit 打标签 |
| Cherry-pick | `C` | 将该 commit 捡到当前分支 |
| 还原 | `g` | 创建一个 revert commit |

### 5.5 撤销与重置

| 操作 | 按键 | 说明 |
| ---- | ---- | ---- |
| 撤销暂存 | `<` | 取消上一次暂存 |
| 重置工作区 | `D` | 丢弃所有未暂存的修改（谨慎！） |
| 软重置 | `f` | git reset --soft 到该 commit |
| 混合重置 | `g` | git reset --mixed 到该 commit |
| 硬重置 | `!` | git reset --hard 到该 commit（不可恢复！） |

> [!warning] `!` 硬重置不可恢复，使用前确认没有未备份的改动。

---

## 六、进阶操作

### 6.1 交互式变基（Rebase）

这是 lazygit 最亮的功能之一。在 Commits 面板（`3`）：

1. 选中最旧的那个需要修改的 commit
2. 按 `e` 或 `r` 启动交互式变基
3. 进入 rebase 视图，对每个 commit 可以：

| 操作 | 按键 | 效果 |
| ---- | ---- | ---- |
| 保留 | `p` | 保留该 commit |
| 编辑 | `e` | 停下来修改该 commit 内容 |
| 合并到上一个 | `s` | squash——合并到上一个 commit |
| 修复到上一个 | `f` | fixup——合并但丢弃该 commit 信息 |
| 修改信息 | `r` | reword——修改提交信息 |
| 删除 | `d` | drop——丢弃该 commit |
| 调整顺序 | `Ctrl+↑/↓` | 拖动 commit 交换位置 |

对比命令行：

```bash
# 命令行做一次 squash 需要：
git rebase -i HEAD~3
# 进入 vim 编辑 pick/squash
# 保存退出
# 再编辑一次提交信息
# 保存退出
```

Lazygit 中：选中文件 → `s` → 确认 → 完成。

### 6.2 解决冲突

在合并或变基过程中遇到冲突时：

1. Lazygit 会自动显示有冲突的文件（Files 面板标记为黄色）
2. 选中冲突文件按 `Enter` 查看 diff
3. 按 `空格` 在 base / local / remote 版本之间切换
4. 手动编辑文件后保存
5. 按 `空格` 标记为已解决
6. 所有冲突解决后，按 `c` 继续提交

> [!tip] 按 `1` 可以快速查看当前合并/变基的状态，以及剩余冲突数。

### 6.3 暂存栈（Stash）

按 `5` 进入 Stash 面板：

| 操作 | 按键 | 说明 |
| ---- | ---- | ---- |
| 创建暂存 | `w` | 把当前未提交的改动存起来 |
| 应用暂存 | `Enter` | 应用选中的暂存但不删除 |
| 弹出暂存 | `空格` | 应用并删除该暂存 |
| 删除暂存 | `d` | 丢弃该暂存 |
| 查看内容 | `Enter` | 在右侧查看暂存内容 |

### 6.4 远程操作

按 `4` 进入 Branch 面板：

| 操作 | 按键 | 说明 |
| ---- | ---- | ---- |
| 推送 | `P` | 推送到远程 |
| 拉取 | `p` | git pull |
| 抓取 | `f` | git fetch ——只获取不合并 |
| 设置上游 | `u` | 设置 upstream 分支 |

> [!tip] 第一次推送新分支时，lazygit 会自动提示设置上游。

---

## 七、常用快捷键速查

### 全局操作

| 快捷键 | 作用 |
| ------ | ---- |
| `1`-`5` | 切换面板 |
| `↑/↓` | 选中上/下一个条目 |
| `PgUp/PgDn` | 滚动面板内容 |
| `/` | 搜索 |
| `:` | 输入自定义命令 |
| `q` | 退出 |
| `?` | 查看所有快捷键 |

### Files 面板

| 快捷键 | 作用 |
| ------ | ---- |
| `空格` | 暂存/取消暂存 |
| `Enter` | 查看 diff |
| `c` | 提交 |
| `a` | 追加到上次提交（amend） |
| `d` | 丢弃修改 |
| `s` | 暂存到 stash |

### Commits 面板

| 快捷键 | 作用 |
| ------ | ---- |
| `Enter` | 查看 commit 内容 |
| `e` | 交互式变基 |
| `s` | squash 到上一 commit |
| `r` | 修改提交信息 |
| `d` | 删除 commit |
| `C` | cherry-pick |
| `g` | 重置到该 commit |
| `t` | 打标签 |

### Branch 面板

| 快捷键 | 作用 |
| ------ | ---- |
| `Enter` | 切换分支 |
| `n` | 创建新分支 |
| `d` | 删除分支 |
| `M` | 合并分支到当前 |
| `r` | 变基到选中分支 |
| `P` | 推送 |
| `p` | 拉取 |
| `f` | 抓取 |

---

## 八、配置与定制

### 8.1 配置文件位置

**Linux:** `~/.config/lazygit/config.yml`

**macOS:** `~/Library/Application Support/lazygit/config.yml`

**Windows:** `%APPDATA%\lazygit\config.yml`

首次启动 lazygit 后会自动生成。

### 8.2 常用配置

```yaml
# ~/.config/lazygit/config.yml

gui:
  # 主题
  theme:
    lightTheme: false
    activeBorderColor:
      - green
      - bold
    inactiveBorderColor:
      - white
    searchingActiveBorderColor:
      - yellow
      - bold
    optionsTextColor: yellow
    selectedLineBgColor:
      - blue
      - bold

  # 显示行号
  showFileTree: true
  # 在 diff 中显示行号
  showNumstatInDiffView: false

git:
  paging:
    # 使用 delta 作为 diff 呈现工具
    colorArg: always
    pager: delta --dark --paging=never

  # 默认推送行为
  push:
    autoPush: false

update:
  # 自动检查更新
  method: never

os:
  # 自定义编辑器
  editPreset: nvim
  # 或直接指定命令
  # editCommand: "code"
  # editCommandTemplate: '{{editor}} "{{filename}}"'
```

### 8.3 实用配置项说明

| 配置项 | 作用 | 推荐值 |
| ------ | ---- | ------ |
| `gui.showFileTree` | 文件面板以目录树显示 | `true` |
| `git.paging.pager` | diff 的呈现方式 | `delta` 或 `diff-so-fancy` |
| `os.editPreset` | 编辑提交信息的默认编辑器 | `nvim` / `vim` / `code` |
| `update.method` | 是否自动检查更新 | `never`（手动更新） |

---

## 九、日常流程示例

### 9.1 日常提交流程

```text
1. 在终端输入 lazygit

2. Files 面板（按 2）
   → 上下键浏览改动的文件
   → 空格暂存需要的文件
   → Enter 看具体 diff，确认无误

3. 按 c 提交
   → 输入提交信息
   → Enter 确认

4. 按 P 推送到远程
```

### 9.2 修改上次提交

```text
1. 暂存新改动
2. 按 a（amend）
   → 输入新的提交信息（留空保持原信息）
   → Enter 确认
3. 如果已推送过，需要 force push → 确认
```

### 9.3 合并多个 commit（squash）

```text
1. Commits 面板（按 3）

2. 选中最早需要改的那个 commit
   例如要把最近的 3 个 commit 合并：

   commit C  (最新的)
   commit B
   commit A  ← 选中这个

3. 按 e 进入交互式变基

4. 对 commit C 按 s（squash 到上一个）
   对 commit B 按 s（squash 到上一个）
   commit A 保留 pick

5. 确认 → 编辑合并后的提交信息 → 完成
```

### 9.4 解决冲突

```text
场景：合并分支时提示有冲突

1. Files 面板 → 看到黄色标记的冲突文件

2. Enter 查看 diff
   → 看 base / local / remote 三栏
   → 按空格切换版本

3. 手动编辑文件后保存

4. 再空格一次标记为已解决

5. 所有冲突解决后 → 按 c 提交
```

---

## 十、适用场景与注意事项

### Lazygit 适合

- 日常开发中的暂存、提交、推送循环
- 需要频繁看 diff 来确认改了什么
- 交互式变基（squash / reword / drop）
- 多人协作时查看分支拓扑和 commit 关系
- 刚学 Git 的人降低上手门槛
- 排查问题时快速浏览历史

### Lazygit 不太适合

- CI/CD 脚本、自动化流程（用原生命令）
- 大规模仓库中的性能敏感操作
- 非常复杂的冲突合并（仍建议用专门的 merge 工具）
- Git 子模块管理（支持有限）

### 常见问题

| 问题 | 解决方法 |
| ---- | -------- |
| 启动后没有内容 | 确认当前目录是 Git 仓库 |
| 提交信息编辑器不符合预期 | 配置 `os.editPreset` 或设置 `GIT_EDITOR` 环境变量 |
| 中文乱码 | 终端编码设为 UTF-8，确保 locales 已生成 |
| Diff 没有高亮 | 配置 `git.paging.pager: delta` |
| 无权限推送到远程 | 检查 SSH key / credential helper |

---

## 十一、总结

Lazygit 解决的核心矛盾是：**Git 功能强大但操作繁琐，而可视化工具通常需要离开终端。** 它让你在不切换窗口的情况下获得图形化的反馈，降低日常 Git 操作的心智负担。

它不是替代 `git` 命令——当你需要写脚本、做复杂的远程管理、或处理非常特殊的场景时，命令行仍然是唯一的选择。但对于日常的分支操作、暂存提交、历史管理和变基合并，lazygit 提供了一条效率明显更高的路径。

## 相关笔记

- [[Ghostty 终端配置指南]]
