---
tags: [工具, 终端, shell, 美化]
date: 2026-05-17
---

# Starship 终端提示符配置

Starship 是一个用 Rust 编写的跨 Shell 极简提示符工具，速度快、配置简单，支持 bash/zsh/fish/powershell/ion 等所有主流 Shell。

## 当前环境

- **版本**: 1.25.1 (2026-04-30 编译)
- **安装路径**: `/usr/local/bin/starship`
- **配置文件**: `~/.config/starship.toml`
- **主题**: Gruvbox Dark 自定义调色板

## Shell 集成

在 `~/.bashrc` 第 159 行：

```bash
eval "$(starship init bash)"
```

切换 Shell 时对应的 init 命令：

```bash
# zsh
eval "$(starship init zsh)"

# fish
starship init fish | source

# powershell
Invoke-Expression (&starship init powershell)
```

## 配置概览

当前配置采用**多段 Powerline 风格**，从左到右依次展示：

| 段 | 背景色 | 显示内容 |
|----|--------|----------|
| 第1段 (Orange) | `#d65d0e` | OS 图标 + 用户名 |
| 第2段 (Yellow) | `#d79921` | 当前目录 |
| 第3段 (Aqua) | `#689d6a` | Git 分支 + 暂存状态 |
| 第4段 (Blue) | `#458588` | 编程语言版本 (13种) |
| 第5段 (Bg3) | `#665c54` | Docker / Conda / Pixi |
| 第6段 (Bg1) | `#3c3836` | 当前时间 |
| 换行 | - | 提示符（第二行输入） |

### Gruvbox Dark 调色板

```toml
[palettes.gruvbox_dark]
color_fg0    = '#fbf1c7'  # 前景文字
color_bg1    = '#3c3836'  # 深色背景1
color_bg3    = '#665c54'  # 深色背景3
color_blue   = '#458588'  # 蓝色（语言段）
color_aqua   = '#689d6a'  # 青色（Git段）
color_green  = '#98971a'  # 绿色（提示符）
color_orange = '#d65d0e'  # 橙色（用户/OS段）
color_purple = '#b16286'  # 紫色（Vim visual）
color_red    = '#cc241d'  # 红色（错误提示符）
color_yellow = '#d79921'  # 黄色（目录段）
```

## 各模块配置要点

### OS 图标

40+ 发行版图标映射，常用：

| 发行版 | 图标 |
|--------|------|
| Arch | `󰣇` |
| Ubuntu | `󰕈` |
| Debian | `󰣚` |
| Fedora | `󰣛` |
| MacOS | `󰀵` |
| Windows | `󰍲` |

### 目录替换

常用目录的图标别名：

```toml
"Documents" = "󰈙 "
"Downloads" = " "
"Music"     = "󰝚 "
"Pictures"  = " "
"Developer" = "󰲋 "
```

### 编程语言模块

配置了 13 种语言的版本检测：

C, C++, Rust, Go, Node.js, Bun, PHP, Java, Kotlin, Haskell, Python, Docker, Conda, Pixi

所有语言模块的格式模式一致：
```toml
[<lang>]
symbol = "<icon>"
style = "bg:color_blue"
format = '[[ $symbol( $version) ](fg:color_fg0 bg:color_blue)]($style)'
```

### Git 分支与状态

- 分支图标: ``
- 同步状态（ahead/behind）和暂存区变更计数

### 提示符

- 成功: 绿色 ``
- 失败: 红色 ``
- Vim 普通模式: 绿色 ``
- Vim 替换模式: 紫色 ``
- Vim 可视模式: 黄色 ``

## 常用自定义

### 切换预设主题

Starship 内置多套预设，放在 `~/.config/starship.toml` 即可：

```toml
# Nerd Font 预设（需要 Nerd Font）
# 官方预设文件: https://starship.rs/presets/
```

### 禁用不需要的模块

```toml
[ruby]
disabled = true

[swift]
disabled = true
```

### 调整目录截断

```toml
[directory]
truncation_length = 5        # 默认3段
truncation_symbol = "…/"     # 截断标记
```

### 调试命令

编辑完成后实时预览效果（不需要 `source`）：

```bash
starship prompt    # 单次预览
starship timings   # 查看各模块耗时
starship explain   # 解释当前提示符各段
```

## 维护命令

```bash
# 升级
sh -c "$(curl -fsSL https://starship.rs/install.sh)" -f

# 查看版本
starship --version

# 打印完整配置（含默认值）
starship print-config
```

- 官网: [starship.rs](https://starship.rs)
- 配置参考: [starship.rs/config](https://starship.rs/config)
- 预设主题: [starship.rs/presets](https://starship.rs/presets)
