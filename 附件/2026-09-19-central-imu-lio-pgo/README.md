# 2026-09-19 中心 IMU＋Faster-LIO＋SC-PGO 对比证据

正文：[D1 Max 中心 IMU 与回环建图对比报告](../../项目/D1%20Max%20中心%20IMU%20与回环建图对比报告.md)。

本目录是静态 Obsidian 文档附件，不是 ROS 节点或新 Web 应用。图片与证据复制自同一已完成运行；原始文件不改写，复制来源、大小与 SHA256 见 `source_manifest.json`。

## 图表

- `01-loop-comparison.png`：原始地图与优化地图的共同尺度俯视、侧视及关键帧高度对比。
- `02-frontend-diagnostics.png`：原始前端地图、轨迹及重力／匹配诊断。

图片是原分析产物的原样副本，不重新着色、裁剪或校平。地图点数与有限值检查使用全量点；显示使用确定性的步进采样。第一张图高度色带在显示点的 1%／99% 分位截断，坐标不变。精确方法记录在两个分析 JSON 中。

## 证据

| 文件 | 用途 |
|---|---|
| `evidence/run_report.md` | 原运行报告原样快照；涉及进程/PID 的描述是当时状态，不是阅读时状态 |
| `evidence/result.json`、`manifest.json` | 完成状态、覆盖、退出码、输入与版本摘要 |
| `evidence/central_imu_adapter.json`、`central_adapter.log` | 192,971 条实收／转发审计，以及审计写出后的重复 shutdown 异常 |
| `evidence/pgo_drain.json` | 结束前输出稳定性检查；不是内部队列已排空的证明 |
| `evidence/loop_result.json`、`frontend_result.json` | 图表数值、方法、限制与地图文件检查 |
| `evidence/loop_events.csv` | 仅 `accepted` 计入 4 条接纳约束；候选和几何中间事件不计入 |
| `evidence/odom_poses.txt`、`optimized_poses.txt` | 同一批 644 个关键帧的原始／优化 KITTI 位姿，每行 3×4 矩阵、无时间列 |
| `evidence/times.txt` | 与两份位姿按行对应的关键帧传感器时间；不是事件日志中的处理端 `ros_time` |
| `evidence/frontend_effective.yaml`、`pgo_effective.yaml` | 本次生效配置快照 |
| `evidence/calibration.yaml` | 实验旋转、名义平移及 −13 ms 偏移假设，不是完整出厂标定 |

注意：原样保存的 `calibration.yaml` 及 adapter 审计中的 provenance，包含上一轮标定／前端实验遗留的 `No ... loop closure used` 文字。它不描述本次整体运行；本次以 `result.json` 的 `loop_closure_enabled=true`、4 条 `accepted` 及后端配置为准。没有为消除这处历史文字而改写源证据。

原始报告中 `analysis/loop_result.png` 的链接属于运行目录布局；知识库正文已经改为本目录的便携相对链接。JSON 中的绝对源路径同样用于溯源，不保证在另一台电脑存在。

## 可以独立核对什么

只用本目录的位姿、时间和事件文件，可以重算关键帧数量、4 条接纳事件、首尾 XYZ 差、XY/XYZ 距离及轨迹高度跨度。KITTI 平移列为第 4、8、12 列，不能把第一列当时间。

两张图依赖完整地图，原始前端跨运行一致性检查依赖两轮完整 `frontend_state.csv`。这些大文件没有复制到知识库，因此附件不声称可以脱离原始数据重跑全部分析。全量 PCD、bag 保持在原工作空间；本次写入知识库不重启机器人、回放或建图，也不自动提交、推送 Git。
