# PCD → PCT 全局规划：图像与证据归档

记录日期：2026-09-23。对应 [[项目/D1 Max 从原始 PCD 到 PCT 全局规划的完整处理流程]]。

七张 PNG 均是已有实验图片的逐字节副本，没有在文档整理时裁剪、重画或修改颜色；配置与数值结果也按原文件复制。本目录不包含大型 PCD、rosbag、tomogram 或原生依赖库。原六张图片和 20 个证据文件未覆盖，本轮追加路径优化资料。

| 图片 | 含义与版本 |
|---|---|
| `01-source-map-comparison.png` | 09-19 前端与 SC-PGO 对比；右侧优化图是本轮处理输入。 |
| `02-early-cost-stages.png` | 09-22 早期 official 版本，原图、保留层 2、安全边距 0.40 m；不是 v6。 |
| `03-observed-floor-height.png` | 优化轨迹附近实测地面高度及单一平面拟合。 |
| `04-compact-vs-v3.png` | compact → v3，局部改善但长走廊尚未全部连通。 |
| `05-v3-breaks-diagnosis.png` | v3 的四处断带：代价与真实点云侧剖面。 |
| `06-compact-vs-v6.png` | compact → 最终 v6；不是 v3 → v6。 |
| `07-path-quality-before-after.png` | 同一 v6 地图、相同起终点的路径优化前后；直走廊与真实转角。是实际路径数据绘图，不是 RViz 截图。 |

`evidence/` 保存 30 个配置、manifest、验收结果、路径及轨迹文件。编号 01～20 为上一阶段；21～30 为本轮路径质量对比、14 用例约定与摘要、配置快照、关键路径和 RViz 发布验证。JSON 内的绝对路径保留为实验现场来源，不改写成附件地址，以免破坏原始证据。正文链接使用知识库内副本，原始 PCD/代码仍需从项目目录访问。

[source-manifest.json](source-manifest.json) 记录每个副本的原始路径、字节数和 SHA-256，以及未复制的大文件哈希。所有图像与证据可以随知识库一起移动；本归档不是完整可独立运行的软件发布包。

可用 [verify_archive.py](verify_archive.py) 做只读校验：运行 `python3 verify_archive.py` 检查附件哈希、图像尺寸、文内相对链接、点数分区与路径验收摘要；在原计算机上加 `--check-originals`，还会对照工程原件及大型 PCD/tomogram 的哈希。该脚本不会启动机器人、ROS 或规划任务。

配置快照反映当时版本，不等于当前工程配置。例如证据 16 是旧 2/8 配置，证据 24 是本轮 1/8＋路径整理配置。若原路径后来已合法更新，`--check-originals` 会报告差异；不应为了消除差异而覆盖历史快照。默认校验检查知识库归档自身的完整性。
