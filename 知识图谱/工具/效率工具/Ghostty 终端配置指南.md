---
title: Ghostty 终端配置指南
aliases:
  - Ghostty
  - ghostty
tags:
  - terminal
  - linux
  - tool
created: 2026-05-07
---

# Ghostty 终端配置指南

> GPU 加速、原生体验、功能丰富的跨平台终端模拟器。

## 安装

```bash
# Ubuntu / Debian
sudo dpkg -i ghostty-*.deb
```

## 配置文件

路径：`~/.config/ghostty/config`，修改后即时生效无需重启。

## 当前配置

```ini
# 字体
font-family = Ubuntu Mono
font-size = 13

# 主题 (Catppuccin Mocha)
background = #1e1e2e
foreground = #cdd6f4

# 窗口
background-opacity = 0.93
window-padding-x = 8
window-padding-y = 4
window-theme = dark
window-inherit-working-directory = true

# 光标
cursor-style = bar
cursor-style-blink = true

# 回滚
scrollback-limit = 50000

# 分屏 (vim 风格)
keybind = ctrl+alt+h=goto_split:left
keybind = ctrl+alt+j=goto_split:bottom
keybind = ctrl+alt+k=goto_split:top
keybind = ctrl+alt+l=goto_split:right
keybind = ctrl+shift+h=new_split:left
keybind = ctrl+shift+v=new_split:right
keybind = ctrl+shift+s=new_split:down

# 标签页
keybind = ctrl+t=new_tab
keybind = ctrl+w=close_surface
keybind = alt+1..8=goto_tab:1..8
keybind = alt+9=last_tab

# 字体缩放
keybind = ctrl+=increase_font_size:1
keybind = ctrl+-=decrease_font_size:1
keybind = ctrl+0=reset_font_size

# 复制粘贴
copy-on-select = true
clipboard-paste-protection = true

# Shell 集成
shell-integration = detect
shell-integration-features = cursor,no-sudo,title

# 桌面通知
desktop-notifications = true

# 确认关闭
confirm-close-surface = true
```

## 快捷键速查

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+T` | 新建标签页 |
| `Ctrl+W` | 关闭当前标签页/分屏 |
| `Alt+1~8` | 跳到第 N 个标签页 |
| `Alt+9` | 跳到最后一个标签页 |
| `Ctrl+Alt+H/J/K/L` | 分屏间移动 (vim 风格) |
| `Ctrl+Shift+H` | 左侧新建分屏 |
| `Ctrl+Shift+V` | 右侧新建分屏 |
| `Ctrl+Shift+S` | 下方新建分屏 |
| `Ctrl+=` / `Ctrl+-` | 放大/缩小字体 |
| `Ctrl+0` | 恢复默认字号 |

## 相比 GNOME Terminal 的优化

- **GPU 渲染** — OpenGL 加速，大输出量不卡顿
- **多线程架构** — 独立读写/渲染线程
- **内置分屏** — 无需 tmux
- **字体内连字** — Fira Code 等连字字体自动渲染
- **emoji 支持** — 肤色、国旗等复杂 emoji 正确显示
- **Kitty 图形协议** — 终端内显示图片
- **数百内置主题** — 一行配置切换
- **Shell 集成** — 光标定位 + sudo 安全提示 + 标题同步
- **配置热重载** — 改配置文件即时生效
- **单实例模式** — 新窗口复用进程

## 实用技巧

### 命令完成通知

```bash
# 加到 ~/.bashrc
alias alert='echo -e "\a"'

# 使用
sudo apt update && sudo apt upgrade -y && alert
```

### 查看完整默认配置

```bash
ghostty +show-config --default
```

### 升级字体

```bash
sudo apt install fonts-jetbrains-mono fonts-firacode
```

## 相关链接

- [Ghostty 官方文档](https://ghostty.org/docs)
- [GitHub 仓库](https://github.com/ghostty-org/ghostty)
