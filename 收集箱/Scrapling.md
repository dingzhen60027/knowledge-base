---
title: Scrapling 网页抓取库
tags:
  - inbox
  - tool/web-scraping
  - tool/mcp
created: 2026-06-16
---

# Scrapling：一个自带反爬和 MCP 的 Python 抓取库

## 它是什么

Scrapling 是一个 Python 的**自适应网页抓取框架**（GitHub 64k+ stars），一个库搞定请求、解析、JS渲染和反爬绕过。

> 项目地址：https://github.com/d4vinci/Scrapling
> 安装：`pip install "scrapling[ai]"`

## 为什么需要它

传统的 Python 爬虫路线太碎了：

1. `requests` 发请求 → 遇到 JS 渲染页面就废
2. 换 `Playwright/Selenium` → 配置一堆，还容易被网站检测爬虫
3. `BeautifulSoup` 解析 → 写一堆 `.find().find_all()`
4. 遇到 Cloudflare 反爬 → 再去找 `cloudscraper`、`undetected-chromedriver`
5. 想爬整个站 → 再上 `Scrapy`，又是一套新的学习成本

**Scrapling 的核心价值就是把这些拼在一起了**：一个库 = 请求 + 解析 + JS渲染 + 反爬绕过 + 全站爬取。

## 为什么把它配成 MCP

Claude Code 自带的 WebFetch 工具很弱：

| 场景 | WebFetch | Scrapling MCP |
|------|----------|---------------|
| 普通网页 | 能用 | 能用 |
| GitHub/raw 内容 | 被限制 | 能爬 |
| JS 渲染页面 | 拿不到内容 | Playwright 渲染 |
| Cloudflare 反爬 | 被拦截 | stealth 绕过 |
| 需要登录态 | 不行 | 可以带 session |
| 批量多页面 | 一个个手动 | bulk_get 一次搞定 |

**简单说就是**：配了 Scrapling MCP 后，Claude 能自己去爬网页了，不需要你先复制粘贴再喂给我。遇到有反爬的网站也能绕过，还能批量操作。

## MCP 提供的 10 个工具（3 层架构）

Scrapling 的工具分为三层，从轻到重：

```
get / bulk_get         → 轻量 HTTP，最快最省
  ↓ 遇到 JS/动态内容
fetch / bulk_fetch     → 开 Chromium 渲染
  ↓ 遇到 Cloudflare/反爬
stealthy_fetch / bulk_stealthy_fetch → 隐身模式硬刚
```

每层都有单次和批量两种模式。各层详解：

---

### 第一层：基础 HTTP 请求（get / bulk_get）

**工作原理**：模拟浏览器发 HTTP 请求（非真实浏览器），自带 TLS 指纹伪装、HTTP/3 支持。速度最快、资源最少。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `impersonate` | 伪装成哪个浏览器：`chrome`、`firefox`、`safari`、`edge` 或具体版本号如 `chrome124` | `chrome` |
| `timeout` | 超时秒数 | `30` |
| `follow_redirects` | 是否跟随重定向 | `true` |
| `verify` | 是否验证 SSL 证书 | `true` |
| `headers` | 自定义请求头，格式 `"Key: Value"` | 自动生成伪装头 |
| `cookies` | Cookie 字符串，格式 `"name1=value1; name2=value2"` | - |
| `proxy` | 代理 `"http://user:pass@host:port"` | - |
| `css_selector` | 只提取匹配 CSS 选择器的元素 | 返回整页 |
| `extraction_type` | 返回格式：`markdown`、`html`、`text` | `markdown` |
| `main_content_only` | 只提取主体内容，过滤导航/广告/隐藏元素（也过滤 prompt 注入） | `true` |

**使用场景**：
- 适用：普通网页
- 适用：API 返回数据
- 适用：不需要 JS 渲染的静态页面
- 不适用：页面内容是 JS 动态加载的
- 不适用：有 Cloudflare/反爬保护的网站

**实测表现**：GitHub Trending 页面 — 成功拿到热门仓库列表。

---

### 第二层：浏览器渲染（fetch / bulk_fetch）

**工作原理**：启动真实 Chromium 浏览器（Playwright），页面完全加载 JS 后再提取内容。可以拿到 SPA 应用的全部内容。

比 `get` 多了以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `headless` | 是否无头模式 | `true` |
| `wait` | 加载后额外等待（毫秒） | `0` |
| `wait_selector` | 等待某个 CSS 选择器出现后再提取 | - |
| `network_idle` | 是否等到网络空闲 | `false` |
| `disable_resources` | 是否禁用图片/字体等加速加载 | `false` |
| `locale` | 浏览器语言，如 `zh-CN` | 系统默认 |
| `block_ads` | 是否拦截广告和 tracker | `false` |
| `extra_headers` | 额外请求头 | - |

