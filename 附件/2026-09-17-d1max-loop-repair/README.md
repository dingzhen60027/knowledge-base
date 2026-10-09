# 2026-09-17 技术日记：图表和证据

正文：[D1 Max 建图技术日记](../../日历/2026-09-17.md)。本目录是静态技术文档附件，不是 ROS 节点或新的 Web 应用。

## 四张图的来源

| 图片 | 数据 | 处理和限制 |
|---|---|---|
| `01-height-profile.png` | `raw_poses.txt`、`optimized_poses.txt`、`times.txt` | 同批 647 帧，相对首帧高度；保留全部样本，不平滑、不强制水平 |
| `02-loop-clouds.png` | `closure_clouds.npz` | 起点前 9 帧与最后一帧；原始扫描半径 10 m、0.10 m 体素；世界坐标固定空间裁剪、Y–Z 投影，非完整地图 |
| `03-floor-tilt.png` | `geometry_validation_final.json` | 10 个局部平面抽样；不是测量真值，也不是全部地面 |
| `04-synthetic-height.png` | `synthetic_*` | 单独标明的合成试验；真值高度公式为 `1.2 * sin(pi * i / 96)`，不混入实机结果 |

图 2 的 `before`、`after` 使用同一份最后一帧 body 点云，分别应用保存的前端与后端位姿；目标子图始终使用原始早期位姿。绘图程序没有重新估计配准或修正点云。

## 直接重画

依赖 Python 3、NumPy、Matplotlib。推荐安装 Noto Sans CJK 字体以正确显示中文。

```bash
cd /home/dndx/knowledge-base
OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=1 /usr/bin/python3 \
  附件/2026-09-17-d1max-loop-repair/render_figures.py
```

默认仅使用随附的证据快照，不需要 ROS、机器人、原始 bag 或完整 PCD。它会重新计算并核对首尾位置误差，检查位姿数量、时间单调性、有限值、回环条数及关键闭环索引，然后生成四张 PNG。

`--collect` 才从脚本中明确记录的本机源路径刷新附件，另外需要 Open3D 和 PyYAML。该选项读取前 9 个及最后 1 个扫描，**不读取完整 bag、不启动算法、不连接机器人**；其他电脑只有附件时不要使用它。

## 证据文件说明

- `source_manifest.json`：复制来源及 SHA256；列出图 2 的扫描来源与哈希。
- `baseline_result.json`：18:28 的双雷达 Zenoh 基线，接受回环为 0。
- `replay_result.json`：19:01 完整前端回放阶段，只接受 2 条小回环。
- `repair_result.json`：最终后端修复结果、地图位置和未验证范围。
- `geometry_validation_initial.json`：早期单帧可见性不足的未通过记录。
- `geometry_validation_final.json`：小子图独立配准结果及地面法向抽样。
- `loop_events.csv`：最终后端的原始事件记录；`ros_time` 为处理端事件时钟，不要当成传感器轨迹横轴。
- `times.txt`：关键帧的原始传感器时间；绘图减去首个时间，不以时间戳转换出的日历日期命名实验。
- `raw_poses.txt`、`optimized_poses.txt`：每行 3×4 位姿矩阵，按行展开、无额外时间列。
- `pgo_effective_config.yaml`：这次加速关键帧重算的参数，不是线上默认运行频率。
- `faster_lio_config.yaml`：前端基础 YAML 快照；部分外参会被启动文件覆盖，不能单独认定为所有生效参数。
- `synthetic_result.json` 和 `synthetic_*_poses.txt`：含地面场景回归证据，必须与实机数据分开解释。
- `bag_summary.json`：从原始包元数据提取的话题、消息数和时长，不包含录制任务 token 或设备序列号。

图片中的“闭合误差”是相对于首尾点云配准测量的内部一致性指标，**没有外部测量真值**。配准使用不同实现仍共享原始点云，不能描述为完全独立的绝对定位精度验证。

## 本次文档检查范围

绘图时重新核对了 647 帧、6 条接受约束、`0 ↔ 642` 及位置闭合误差；四张 PNG 已逐张检查，图中保留未改善样本和合成测试的曲线偏差。文档相对链接另做本地存在性检查。

技术日记不自动提交或推送 Git，不改变原机器人项目。没有把原始 bag、完整地图、设备序列号或登录凭据带入仓库；局部 XYZ 几何是图 2 的复现数据。
