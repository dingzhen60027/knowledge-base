---
tags: [工具, 终端, 文件管理]
date: 2026-05-15
---

# Yazi 终端文件管理器安装指南

Yazi 是一个用 Rust 编写的现代化终端文件管理器，支持异步 I/O、图片/视频预览、代码高亮、Vim 键位、Lua 插件系统。

## 安装

### 方法一：官方二进制（推荐，版本最及时）

```bash
curl -LO https://github.com/sxyazi/yazi/releases/latest/download/yazi-x86_64-unknown-linux-musl.zip
unzip yazi-x86_64-unknown-linux-musl.zip
cd yazi-x86_64-unknown-linux-musl
sudo mv yazi ya /usr/local/bin/
```

无 sudo 权限时：

```bash
mkdir -p ~/.local/bin
cp yazi ya ~/.local/bin/
```

确保 `~/.local/bin` 在 PATH 中。

### 方法二：Snap（最简单）

```bash
sudo snap install yazi --classic
```

### 方法三：Cargo

```bash
cargo install --locked yazi-fm yazi-cli
```

## Shell 集成（退出时自动 cd）

在 `~/.bashrc` 中添加：

```bash
function y() {
    local tmp="$(mktemp -t "yazi-cwd.XXXXXX")"
    yazi "$@" --cwd-file="$tmp"
    if cwd="$(cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
        cd -- "$cwd"
    fi
    rm -f -- "$tmp"
}
```

`source ~/.bashrc` 后，用 `y` 命令启动，退出时终端自动 cd 到浏览目录。

## 可选依赖

```bash
sudo apt install -y ffmpeg 7zip jq poppler-utils fd-find ripgrep fzf zoxide imagemagick
```

| 依赖 | 功能 |
|------|------|
| `ffmpeg` | 视频缩略图 |
| `7zip` | 压缩包预览与解压 |
| `jq` | JSON 高亮 |
| `poppler-utils` | PDF 预览 |
| `fd-find` | 文件名搜索 |
| `ripgrep` | 文件内容全文搜索 |
| `fzf` | 模糊搜索/快速导航 |
| `zoxide` | 智能目录跳转 |
| `imagemagick` | 通用图片处理 |

## 常用操作

| 按键 | 功能 |
|------|------|
| `j/k` | 上下移动 |
| `h/l` | 进入/退出目录 |
| `space` | 选中/取消 |
| `v` | 进入选择模式 |
| `y/p` | 复制/粘贴 |
| `d` | 剪切 |
| `r` | 重命名 |
| `/` | 搜索 |
| `q` | 退出 |

- 官方仓库：[sxyazi/yazi](https://github.com/sxyazi/yazi)