**使用场景**：
- 适用：SPA / 单页应用（React、Vue 等）
- 适用：内容通过 JS 异步加载的网站
- 适用：需要等待特定元素出现才操作
- 适用：普通 `get` 拿到空内容或不完整时
- 不适用：有 Cloudflare 强防护的网站

**实测表现**：豆瓣小组 — 成功渲染 JS 动态内容，拿到完整的讨论精选和小组日榜。小红书 — 虽然页面渲染成功（返回 200），但热榜内容需要登录，不是工具的问题。

---

### 第三层：Stealth 隐身模式（stealthy_fetch / bulk_stealthy_fetch）

**工作原理**：使用经过深度改造的浏览器，修改了浏览器指纹、WebDriver 特征、navigator 属性等，看起来和真人浏览器一模一样 — 专门对付 Cloudflare Turnstile、Interstitial 等反爬系统。

`stealthy_fetch` 除了 `fetch` 的全部参数外，还有：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `solve_cloudflare` | 是否尝试自动解决 Cloudflare 验证 | `false` |
| `hide_canvas` | 是否隐藏 Canvas 指纹 | `false` |
| `block_webrtc` | 是否阻止 WebRTC 泄露真实 IP | `false` |
| `allow_webgl` | 是否允许 WebGL（某些 WAF 会检测） | `true` |

**使用场景**：
- 适用：Cloudflare 保护的网站
- 适用：有 WAF/反爬系统的网站
- 适用：`fetch` 被拦截时
- 适用：需要抓取的是对抗性较强的网站

**实测表现**：百度搜索 — 成功绕过了反爬，拿到完整的热搜列表。

---

### 截图工具（screenshot）

**工作原理**：通过已打开的浏览器会话对页面截图，Claude 能直接"看到"页面长什么样（返回的是图片内容块，不是 base64 字符串）。

**注意**：必须先 `open_session` 创建会话，再传 `session_id`。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `session_id` | 已打开的浏览器会话 ID | 必填 |
| `image_type` | 图片格式 `png` / `jpeg` | `png` |
| `full_page` | 是否截取整个页面（包括滚动部分） | `false` |
| `quality` | JPEG 质量（0-100），仅 JPEG 可用 | - |
| `wait` | 加载后等待（毫秒） | `0` |
| `wait_selector` | 等待某元素出现再截 | - |
| `network_idle` | 等到网络空闲再截 | `false` |

**使用场景**：
- 适用：页面视觉布局检查
- 适用：需要看图片/图表/UI 的内容
- 适用：抓取内容格式复杂，截图更清晰

---

### 会话管理（open_session / close_session / list_sessions）

**为什么要会话管理**：每次 `fetch` 都要重新启动一个完整的 Chromium 浏览器，非常慢（几百毫秒到几秒）。如果爬同一个网站的多个页面，**用会话复用浏览器**，速度快很多。

| 工具 | 说明 |
|------|------|
| `open_session` | 创建持久浏览器会话。支持 `dynamic`（标准）和 `stealthy`（隐身）两种类型 |
| `close_session` | 关闭会话，释放资源 |
| `list_sessions` | 列出所有活跃中的会话 |

**open_session 参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `session_type` | `dynamic`（标准）或 `stealthy`（隐身） | 必填 |
| `session_id` | 自定义名称，便于管理 | 随机生成 |
| `headless` | 是否无头 | `true` |
| `solve_cloudflare` | 是否解决 Cloudflare（stealthy 类型用） | `false` |
| `locale` | 浏览器语言 | 系统默认 |
| `proxy` | 代理设置 | - |
| `max_pages` | 最大同时打开页面数 | `5` |

**使用场景**：
- 适用：爬取同一个网站的多个页面
- 适用：需要保持登录态的长时间抓取
- 适用：登录 → 抓取 → 关闭 的完整工作流
- 适用：多个抓取任务共用浏览器，避免反复启动

**必记**：用完一定要 `close_session`，不然浏览器进程一直挂着。


## 什么场景用到它

- 让 Claude 去爬竞品信息做对比分析
- 抓 JS 渲染的页面（SPA、电商等）
- 被 Cloudflare 等反爬保护的网站
- 需要登录态保持的批量抓取
- AI Agent 自主联网查资料

## 安装方式

```bash
pip install "scrapling[ai]"
scrapling install              # 安装 Playwright 浏览器
claude mcp add Scrapling $(which scrapling) mcp   # 注册 MCP
```

## 其他亮点

- **CSS 选择器**：爬取时直接指定元素，省 token
- **Prompt 注入防护**：自动剔除隐藏的 CSS/aria-hidden 元素和零宽字符
- **Docker 可用**：`ghcr.io/d4vinci/scrapling:latest`
- **Streamable HTTP 模式**：`scrapling mcp --http` 可选

## 注意事项

- 注意遵守 robots.txt 和网站的 ToS
- 注意频率控制，别把人家服务器搞炸了
- 持久会话用完记得关，不然进程一直挂着
